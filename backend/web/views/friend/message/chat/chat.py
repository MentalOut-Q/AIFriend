import json
from pprint import pprint

from django.http import StreamingHttpResponse
from langchain_core.messages import HumanMessage, BaseMessageChunk, SystemMessage, AIMessage
from rest_framework.renderers import BaseRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.friend import Friend, Message, SystemPrompt
from web.views.friend.message.chat.graph import ChatGraph
from web.views.friend.message.memory.update import update_memory
import asyncio
import base64
import json
import os
import threading
import uuid
from queue import Queue

import websockets


META_SPEECH_PATTERNS = (
    '我需要查询',
    '我需要查',
    '我先查询',
    '我先查',
    '让我查询',
    '让我查',
    '我去查询',
    '我去查',
    '需要查询更多',
    '根据资料',
    '根据知识库',
    '根据角色故事',
)


class LeadingMetaSpeechFilter:
    def __init__(self):
        self.buffer = ''
        self.checked = False

    def feed(self, text):
        if self.checked:
            return text

        self.buffer += text
        sentence_end = -1
        for i, ch in enumerate(self.buffer):
            if ch in '。！？.!?\n':
                sentence_end = i
                break

        if sentence_end < 0 and len(self.buffer) < 80:
            return ''

        if sentence_end >= 0:
            first_sentence = self.buffer[:sentence_end + 1]
            rest = self.buffer[sentence_end + 1:]
        else:
            first_sentence = self.buffer
            rest = ''

        compact_sentence = ''.join(first_sentence.split())
        self.checked = True
        self.buffer = ''
        if any(pattern in compact_sentence for pattern in META_SPEECH_PATTERNS):
            return rest.lstrip()
        return first_sentence + rest

    def flush(self):
        if self.checked or not self.buffer:
            return ''
        text = self.buffer
        self.buffer = ''
        self.checked = True
        compact_text = ''.join(text.split())
        if any(pattern in compact_text for pattern in META_SPEECH_PATTERNS):
            return ''
        return text


class SSERenderer(BaseRenderer):
    media_type = 'text/event-stream'
    format = 'txt'
    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data

def add_system_prompt(state, friend):
    msgs = state['messages']
    system_prompts = SystemPrompt.objects.filter(title='回复').order_by('order_number')
    prompt = ''
    for sp in system_prompts:
        prompt += sp.prompt
    prompt += f'\n【角色性格】\n{friend.character.profile}\n'
    prompt += f'【长期记忆】\n{friend.memory}\n'
    prompt += '''
        【工具使用规则】
        - 需要查阅角色故事、时间、知识库时，直接调用对应工具，不要先输出任何说明文字。
        - 禁止说出「我需要查询」「让我查一下」「根据资料」等元话语。
        - 拿到工具结果后，只用角色身份自然回答，不要提及工具、知识库、文档。
        '''
    return {'messages': [SystemMessage(prompt)] + msgs}


def add_recent_messages(state, friend):
    msgs = state['messages']
    message_raw = list(Message.objects.filter(friend=friend).order_by('-id')[:10])
    message_raw.reverse()
    messages = []
    for m in message_raw:
        messages.append(HumanMessage(m.user_message))
        messages.append(AIMessage(m.output))
    return {'messages': msgs[:1] + messages + msgs[-1:]} # 把10轮对话加入到系统提示词和用户消息之间

