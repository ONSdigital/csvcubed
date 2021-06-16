FROM python:latest

RUN pip install pipenv
RUN mkdir /workspace
WORKDIR /workspace