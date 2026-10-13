from src.agent.tools import query_database
cases = [
    'SELECT COUNT(*) FROM qa_history',
    'SELECT * FROM book',
    'DELETE FROM qa_history',
    'SELECT * FROM user',
    'SELECT id FROM qa_history; DROP TABLE user',
    'SELECT name FROM book',
]
for sql in cases:

    print('  SQL  :%s'% sql)
    print('  返回  :%s'% query_database.invoke({'sql':sql}))
    print('-'*70)