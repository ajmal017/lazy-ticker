FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

RUN pip install poetry

COPY pyproject.toml /tmp/install/pyproject.toml
COPY poetry.lock /tmp/install/poetry.lock

RUN poetry config virtualenvs.create false
RUN cd /tmp/install/ && poetry install

COPY lazy_ticker /app/lazy_ticker
COPY main.py /app/main.py
