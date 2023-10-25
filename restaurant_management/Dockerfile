FROM python:3.10-slim as build
WORKDIR /restaurant_management
ADD requirements.txt /restaurant_management
RUN pip install --no-cache-dir -r requirements.txt
ADD . /restaurant_management
CMD uvicorn app.main:app --host 0.0.0.0 --port 9000