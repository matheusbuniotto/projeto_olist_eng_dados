FROM python:3.9-slim-buster
VOLUME [ "/data" ]
WORKDIR /data 


RUN apt-get update 
RUN apt-get install wget -qqq
RUN apt-get install unzip

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./scripts/pull_and_unzip.sh .
