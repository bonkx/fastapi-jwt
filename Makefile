CURRENT_DIRECTORY := $(shell pwd)
CURRENT_USER := $(shell whoami)
CURRENT_TIME = $(shell date +"%Y%m%d_%H%M")
CURRENT_TIME_SECONDS = $(shell date +"%Y%m%d_%H%M%S")

PYTEST_REPORT_FILENAME = pytest-report.${CURRENT_TIME}.html

guard-%:
	@ if [ "${${*}}" = "" ]; then \
        echo "Environment variable $* not set"; \
        exit 1; \
	fi

hello: guard-MSG
	@echo ${MSG}

dev:
	python -m uvicorn app.main:app --reload
# 	python main.py

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

test:
	-pytest --cov --cov-report=html --html=${PYTEST_REPORT_FILENAME} ${ARGS}
	-start "" "$(CURRENT_DIRECTORY)/${PYTEST_REPORT_FILENAME}"
	-start "" "$(CURRENT_DIRECTORY)/htmlcov/index.html"
# 	-python -m webbrowser -t file://${CURRENT_DIRECTORY}/${PYTEST_REPORT_FILENAME}
# 	-python -m webbrowser -t file://${CURRENT_DIRECTORY}/htmlcov/index.html

test-changes:
ifdef RESET
	@make reset-artifact ARTIFACT=.testmondata
endif
	-pytest --testmon --html=${PYTEST_REPORT_FILENAME} ${ARGS}
	-start "" "$(CURRENT_DIRECTORY)/${PYTEST_REPORT_FILENAME}"
# 	-python -m webbrowser -t file://${CURRENT_DIRECTORY}/${PYTEST_REPORT_FILENAME}