QUERY_GET_GENRES = '''
    SELECT id, name 
    FROM content.genre 
    WHERE modified > '{date_modify}';
'''
