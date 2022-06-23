FROM python:3.10-slim-buster
WORKDIR /code
RUN pip install poetry
COPY . .
RUN poetry config virtualenvs.create false
RUN poetry install
EXPOSE 8090
WORKDIR /code/app
ENTRYPOINT ["poetry", "run", "python", "run.py"]