import requests
from src.config import EMBED_MODEL,EMBED_URL,get_header
def embed_batch(texts):
    data = {'model': EMBED_MODEL, 'input': texts}
    resp = requests.post(EMBED_URL, json=data,headers=get_header())
    if resp.status_code != 200:
        raise RuntimeError(f'向量化失败：{resp.status_code}{resp.text}')
    items = resp.json()['data']
    items.sort(key=lambda x: x['index'])
    return [it['embedding'] for it in items]

def embed_one(text):
    return embed_batch([text])[0]