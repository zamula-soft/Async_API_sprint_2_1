QUERY_GET_PERSONS_BY_DATE_MODIFY = '''
    SELECT id 
        FROM content.person 
        WHERE modified > '{date_modify}';
'''

QUERY_GET_PERSONS = '''
    SELECT id, full_name 
    FROM content.person 
    WHERE id in ({});
'''