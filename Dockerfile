FROM tiangolo/uvicorn-gunicorn:python3.11-slim
LABEL maintainer="Sebastian Ramirez <tiangolo@gmail.com>"
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY ./src/ /app