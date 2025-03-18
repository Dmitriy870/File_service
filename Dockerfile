FROM python:3.12-slim

WORKDIR /src

COPY pyproject.toml poetry.lock ./

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install  --no-root --no-interaction --no-ansi

COPY src /src

ENV PYTHONPATH "${PYTHONPATH}:/src"

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
