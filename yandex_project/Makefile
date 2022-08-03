include .env

.PHONY: first_start, collect-static, migrate, createsuperuser, update_db, build, up, build_tests, start_tests

build:
	docker-compose build

up:
	docker-compose up

collect-static:
	docker exec yandex_project-service-1 python3 manage.py collectstatic --noinput

migrate:
	docker exec yandex_project-service-1 python3 manage.py migrate --fake-initial

createsuperuser:
	docker exec yandex_project-service-1 python3 manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('${DJANGO_SUPERUSER_USERNAME}', '${DJANGO_SUPERUSER_EMAIL}', '${DJANGO_SUPERUSER_PASSWORD}')"

update_db:
	docker exec elt-process bash -c "cd update_db && python3 load_data.py"

delete_date_from_redis:
	docker exec yandex_project-redis-1 redis-cli del mod_date

build_tests:
	cd tests/functional && docker-compose build

start_tests:
	cd tests/functional && docker-compose up


first_start: collect-static migrate createsuperuser update_db delete_date_from_redis