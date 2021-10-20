# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.9

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
WORKDIR /workspace
ADD . /workspace
RUN pip install poetry
RUN poetry export --without-hashes --format requirements.txt > requirements.txt
RUN pip install --requirement requirements.txt
RUN pip install --no-deps . 
