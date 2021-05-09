FROM python:3.9.5-slim-buster

WORKDIR .

COPY . .

RUN pip install -U pipenv

RUN pipenv install --system --deploy

ENTRYPOINT ["python3"]
CMD ["-m", "shorturl"]