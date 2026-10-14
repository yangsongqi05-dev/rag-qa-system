import sys, os, time
sys.path.insert(0, r'E:\python\rag_agent')
os.chdir(r'E:\python\rag_agent')

from src.agent import graph as g

T = 'sit_' + str(int(time.time()) % 100000)
print('thread =', T)

print('--- 1) 正常提问，问需要查库的 ---')
for ev in g.ask_stream('book 表里有几本书？', T):
    print('   ', ev)

print()
print('--- 2) 用户点【确认】，继续 ---')
for ev in g.ask_stream_resume(True, T):
    print('   ', ev)