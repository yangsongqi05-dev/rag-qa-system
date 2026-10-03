import json
import os
from src.config import BASE_DIR,TOP_K,MIN_SCORE
from src.core import retriever
EVAL_FILE=os.path.join(BASE_DIR,'tests','eval_set.json')
with open(EVAL_FILE,encoding='utf-8') as f:
    cases = json.load(f)
in_total=out_total=0
in_hit=out_hit=0
miss_list=[]
cls_hit=0
wrong_list=[]
print(f'测试集{len(cases)}条 阀值{MIN_SCORE}')
print('-'*62)
for case in cases:
    q=case['q']
    results= retriever.search(q,top_k=TOP_K)
    top1=results[0][0]
    if case['in_kb']:
        in_total+=1
        ok=any(case['expect']in text for _,text in results)
        if ok:
            in_hit+=1
            if top1>=MIN_SCORE:
                cls_hit+=1
        else:
            miss_list.append((q,top1))
        tag = '域内'
    else:
        out_total+=1
        ok = top1<MIN_SCORE
        if ok:
            out_hit+=1
            if top1<MIN_SCORE:
                cls_hit+=1
        else:
            wrong_list.append((q,top1))
        tag='域外'
        mark = 'ok' if ok else 'x'
        print(f'[{tag}] {mark} {top1:.3f} {q}')
print('-'*62)
if in_total>0:
    print(f'域内命中率：{in_hit}/{in_total} = {in_hit / in_total:.1%}')
print(f'域外拒答率：{out_hit}/{out_total} = {out_hit / out_total:.1%}')
total_hit = in_hit + out_hit
print(f'阈值分类准确率：{cls_hit}/{len(cases)} = {cls_hit / len(cases):.1%}')
print()
if miss_list:
    print('库里有的但没有检索到：')
    for q,s in miss_list:
        print(f'{s:.3f} {q}')
if wrong_list:
    print('库里没有但分数偏高的：')
    for q,s in wrong_list:
        print(f'{s:.3f} {q}')







































