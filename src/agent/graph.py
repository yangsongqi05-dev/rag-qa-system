from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from src.config import CHAT_MODEL, get_header
from src.agent.tools import search_knowledge
from langgraph.checkpoint.memory import InMemorySaver
BASE_URL = 'https://api.siliconflow.cn/v1'
SYSTEM_PROMPT=(
    '你是数据库课程助手。回答前先调用search_knowledge查资料'
    '只根据查到的资料作答，资料里没有的，就直说没有，不要编造'
)
def build_model():
    key=get_header()['Authorization'].replace('Bearer ','')
    return ChatOpenAI(
        model=CHAT_MODEL,
        base_url=BASE_URL,
        api_key=key,
        temperature=0
                      )
agent=create_agent(
    model=build_model(),
    tools=[search_knowledge],
    system_prompt=SYSTEM_PROMPT,
    checkpointer=InMemorySaver(),

)
def ask(question,thread_id='default'):
    result=agent.invoke(
        {'messages':[{'role':'user','content':question}]},
        {'configurable':{'thread_id':thread_id}}
    )
    message=result['messages']
    return message[-1].content,message


async def ask_stream(qustion,thread_id='default'):
    async for chunk,meta in agent.astream(
            {'messages':[{'role':'user','content':qustion}]},
        {'configurable':{'thread_id':thread_id}},
        stream_mode='messages'
    ):
        node=meta.get('langgraph_node')
        if node=='tools':
            yield {'type':'tool_result','text':str(chunk.content)}
            continue
        cc=getattr(chunk,'tool_call_chunks',None)
        if cc:
            for c in cc:
                if c.get('name'):
                    yield {'type':'tool_call','name':c['name']}
        elif chunk.content:
            yield {'type':'text','text':chunk.content}

    yield {'type':'done'}












def to_steps(messages):
    start = 0
    for i in range(len(messages)-1,-1,-1):
        if type(messages[i]).__name__=='HumanMessage':
            start=i
            break

    steps=[]
    for m in messages[start:]:
        name =type(m).__name__
        if name == 'HumanMessage':
            continue
        if name =='AIMessage':
            calls = getattr(m,'tool_calls',None)
            if calls:
                for tc in calls:
                    steps.append(
                        {
                            'type':'tool_call',
                            'name':tc['name'],
                            'args':tc['args'],
                        }
                    )
            elif m.content:
                steps.append({'type':'answer','text': str(m.content)[:200]})
        elif name =='ToolMessage':
            steps.append({'type':'tool_result','text': str(m.content)[:200]})
    return steps






























