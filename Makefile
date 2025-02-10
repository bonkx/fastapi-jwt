dev:
	python main.py

migrate:
	python app/configs/migrate.py

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