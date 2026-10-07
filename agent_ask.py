
from src.agent import graph


question = input('问点什么：')
answer,messages = graph.ask(question)
print('\n--------中间过程-------------')
for i,m in enumerate(messages):
    name = type(m).__name__
    text = m.content if isinstance(m.content,str) else str(m.content)
    print('[%d] %-16s %s'%(i,name,text[:80].replace('\n',' ')))
    if getattr(m,'tool_calls', None):
        for tc in m.tool_calls:
            print('      >>> Agent 决定调用工具: %s(%s)' % (tc['name'], tc['args']))
print('\n----------回答-----------')
print(answer)






















