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
RUN cd /workspace/csvcubed-models && pip install .
RUN cd /workspace/csvcubed-pmd && poetry export --format requirements.txt --without-hashes | grep -v 'csvcubed-models' > requirements.txt
RUN pip install --requirement /workspace/csvcubed-pmd/requirements.txt
RUN pip install --no-deps --use-feature=in-tree-build /workspace/csvcubed-pmd/.