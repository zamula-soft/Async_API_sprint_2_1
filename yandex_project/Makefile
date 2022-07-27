.PHONY: admin docker-up collect-static

go: collect-static docker-up django-setup


collect-static:
	python3 app/manage.py collectstatic

docker-up:
	docker compose up -d

django-setup:docker-up
	docker exec yandex_project-service-1 python3 manage.py migrate --fake-initial
# при --noinput логин и пароль возмутся из переменных окружения, если юзер уже есть - упадет с ошибкой, но пойдет дальше.
	docker exec yandex_project-service-1 python3 manage.py createsuperuser --noinput || true

restart:
	docker-compose down
#можно добавить удаление контейнеров	