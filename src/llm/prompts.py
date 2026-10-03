SYSTEM_PROMPT='你是一个严谨的数据库课程助手，只根据学生提供的资料作答'
def build_prompt(question,contexts):
    material = '\n\n'.join(contexts)
    return f'''请严格根据下面的资料回答学生的问题。
资料里没有的信息，就回答"我的资料里没有提到这一点"，绝对不要自己编。
【资料】
{material}
【问题】
{question}



'''

