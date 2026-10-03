import math
from src.core import store
k1 =1.5
B =0.75
_index = {}
def tokenize(text):
    text = ''.join(ch for ch in text if ch.isalnum())
    return [text[i:i+2] for i in range(len(text)-1)]
def build_index(chunks):
    tfs=[]
    df={}
    for chunk in chunks:
        tf={}
        for t in tokenize(chunk):
            tf[t]=tf.get(t,0)+1
        tfs.append(tf)
        for t in tf:
            df[t]=df.get(t,0)+1
    return tfs,df
def search(question,top_k=3,chunks=None):
    if chunks is None:
        chunks,_=store.load()
    if _index.get('chunks')is not chunks:
        tfs,df=build_index(chunks)
        _index['chunks']=chunks
        _index['df']=df
        _index['tfs']=tfs
    tfs = _index['tfs']
    df=_index['df']
    n = len(chunks)
    avg_len=sum(sum(tf.values()) for tf in tfs) /n
    q_tokens=tokenize(question)
    scores =[]
    for i,tf in enumerate(tfs):
        dl =sum(tf.values())
        s=0.0
        for t in q_tokens:
            f = tf.get(t,0)
            if f == 0:
                continue

            idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
            s += idf * (f * (k1 + 1)) / (f + k1 * (1 - B + B * dl / avg_len))
        scores.append((s, i))
    scores.sort(reverse=True)
    return [(s, chunks[i]) for s, i in scores[:top_k]]


































