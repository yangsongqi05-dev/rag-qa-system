from src.rag.pipeline import answer
question = 'WHERE 和 HAVING 有什么区别'
reply, source = answer(question)
print(f'问题：{question}')
print()
print('回答：')
print(reply)
print()
print('依据的资料:')
for score,text in source:
    print(f'[{score:.4f}]{text[:60]}...')