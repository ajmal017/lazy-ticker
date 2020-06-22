FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

RUN pip install poetry

COPY pyproject.toml /tmp/install/pyproject.toml
COPY poetry.lock /tmp/install/poetry.lock

RUN poetry config virtualenvs.create false
RUN cd /tmp/install/ && poetry install --no-root

COPY lazy_ticker /app/lazy_ticker
COPY static /app/static
COPY templates /app/templates

COPY frontend.py /app/frontend.py

ENV MODULE_NAME=frontend
