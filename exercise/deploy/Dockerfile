FROM python:3.7-slim

RUN pip install -U numpy xgboost seldon-core

WORKDIR /app

COPY . /app

EXPOSE 5000

# Define environment variable
ENV MODEL_NAME Deploy
ENV API_TYPE REST
ENV SERVICE_TYPE MODEL
ENV PERSISTENCE 0

CMD exec seldon-core-microservice $MODEL_NAME $API_TYPE --service-type $SERVICE_TYPE --persistence $PERSISTENCE