FROM python:3.8-slim-buster

WORKDIR .

COPY . .

RUN pip install -U pipenv

RUN pipenv install --system --deploy

ENTRYPOINT ["python3"]
CMD ["-m", "shorturl"]