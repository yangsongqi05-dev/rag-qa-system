from src.core import retriever,bm25
k =60
POOL = 10
def search(question,top_k=3,pool=POOL):
    vec_hits = retriever.search(question,pool)
    bm_hits =bm25.search(question,pool)
    scores = {}
    for rank,(_,text) in enumerate(vec_hits):
        scores[text] = scores.get(text,0)+1 /(k+rank)
    for rank,(_,text) in enumerate(bm_hits):
        scores[text] = scores.get(text,0)+1 /(k+rank)
    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    return [(score,text) for text,score in ranked[:top_k]]
















