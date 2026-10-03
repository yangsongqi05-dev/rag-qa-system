import os
# 项目根目录（也就是 rag_agent 这个文件夹）
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath((__file__))))

# 数据相关路径
DATA_DIR=os.path.join(BASE_DIR,'data')
RAW_DIR=os.path.join(DATA_DIR,'raw')
CORPUS_FILE=os.path.join(RAW_DIR,'mysql_knowledge.txt')
VECTOR_FILE=os.path.join(DATA_DIR,'vector.json')
WEB_DIR = os.path.join(BASE_DIR, 'web')

# 密钥文件
API_KEY_FILE=r'E:\python\api_key.txt.txt'
# 模型与接口
EMBED_MODEL = 'BAAI/bge-m3'
CHAT_MODEL = 'deepseek-ai/DeepSeek-V3'
EMBED_URL = 'https://api.siliconflow.cn/v1/embeddings'
CHAT_URL = 'https://api.siliconflow.cn/v1/chat/completions'
RERANK_MODEL = 'BAAI/bge-reranker-v2-m3'
RERANK_URL = 'https://api.siliconflow.cn/v1/rerank'
# 检索参数
TOP_K=3
BATCH_SIZE= 16
MIN_SCORE = 0.55

def get_header():
    with open(API_KEY_FILE,encoding='utf-8') as f:
        key = f.read().strip()
    return {
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }
INDEX_FILE = os.path.join(BASE_DIR, 'web', 'index.html')


















