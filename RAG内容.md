离线： 故事 txt → 切块 → Embedding → 按角色写入 LanceDB。
在线： 用户提问 →（模型决定要查故事时）问题 Embedding → 靠 function call（search_character_story） 触发检索 → 在该角色向量表里取 top-k 相近段落 → 把原文交给 LLM → 生成角色化回答
其中LanceDB(向量数据库)存储角色故事.txt Embedding后的向量, ``vector_db.similarity_search(query, k=3)``
这是 LangChain 的 LanceDB 封装。创建/查询时没有传 distance="cosine" / metric="cosine"，所以一般走 LanceDB 默认度量：l2（欧氏距离）。
你也可以改成余弦相似度来计算, 不过你要自己写个函数导进来使用
like this:
```python
import numpy as np

def cosine_similarity(vec1, vec2):
    dot = np.dot(vec1, vec2)
    return dot / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# 比较向量相似度，值越大越相似
for v in vectors:
    similarity = cosine_similarity(vector, v)
    print("Cosine Similarity:", similarity)
```