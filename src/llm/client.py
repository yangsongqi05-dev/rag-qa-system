
import json
import requests
from src.config import CHAT_MODEL,CHAT_URL,get_header
def chat(system,user):
    data={
        'model':CHAT_MODEL,
        'messages':[
            {'role':'system','content':system},
            {'role':'user','content':user}
        ]
    }

    resp = requests.post(CHAT_URL,headers=get_header(),json=data)
    if resp.status_code != 200:
        raise RuntimeError(f'生成失败：{resp.status_code}{resp.text}')
    return resp.json()['choices'][0]['message']['content']

def chat_stream(system,user):
    data={
        'model':CHAT_MODEL,
        'messages':[
            {'role':'system','content':system},
            {'role':'user','content':user}
        ],
        'stream':True
    }
    resp = requests.post(CHAT_URL,headers=get_header(),json=data,stream=True)
    resp.encoding = 'utf-8'
    if resp.status_code != 200:
        raise RuntimeError((f'生成失败：{resp.status_code} {resp.text}'))
    for line in resp.iter_lines(decode_unicode=True):
        if not line or not line.startswith('data: '):
            continue
        payload = line[6:]
        if payload=='[DONE]':
            break
        chunk = json.loads(payload)
        piece=chunk['choices'][0]['delta'].get('content')
        if piece:
            yield piece

















