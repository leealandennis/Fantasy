FROM python:3.9

ENV TZ America/Montreal

RUN pip install "poetry==1.1.2"

WORKDIR /fantasy

COPY poetry.lock pyproject.toml /fantasy/

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi