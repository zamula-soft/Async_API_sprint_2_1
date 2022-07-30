# NashNetfilx

Our analogue Netflix as part of training at Yandex. (Our answer to the West :) )

main repository - [here](https://github.com/psgaiduk/Async_API_sprint_1)

Now done:
- Admin panel of the site where you can create a movie, genre, person.
- Synchronization between the site admin panel and elasticsearch is performed every 10 seconds 
(when creating a new object or changing an existing one).
- API for working with movies, genres and persons.

## Project structure:

Main folder is yandex_project.
1. Admin panel - Django (Service)
2. Database - Postgres
3. Database cache - Redis
4. Search and indexing - ElasticSearch
5. Synchronization service between Postgres and ElasticSearch - ETL process 
6. Api for work with service - Fastapi

### Links:

- Admin panel http://{host}/admin
- Api documentation http://{host}:81/api/openapi

## Start project:

Build project

```shell
make build
```

Run project 
```shell
make up
```

For first start:
- Create static
- Create migration
- Create superuser
- Populate the database with data
```shell
make first_start
```

### ENV Project:
- DB_NAME - name of database in Postgres
- DB_USER - username in Postgres
- DB_PASSWORD - password for username in Postgres
- DB_HOST - name of service (postgres)
- DB_PORT - port for connect to database
- SECRET_KEY - Django secrete key
- DEBUG - Flag of debug
- ALLOWED_HOSTS - Hosts to connect to admin panel
- INTERNAL_IPS - Ips for connect to admin panel
- ES_PORT - port for connect to ElasticSearch
- ES_HOST - host name ElasticSearch
- REDIS_HOST - host name Redis
- REDIS_PORT - port for connect to Redis
- DJANGO_SUPERUSER_USERNAME - username for Django admin panel
- DJANGO_SUPERUSER_PASSWORD - password for Django admin panel
- DJANGO_SUPERUSER_EMAIL - email for Django admin

## Team:
1. Pavel Gaiduk
2. Kirill Bondar