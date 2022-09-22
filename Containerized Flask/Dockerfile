FROM python:3.9.13

WORKDIR /flask_app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY main.py .
# нужно так же скопировать deserialization.py, если он есть
# COPY deserialization.py .
COPY migrations/ ./migrations/

ENV FLASK_APP main.py
