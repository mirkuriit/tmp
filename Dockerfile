FROM python:3.14 AS requirements-stage

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry self add poetry-plugin-export && poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.14

WORKDIR /app

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /app

CMD ["uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug" , "--use-colors"]