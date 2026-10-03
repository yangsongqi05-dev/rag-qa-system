MIN_LEN=45
MAX_LEN=420
def split_text(text):
    raw = [p.strip() for p in text.split('\n\n') if p.strip()]
    chunks= []
    for p in raw:
        if chunks and len(p) < MIN_LEN and len(chunks[-1]) + len(p) < MAX_LEN:
            chunks[-1] = chunks[-1] + '\n' + p
        else:
            chunks.append(p)
    return chunks










