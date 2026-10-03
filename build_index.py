
import time
from src.config import BATCH_SIZE
from src.core.embedder import embed_batch
from src.core import store
from src.core.loader import load_corpus
from src.core.splitter import split_text

text = load_corpus()
print(f'语料共{len(text)}')
chunks = split_text(text)
print(f'切成{len(chunks)}块')

vectors = []
for i in range(0, len(chunks), BATCH_SIZE):
    batch = chunks[i:i+BATCH_SIZE]
    vectors.extend(embed_batch(batch))
    print(f'向量进度{len(vectors)}/{len(chunks)}')
    time.sleep(0.3)

path = store.save(chunks,vectors)
print(f'向量已保存：{path}')
print(f'共{len(vectors)}个向量，每个{len(vectors[0])}维')







lens = sorted([len(c) for c in chunks])
print(f'块长：最短{lens[0]},中位{lens[len(lens)//2]},最长{lens[-1]}')

print()
for i,c in enumerate(chunks[:2],1):
    print(f'---第{i}块({len(c)}字)---)')
    print(c[:150])
    print()






