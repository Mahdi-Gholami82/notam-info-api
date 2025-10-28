FROM python:3.13

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y postgresql-client

WORKDIR /app
COPY ./app /app
ADD --chmod=755 ./docker/django-entry.sh /usr/bin/

RUN pip install --no-cache-dir uv
RUN uv sync && uv pip install psycopg[binary]

ENTRYPOINT ["/usr/bin/django-entry.sh"]