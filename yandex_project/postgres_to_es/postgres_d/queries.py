QUERY_TEMPLATE = '''
SELECT
    fw.id,
    fw.rating AS rating,
    ARRAY_AGG(DISTINCT g.name) as genre,
    fw.title,
    fw.description,
    ARRAY_AGG(DISTINCT p.full_name) FILTER (
        WHERE pfw.role = 'director'
    ) AS directors_names,
    ARRAY_AGG(DISTINCT p.full_name) FILTER (
        WHERE pfw.role = 'actor'
    ) AS actors_names,
    ARRAY_AGG(DISTINCT p.full_name) FILTER (
        WHERE pfw.role = 'writer'
    ) AS writers_names,
    COALESCE (
        json_agg(
            DISTINCT jsonb_build_object(
                'id', p.id,
                'name', p.full_name
            )
        ) FILTER (WHERE pfw.role = 'actor'),
        '[]'
    ) as actors,
    COALESCE (
        json_agg(
            DISTINCT jsonb_build_object(
                'id', p.id,
                'name', p.full_name
            )
        ) FILTER (WHERE pfw.role = 'writer'),
        '[]'
    ) as writers,
    fw.modified
        FROM content.film_work AS fw
            LEFT JOIN content.person_film_work AS pfw ON pfw.film_work_id = fw.id
            LEFT JOIN content.person AS p ON p.id = pfw.person_id
            LEFT JOIN content.genre_film_work AS gfw ON gfw.film_work_id = fw.id
            LEFT JOIN content.genre AS g ON g.id = gfw.genre_id
        WHERE fw.id IN {}
        GROUP BY fw.id
        ORDER BY fw.modified;
'''

QUERY_GET_ALL_FILMS = '''
SELECT fw.id AS id
    FROM content.film_work fw;
'''

QUERY_GET_FILMS_BY_DATE_MODIFY = '''
SELECT fw.id AS id
    FROM content.film_work fw
    WHERE fw.modified > '{mod_date}'
    UNION
        SELECT pfw.film_work_id
            FROM content.person_film_work AS pfw
            WHERE pfw.person_id IN (SELECT p.id
                FROM content.person AS p
                WHERE p.modified > '{mod_date}'
    UNION
        SELECT gfw.film_work_id
            FROM content.genre_film_work AS gfw
            WHERE gfw.genre_id IN (SELECT g.id
                FROM content.genre AS g
                WHERE g.modified > '{mod_date}';
'''