class MessageChatView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [SSERenderer]
    def post(self, request):
        friend_id = request.data['friend_id']
        message = request.data['message'].strip()
        if not message:
            return Response({
                'result': '消息不能为空'
            })
        friends = Friend.objects.filter(pk=friend_id, me__user=request.user) # 好友的聊天对象是登录的账号, 因为你不能和别人的好友聊天
        if not friends.exists():
            return Response({
                'result': '好友不存在'
            })
        friend = friends.first()
        app = ChatGraph.create_app(character_id=friend.character.id)

        inputs = {
            'messages': [HumanMessage(message)]
        }

        inputs = add_system_prompt(inputs, friend)
        inputs = add_recent_messages(inputs, friend)
        pprint(inputs)

        response = StreamingHttpResponse(
            self.event_stream(app, inputs, friend, message),
            content_type='text/event-stream',
        )

        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response

    async def send_tts_text(self, ws, task_id, content):
        await ws.send(json.dumps({
            "header": {
                "action": "continue-task",
                "task_id": task_id,  # 随机uuid
                "streaming": "duplex"
            },
            "payload": {
                "input": {
                    "text": content,
                }
            }
        }))

    async def finish_tts_task(self, ws, task_id):
        await ws.send(json.dumps({
            "header": {
                "action": "finish-task",
                "task_id": task_id,
                "streaming": "duplex"
            },
            "payload": {
                "input": {}  # input不能省去，否则会报错
            }
        }))

    async def tts_sender(self, app, inputs, mq, ws=None, task_id=None):
        meta_speech_filter = LeadingMetaSpeechFilter()
        tts_enabled = ws is not None and task_id is not None
        async for msg, metadata in app.astream(inputs, stream_mode="messages"):
            if isinstance(msg, BaseMessageChunk):
                if msg.content:
                    content = meta_speech_filter.feed(msg.content)
                    if not content:
                        continue
                    mq.put_nowait({'content': content})
                    if tts_enabled:
                        try:
                            await self.send_tts_text(ws, task_id, content)
                        except Exception as e:
                            print(f'语音合成发送失败，已继续输出文字：{e}')
                            tts_enabled = False
                if hasattr(msg, 'usage_metadata') and msg.usage_metadata:
                    mq.put_nowait({'usage': msg.usage_metadata})
        content = meta_speech_filter.flush()
        if content:
            mq.put_nowait({'content': content})
            if tts_enabled:
                try:
                    await self.send_tts_text(ws, task_id, content)
                except Exception as e:
                    print(f'语音合成发送失败，已继续输出文字：{e}')
                    tts_enabled = False
        if tts_enabled:
            try:
                await self.finish_tts_task(ws, task_id)
            except Exception as e:
                print(f'语音合成结束失败，已继续输出文字：{e}')
                tts_enabled = False
        return tts_enabled

    async def tts_receiver(self, mq, ws):
        try:
            async for msg in ws:
                if isinstance(msg, bytes):
                    audio = base64.b64encode(msg).decode('utf-8')
                    mq.put_nowait({'audio': audio})
                else:
                    data = json.loads(msg)
                    event = data['header']['event']
                    if event in ['task-finished', 'task-failed']:
                        break
        except Exception as e:
            print(f'语音合成接收失败，已继续输出文字：{e}')

    async def wait_task_started(self, ws):
        async for msg in ws:
            data = json.loads(msg)
            header = data.get('header', {})
            event = header.get('event')
            if event == 'task-started':
                return
            if event == 'task-failed':
                raise RuntimeError(data.get('payload') or header.get('error_message') or data)

    async def run_tts_tasks(self, app, inputs, mq, voice_id):
        task_id = uuid.uuid4().hex
        api_key = os.getenv('API_KEY')
        wss_url = os.getenv('WSS_URL')
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        try:
            ws_context = websockets.connect(wss_url, additional_headers=headers)
            ws = await ws_context.__aenter__()
            await ws.send(json.dumps({
                "header": {
                    "action": "run-task",
                    "task_id": task_id,  # 随机uuid
                    "streaming": "duplex"
                },
                "payload": {
                    "task_group": "audio",
                    "task": "tts",
                    "function": "SpeechSynthesizer",
                    "model": "cosyvoice-v3-flash",
                    "parameters": {
                        "text_type": "PlainText",
                        "voice": voice_id,  # 音色
                        "format": "mp3",  # 音频格式
                        "sample_rate": 22050,  # 采样率
                        "volume": 50,  # 音量
                        "rate": 1.25,  # 语速
                        "pitch": 1  # 音调
                    },
                    "input": {  # input不能省去，不然会报错
                    }
                }
            }))
            await self.wait_task_started(ws)
        except Exception as e:
            print(f'语音合成初始化失败，已改为只输出文字：{e}')
            await self.tts_sender(app, inputs, mq)
            return

        try:
            receiver_task = asyncio.create_task(self.tts_receiver(mq, ws))
            tts_enabled = await self.tts_sender(app, inputs, mq, ws, task_id)
            if tts_enabled and not receiver_task.done():
                await receiver_task
            elif not tts_enabled and not receiver_task.done():
                receiver_task.cancel()
        finally:
            await ws_context.__aexit__(None, None, None)

    def work(self, app, inputs, mq, voice_id):
        try:
            asyncio.run(self.run_tts_tasks(app, inputs, mq, voice_id))
        except Exception as e:
            mq.put_nowait({'error': f'语音或模型调用失败：{e}'})
        finally:
            mq.put_nowait(None)

    def event_stream(self, app, inputs, friend, message):
        mq = Queue()
        thread = threading.Thread(target=self.work, args=(app, inputs, mq, friend.character.voice.voice_id))
        thread.start()

        full_output = ''
        full_usage = {}
        while True:
            msg = mq.get()
            if not msg:
                break
            if msg.get('content', None):
                full_output += msg['content']
                yield f'data: {json.dumps({'content': msg['content']}, ensure_ascii=False)}\n\n'
            if msg.get('audio', None):
                yield f'data: {json.dumps({'audio': msg['audio']}, ensure_ascii=False)}\n\n'
            if msg.get('usage', None):
                full_usage = msg['usage']
            if msg.get('error', None):
                yield f'data: {json.dumps({'error': msg['error']}, ensure_ascii=False)}\n\n'

        yield 'data: [DONE]\n\n'
        input_tokens = full_usage.get('input_tokens', 0)
        output_tokens = full_usage.get('output_tokens', 0)
        total_tokens = full_usage.get('total_tokens', 0)
        Message.objects.create(
            friend=friend,
            user_message=message[:500],
            input=json.dumps(
                [m.model_dump() for m in inputs['messages']],
                ensure_ascii=False,
            )[:10000],
            output=full_output[:500],
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
        )
        if Message.objects.filter(friend=friend).count() % 1 == 0:
            try:
                update_memory(friend)
            except Exception as e:
                print(f'记忆更新失败：{e}')
