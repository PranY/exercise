FROM python:3.7-slim

RUN pip install -U scikit-learn numpy

WORKDIR /app

COPY test.py ./test.py

ENTRYPOINT [ "python", "test.py" ]