FROM python:3.14-slim

WORKDIR /app

ENV POETRY_VIRTUALENVS_CREATE=false \
    PIP_NO_CACHE_DIR=1

RUN pip install poetry==2.4.1

COPY ./pyproject.toml ./poetry.lock /app/

RUN poetry install --no-root --without dev

COPY . /app

CMD ["/app/start.sh"]