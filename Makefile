PYTHON_FOLDERS = api bounca certificate_engine vuetifyforms x509_pki superuser_signup
LOCAL_SERVER_PORT ?= 8000

default:
	@echo "No default target!"

frontend_collect:
	python manage.py collectstatic --link --noinput

runserver:
	python manage.py runserver 0.0.0.0:$(LOCAL_SERVER_PORT)

quality: flake8 black_check isort_check

isort_check:
	find $(PYTHON_FOLDERS) -path '**/migrations' -prune -o -name '*.py' -print | xargs isort -c

isort_fix:
	find $(PYTHON_FOLDERS) -path '**/migrations' -prune -o -name '*.py' -print | xargs isort

flake8:
	flake8 $(PYTHON_FOLDERS)

black_fix:
	black .

black_check:
	black --check .

website:
	$(MAKE) -C ./docs html

runwebsiteserver:
	python3 -m http.server -d ./docs/build/html  8090

createvueforms:
	python3 manage.py generate_forms

docserver:
	python3 -m http.server --directory ./docs/build/html 8090

update-python-packages:
	pur

migrate:
	python manage.py migrate

update-deps:
	uv pip compile --upgrade requirements.in -o requirements.txt
	uv pip compile --upgrade requirements.dev.in -o requirements.dev.txt
	uv pip compile --upgrade requirements.docs.in -o requirements.docs.txt

install-deps:
	pip install -r requirements.txt
	pip install -r requirements.dev.txt
	pip install -r requirements.docs.txt
