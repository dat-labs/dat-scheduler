FROM python:3.10
WORKDIR /repo

RUN apt-get update && \
    apt-get install -y cron

COPY pyproject.toml .
RUN pip install poetry

RUN poetry config virtualenvs.create false && poetry lock && poetry install --no-root

RUN crontab -l | { cat; echo "* * * * * /usr/local/bin/python /repo/src/main.py >> /repo/cron.out 2>&1"; } | crontab -

CMD cron -f