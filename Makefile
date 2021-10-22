PYTHON_FOLDERS = api bounca certificate_engine vuetifyforms x509_pki
LOCAL_SERVER_PORT ?= 8000

default:
	@echo "No default target!"

install: backend frontend

backend:
	@# Install Python dependencies
	pip install -q --requirement requirements.txt

frontend: frontend_dependencies frontend_collect

frontend_dependencies:
	@hash npm 2>/dev/null || (echo 'Command "npm" not found. Please make sure NodeJS is installed.' && exit 1)

	@# Install Node dependencies specified in package.json
	npm install

frontend_collect:
	python manage.py collectstatic --link --noinput

runserver:
	python manage.py runserver 0.0.0.0:$(LOCAL_SERVER_PORT)

quality: flake8 npmlint isort_check

isort_check:
	find $(PYTHON_FOLDERS) -path '**/migrations' -prune -o -name '*.py' -print | xargs isort -c

isort_fix:
	find $(PYTHON_FOLDERS) -path '**/migrations' -prune -o -name '*.py' -print | xargs isort

flake8:
	flake8 $(PYTHON_FOLDERS)

autopep8:
	autopep8 --in-place --aggressive --aggressive -r $(PYTHON_FOLDERS)

npmlint:
	npm run -s lint

eslint:
	npm run -s eslint

sass-lint:
	npm run -s sass-lint

gitclean:
	git clean \
		--exclude=*.sublime-* \
			--exclude=.idea \
		--exclude=etc/conf/services.yaml \
		--exclude=*/settings_local.py \
		--interactive \
		-dx
		# --dry-run \
