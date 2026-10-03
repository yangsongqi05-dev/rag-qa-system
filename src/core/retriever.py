"""检索：从向量库里找出跟问题最相关的几块原文"""

import math

from src.config import TOP_K
from src.core.embedder import embed_one
from src.core import store, rerank


def cosine(a, b):
    """余弦相似度：算两个向量有多像，越接近 1 越像"""
    dot = sum(x * y for x, y in zip(a, b))
    len_a = math.sqrt(sum(x * x for x in a))
    len_b = math.sqrt(sum(y * y for y in b))
    return dot / (len_a * len_b)


def rank_by_vector(question):
    """把问题跟库里所有向量算一遍相似度，返回排好序的 (分数, 下标)"""
    chunks, vectors = store.load()
    qvec = embed_one(question)
    scores = []
    for i in range(len(vectors)):
        scores.append((cosine(qvec, vectors[i]), i))
    scores.sort(reverse=True)
    return scores


def search(question, top_k=TOP_K):
    """纯向量检索（实验基线用）"""
    chunks, _ = store.load()
    results = [(s, chunks[i]) for s, i in rank_by_vector(question)[:top_k]]
    return results


def search_rerank(question, top_k=TOP_K, coarse=10):
    """两阶段检索：向量粗筛出 coarse 个候选，再 rerank 精排取前 top_k"""
    chunks, _ = store.load()
    candidates = [chunks[i] for _, i in rank_by_vector(question)[:coarse]]
    return rerank.rerank(question, candidates, top_k)








