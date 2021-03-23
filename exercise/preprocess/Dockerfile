FROM python:3.7-slim

RUN pip install -U scikit-learn numpy

WORKDIR /app

COPY preprocess.py ./preprocess.py

ENTRYPOINT [ "python", "preprocess.py" ]