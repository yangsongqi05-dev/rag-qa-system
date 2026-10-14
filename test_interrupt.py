import sys, os, time
sys.path.insert(0, r'E:\python\rag_agent')
os.chdir(r'E:\python\rag_agent')

from langgraph.types import Command
from src.agent import graph as g

# 每次换一个新 thread —— 避免上一次跑崩留下的脏状态干扰
T = 'itest_' + str(int(time.time()) % 100000)
CFG = {'configurable': {'thread_id': T}}
print('本次 thread =', T)

print('--- 第 1 次：问需要查库的问题 ---')
for chunk in g.agent.stream(
        {'messages': [{'role': 'user', 'content': 'book 表里有几本书？'}]},
        CFG, stream_mode='updates'):
    if isinstance(chunk, dict) and '__interrupt__' in chunk:
        print('   *** 中断了，要问用户：')
        for it in chunk['__interrupt__']:
            print('       ', it.value)
    else:
        print('   ', str(chunk)[:180])

print()
print('--- 第 2 次：resume=True，允许执行 ---')
for chunk in g.agent.stream(Command(resume=True), CFG, stream_mode='updates'):
    print('   ', str(chunk)[:180])