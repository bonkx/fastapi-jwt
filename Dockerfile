FROM python:3.12-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN apt-get update \
    && apt-get install gcc postgresql-client -y \
    && apt-get clean

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt  \
    && rm -rf /root/.cache/pip

COPY . /app