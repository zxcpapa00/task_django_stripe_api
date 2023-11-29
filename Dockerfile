FROM python:3.9-alpine3.16

WORKDIR /task

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /task
COPY ./requirements.txt /task/requirements.txt
COPY ./.env /task/.env
EXPOSE 8000

RUN pip install --upgrade pip

RUN apk add postgresql-client &&  \
    apk add build-base &&  \
    apk add postgresql-dev &&  \
    rm -f /var/lib/apt/lists/*

RUN pip install -r requirements.txt