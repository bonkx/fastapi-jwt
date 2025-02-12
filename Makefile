guard-%:
	@ if [ "${${*}}" = "" ]; then \
        echo "Environment variable $* not set"; \
        exit 1; \
	fi

hello: guard-MSG
	@echo ${MSG}

dev:
	python main.py

migrations: guard-MSG
	alembic revision --autogenerate -m "${MSG}"

migrate:
	alembic upgrade head

pip:
	pip install -r requirements.txt

build:
	docker-compose down
	docker-compose build	

run:
	docker-compose up --remove-orphans

cov:
	pytest --cov=app tests/

cov-html:
	pytest --cov=app --cov-report=html tests/

	