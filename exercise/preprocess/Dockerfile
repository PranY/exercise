FROM python:3.7-slim

RUN pip install -U scikit-learn numpy

WORKDIR /app

RUN mkdir -p /app/data

COPY . /app

COPY data/* /app/data/

ENTRYPOINT [ "python", "preprocess.py" ]