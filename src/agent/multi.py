from typing import Annotated, TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
import os
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

from src.config import CHAT_MODEL, get_header,DATA_DIR
from src.agent.tools import search_knowledge, query_database
from langchain_core.messages import ToolMessage
from langgraph.types import interrupt
BASE_URL = 'https://api.siliconflow.cn/v1'

def build_model():
    key = get_header()['Authorization'].replace('Bearer ','')
    return ChatOpenAI(model=CHAT_MODEL, api_key=key,base_url=BASE_URL,temperature=0)
DB_FILE = os.path.join(DATA_DIR,'checkpoints.db')
def build_checkpointer():
    conn = sqlite3.connect(DB_FILE,check_same_thread=False)
    return SqliteSaver(conn)
KB_PROMPT = (
    '你是数据库课程的知识库助手，只回答数据库概念和原理类问题。'
    '回答前必须调用 search_knowledge 查资料，只根据查到的资料作答，'
    '资料里没有的就直说没有，不要编造。'
)
DB_PROMPT = (
    '你是数据库查询助手，负责回答数据库里的具体数据问题。'
    '调用 query_database 查询，只允许写 SELECT。查不到就如实说明，不要编造数据。'
)
CHAT_PROMPT = (
    '你是数据库课程助手。用户在打招呼或闲聊，简短友好地回应即可，不要调用任何工具。'
)
ROUTE_PROMPT = (
    '判断用户这句话属于哪一类，只输出一个词，不要解释、不要标点：\n'
    'kb —— 数据库概念或原理类问题，比如"什么是回表""事务隔离级别"；\n'
    'db —— 想查数据库里的具体数据，比如"有几条记录""有哪些书"；\n'
    'chat —— 打招呼、闲聊，或者和数据库完全无关的话。'
)
class State(TypedDict):
    messages: Annotated[list,add_messages]
    route:str

def build_multi_agent():
    model=build_model()
    roles={
        'kb':  (model.bind_tools([search_knowledge]),KB_PROMPT),
        'db': (model.bind_tools([query_database]),DB_PROMPT),
        'chat': (model,CHAT_PROMPT),
    }
    tool_map = {'search_knowledge':search_knowledge,'query_database':query_database,}
    def router(state):
        res = model.invoke([
            {'role':'system','content':ROUTE_PROMPT},
            {'role':'user','content':str(state['messages'][-1].content)},
        ] )
        word=res.content.strip().lower()
        if 'db' in word :
            return {'route':'db'}
        if 'kb' in word :
            return {'route':'kb'}
        return {'route':'chat'}
    def model_node(state):
        bind,prompt = roles.get(state['route'],roles['chat'])
        res = bind.invoke([{'role':'system','content':prompt}]+state['messages'])
        return {'messages':[res]}
    def tools_node(state):
        out_msgs=[]
        for tc in state['messages'][-1].tool_calls:
            tool = tool_map.get(tc['name'])
            if tool is None:
                continue
            if tc['name']=='query_database':
                ok = interrupt({'type':'confirm_sql','sql':tc['args'].get('sql','')})
                if not ok:
                    out_msgs.append(ToolMessage(
                        content = '用户取消了这次查询，请不要执行这条 SQL',
                        tool_call_id=tc['id'],

                    ))
                    continue
            out_msgs.append(tool.invoke(tc))
        return {'messages':out_msgs}
    def should_continue(state):
        if getattr(state['messages'][-1],'tool_calls',None):
            return 'tools'
        return END
    b = StateGraph(State)
    b.add_node('router',router)
    b.add_node('model',model_node)
    b.add_node('tools',tools_node)
    b.add_edge(START,'router')
    b.add_edge('router','model')
    b.add_conditional_edges('model',should_continue,{'tools':'tools',END:END})
    b.add_edge('tools','model')
    return b.compile(checkpointer=build_checkpointer())




























