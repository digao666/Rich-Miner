FROM ubuntu:18.04
LABEL maintainer="dgao12@my.bcit.ca"
RUN apt-get update -y && \
apt-get install -y python3 python3-pip
WORKDIR /app
COPY . /app
RUN npm install
RUN npm start
