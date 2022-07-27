QUERY_GET_GENRES_BY_DATE_MODIFY = '''
    SELECT id 
        FROM content.genre 
        WHERE modified > '{date_modify}';
'''

QUERY_GET_GENRES = '''
    SELECT id, name 
    FROM content.genre 
    WHERE id in ({});
'''
