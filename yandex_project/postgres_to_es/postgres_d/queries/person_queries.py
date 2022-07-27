QUERY_GET_PERSONS = '''
    SELECT id, full_name 
    FROM content.person 
    WHERE modified > '{date_modify}';
'''