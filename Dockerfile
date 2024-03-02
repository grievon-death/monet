FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install --no-install-recommends -y gcc && \
    apt-get install make
RUN apt-get install -y python3.10
RUN apt-get update && apt-get install -y python3-pip

RUN mkdir /app
WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt
