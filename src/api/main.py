from fastapi import FastAPI
from fastapi.responses import FileResponse,StreamingResponse
from fastapi.staticfiles import StaticFiles
import json
from src.config import INDEX_FILE, WEB_DIR, TOP_K
from src.rag import pipeline
app = FastAPI()
app.mount('/web', StaticFiles(directory=WEB_DIR), name='web')
@app.get("/")
def home():
    """首页：返回问答页面"""
    return FileResponse(INDEX_FILE)
@app.get('/ask')
def ask(q: str, top_k: int = TOP_K, use_rerank: bool = True):
    """提问接口：/ask?q=你的问题&top_k=3&use_rerank=true"""
    reply, sources = pipeline.answer(q, top_k, use_rerank)
    return {
        'answer': reply,
        'sources': [{'score': round(s, 4), 'text': t} for s, t in sources]
    }
@app.get('/ask_stream')
def ask_stream(q: str, top_k: int = TOP_K, use_rerank: bool = True):
    """流式提问接口：服务器推一段，前端显示一段"""
    def events():
        for item in pipeline.answer_stream(q, top_k, use_rerank):
            yield  'data: '  + json.dumps(item,ensure_ascii=False)+'\n\n'
    return StreamingResponse(events(), media_type="text/event-stream")

















