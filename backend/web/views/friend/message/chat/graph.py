import os
from pprint import pprint
from time import localtime
from typing import TypedDict, Annotated, Sequence

import lancedb
from django.utils.timezone import now, localtime
from langchain_community.vectorstores import LanceDB
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph
from langgraph.prebuilt import ToolNode

from web.documents.utils.custom_embeddings import CustomEmbeddings


class ChatGraph:
    @staticmethod
    def create_app():
        @tool
        def get_time() -> str:
            """当需要查询精确时间时，调用此函数。返回格式为：[年-月-日 时:分:秒]"""
            return localtime(now()).strftime('%Y-%m-%d %H:%M:%S')

        @tool
        def search_knowledge_base(query: str) -> str:
            """当用户查询阿里云百炼平台的相关信息时，调用此函数。输入为要查询的问题，输出为查询结果。"""
            db = lancedb.connect('./web/documents/lancedb_storage')
            embeddings = CustomEmbeddings()
            vector_db = LanceDB(
                connection=db,
                embedding=embeddings,
                table_name='my_knowledge_base',
            )
            docs = vector_db.similarity_search(query, k=3) #在向量数据库里查询3个相近的文档
            context = '\n\n'.join([f'内容片段：{i + 1}\n{doc.page_content}' for i, doc in enumerate(docs)]) #把上面3个文档拼接一下
            return f'从知识库中找到以下相关信息：\n\n{context}\n'

        import requests  # 文件顶部 import

        @tool
        def get_weather(city: str) -> str:
            """当用户询问某地天气、气温、是否下雨时，调用此函数。
            输入为城市名（中文或英文，如：北京、Shanghai），输出为简要天气描述。
            """
            # 1) 城市名 → 经纬度
            geo = requests.get(
                'https://geocoding-api.open-meteo.com/v1/search',
                params={'name': city, 'count': 1, 'language': 'zh'},
                timeout=10,
            ).json()
            if not geo.get('results'):
                return f'未找到城市：{city}'

            place = geo['results'][0]
            lat, lon = place['latitude'], place['longitude']
            name = place.get('name', city)

            # 2) 查当前天气
            weather = requests.get(
                'https://api.open-meteo.com/v1/forecast',
                params={
                    'latitude': lat,
                    'longitude': lon,
                    'current': 'temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m',
                    'timezone': 'Asia/Shanghai',
                },
                timeout=10,
            ).json()
            cur = weather.get('current', {})
            return (
                f'{name}当前天气：'
                f'气温 {cur.get("temperature_2m")}°C，'
                f'湿度 {cur.get("relative_humidity_2m")}%，'
                f'风速 {cur.get("wind_speed_10m")} km/h，'
                f'天气代码 {cur.get("weather_code")}'
            )

        tools = [get_time, search_knowledge_base, get_weather]

        llm = ChatOpenAI(
                model='deepseek-v3.2',
                openai_api_key=os.getenv('API_KEY'),
                openai_api_base=os.getenv('API_BASE'),
                streaming=True,
                model_kwargs={
                    "stream_options": {
                        "include_usage": True,  # 输出token消耗数量
                    }
                }
            ).bind_tools(tools)

        class AgentState(TypedDict):
            messages: Annotated[Sequence[BaseMessage], add_messages] #将大模型返回结果追加到输入消息的末尾

        def model_call(state: AgentState) -> AgentState: #在agent里调用大模型
            pprint(state)
            res = llm.invoke(state['messages'])
            return {'messages': [res]}

        def should_continue(state: AgentState) -> str:
            last_message = state['messages'][-1]
            if last_message.tool_calls:
                return "tools"
            return "end"

        tool_node = ToolNode(tools)

        graph = StateGraph(AgentState)
        graph.add_node('agent', model_call)
        graph.add_node('tools', tool_node)

        #加上2条边
        graph.add_edge(START, 'agent')
        graph.add_conditional_edges(
            'agent',
            should_continue,
            {
                'tools': 'tools',
                'end': END,
            }
        )
        graph.add_edge('tools', 'agent')

        return graph.compile()
