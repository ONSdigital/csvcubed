FROM debian:latest

RUN apt-get update

# install pyenv with appropriate python versions
RUN apt-get install -y make build-essential libssl-dev zlib1g-dev \
  libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
  libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
RUN apt-get install -y git python3 python3-pip

RUN curl https://pyenv.run | bash

RUN /root/.pyenv/bin/pyenv install 3.9.7
RUN /root/.pyenv/bin/pyenv install 3.10.0
RUN /root/.pyenv/bin/pyenv global 3.9.7 3.10.0

# install docker stuff
RUN apt-get install -y \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg \
  lsb-release

RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

RUN apt-get update

RUN apt-get install -y docker-ce docker-ce-cli containerd.io

RUN python3 -m pip install poetry

ADD https://raw.githubusercontent.com/GSS-Cogs/gss-utils/master/cucumber-format.patch /

# Pyright (nodejs)
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
RUN apt-get install -y nodejs
RUN npm install -g pyright
RUN python3 -m pip install tox

RUN mkdir /workspace
WORKDIR /workspace
ENV PATH="~/.pyenv/bin:~/.pyenv/shims:${PATH}"
