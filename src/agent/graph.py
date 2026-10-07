from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from src.config import CHAT_MODEL, get_header
from src.agent.tools import search_knowledge
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

)
def ask(question):
    result=agent.invoke(
        {'messages':[{'role':'user','content':question}]}
    )
    message=result['messages']
    return message[-1].content,message
































