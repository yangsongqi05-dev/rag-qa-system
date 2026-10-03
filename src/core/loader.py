import os
from src.config import RAW_DIR
def load_corpus(folder=None):
    folder = folder or RAW_DIR
    parts=[

    ]
    for name in sorted(os.listdir(folder)):
        if not name.endswith('.txt'):
            continue
        with open(os.path.join(folder,name),encoding='utf-8') as f:
            content=f.read()
        print(f'读取{name}({len(content)}字)')
        parts.append(content)
    return '\n\n'.join(parts)



