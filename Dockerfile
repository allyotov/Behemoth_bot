FROM python:3.9.7-slim-bullseye

WORKDIR /behemoth_bot

COPY pyproject.toml poetry.lock /behemoth_bot/

RUN pip install --upgrade pip && \
    pip install "poetry==1.1.0" && poetry config virtualenvs.create false && poetry install

COPY bot /behemoth_bot/bot/

CMD ["python", "-m", "bot"]