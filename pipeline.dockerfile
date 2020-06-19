FROM python:3.8

RUN pip install poetry

COPY pyproject.toml /tmp/install/pyproject.toml
COPY poetry.lock /tmp/install/poetry.lock

RUN poetry config virtualenvs.create false
RUN cd /tmp/install/ && poetry install --no-root

COPY lazy_ticker /app/lazy_ticker
COPY main_pipeline.py /app/main_pipeline.py
COPY luigi_client.cfg /etc/luigi/luigi.cfg

ENTRYPOINT ["python3", "/app/main_pipeline.py"]
