FROM python:3.10-slim as build
WORKDIR /food_ordering
ADD requirements.txt /food_ordering
RUN pip install --no-cache-dir -r requirements.txt
ADD . /food_ordering
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT