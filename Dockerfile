FROM python:3.9

# Installing packages required by docker.
# To prevent any cache related issues that could occur when building the container and during apt-get install, the apt-get update and apt-get install are added to the same RUN statement 
# as per the instructions in https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#run.
RUN apt-get update && apt-get install -y \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg \
  lsb-release

RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# To prevent any cache related issues that could occur when building the container and during apt-get install, the apt-get update and apt-get install are added to the same RUN statement 
# as per the instructions in https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#run.
RUN apt-get update && apt-get install -y docker-ce docker-ce-cli containerd.io

RUN python3 -m pip install poetry

ADD https://raw.githubusercontent.com/GSS-Cogs/gss-utils/master/cucumber-format.patch /

RUN apt-get install -y git 

# Pyright (nodejs)
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
RUN apt-get install -y nodejs
RUN npm install -g pyright

RUN python3 -m pip install mkdocs mkdocs-material mkdocs-mermaid2-plugin

RUN mkdir /workspace
WORKDIR /workspace
