FROM python:3.12.1-slim
WORKDIR /app

ARG ENV_TYPE
ARG UID

ARG NODE_VERSION=18.18.2
ARG NODE_PACKAGE=node-v$NODE_VERSION-linux-x64
ARG NODE_HOME=/opt/$NODE_PACKAGE
ENV NODE_PATH="$NODE_HOME/lib/node_modules" \
    POETRY_HOME="/opt/poetry"

ENV PATH="$NODE_HOME/bin:$POETRY_HOME/bin:$PATH"

RUN apt-get update --fix-missing -y && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    # install Node and Poetry
    && curl https://nodejs.org/dist/v$NODE_VERSION/$NODE_PACKAGE.tar.gz | tar -xzC /opt/ \
    && curl -sSL https://install.python-poetry.org | python3 -

COPY package.json package-lock.jso[n] ./
COPY pyproject.toml poetry.loc[k] ./

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1 \
    # enable installing dependencies into the system's python environment
    # POETRY_VIRTUALENVS_CREATE=false
    POETRY_VIRTUALENVS_PATH=/.globals/poetry


RUN if [ "$ENV_TYPE" = "dev" ]; then \
	apt-get update -y \
        && apt-get install git -y \
    ;fi

RUN adduser -u ${UID} --disabled-password --gecos "" appuser && chown -R appuser /app \
    && mkdir -p $POETRY_VIRTUALENVS_PATH && chown -R appuser $POETRY_VIRTUALENVS_PATH

USER appuser

# install dependencies
RUN if [ "$ENV_TYPE" = "dev" ]; then \
        poetry install --no-root \
        && npm i \
    ;elif [ "$ENV_TYPE" = "prod" ]; then \
        poetry install --without dev --no-root \
        && npm ci \
    ;fi
