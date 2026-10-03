import json
from src.config import VECTOR_FILE
_cache = {}
def save(chunks,vectors,path=None):
    path = path or VECTOR_FILE
    with open(path,'w',encoding='utf-8') as f:
        json.dump({'chunks':chunks,'vectors':vectors},f,ensure_ascii=False)
        return path
def load(path=None):
    path = path or VECTOR_FILE
    if path not in _cache:

        with open(path,encoding='utf-8') as f:

            _cache[path]=json.load(f)
    db=_cache[path]
    return db['chunks'],db['vectors']














