"""RAG 流程：检索 -> 拼提示词 -> 生成回答"""
from src.config import TOP_K
from src.core import retriever

from src.llm import prompts,client


def answer(question, top_k=TOP_K, use_rerank=True):
    """走完整流程，返回 (回答, 依据列表)"""
    if use_rerank:
        results = retriever.search_rerank(question, top_k)
    else:
        results = retriever.search(question, top_k)
    contexts = [text for _, text in results]
    prompt = prompts.build_prompt(question, contexts)
    reply = client.chat(prompts.SYSTEM_PROMPT, prompt)
    return reply, results
def answer_stream(question, top_k=TOP_K, use_rerank=True):
    """流式版：先给依据，再一段一段吐回答"""
    if use_rerank:
        results = retriever.search_rerank(question, top_k)
    else:
        results = retriever.search(question, top_k)
    yield {'type':'sources',
           'sources':[{'score':round(s,4),'text':t}for s,t in results]}
    contexts = [text for _, text in results]
    prompt = prompts.build_prompt(question, contexts)
    for piece in client.chat_stream(prompts.SYSTEM_PROMPT, prompt):
        yield {'type':'text','text':piece}
    yield {'type':'done'}








