# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.9

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Configure Working Directory
WORKDIR /workspace
COPY . /workspace/

# Set up pip, poetry, and install dependencies
RUN pip install poetry
RUN cd /workspace/sharedmodels && pip install .
RUN cd /workspace/pmd && poetry export --format requirements.txt --without-hashes | grep -v 'sharedmodels' > requirements.txt
RUN pip install --requirement /workspace/pmd/requirements.txt
RUN pip install --no-deps --use-feature=in-tree-build /workspace/pmd/.