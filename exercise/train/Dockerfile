FROM python:3.7-slim

RUN pip install -U scikit-learn numpy

WORKDIR /app

COPY train.py ./train.py

ENTRYPOINT [ "python", "train.py" ]