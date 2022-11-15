FROM python:3.8.12

ENV APP_DIR=/home/feast_gcp \
    POETRY_VERSION=1.1.12

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR $APP_DIR
COPY ./poetry.lock poetry.lock
COPY ./pyproject.toml pyproject.toml

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi --no-root

COPY ./main.py $APP_DIR
COPY . $APP_DIR

EXPOSE 8080

ENTRYPOINT [ "uvicorn", "main:app", "--host=0.0.0.0", "--port=8080" ]
