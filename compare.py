import json
import os

from src.core import retriever, bm25, hybrid
from src.config import  BASE_DIR,TOP_K

EVAL_FILE=os.path.join(BASE_DIR,'tests','eval_set.json')
with open(EVAL_FILE,encoding='utf-8') as f:
    cases = json.load(f)
methons={
    '纯向量检索':retriever.search,
    'BM25关键词':bm25.search,
    '混合检索': hybrid.search,
    '向量+rerank': retriever.search_rerank,

}
groups = ['术语','口语']
for name, fn in methons.items():
    parts = []
    total_hit=0
    total_n=0
    for g in groups:
        subs = [c for c in cases if c.get('type') == g]
        hit =0
        for c in subs:
            top1 = fn(c['q'],TOP_K)[0][1]
            if c['expect'] in top1:
                hit+=1
        parts.append(f'{g}题{hit}/{len(subs)}')
        total_hit+=hit
        total_n+=len(subs)
    print(f'{name}：' + '  |  '.join(parts) + f'  |  合计 {total_hit}/{total_n} = {total_hit / total_n:.0%}')


























