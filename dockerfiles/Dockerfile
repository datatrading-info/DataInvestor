# BUILD:  docker build -t datainvestor-ubuntu .
# RUN:    docker run -it -v "$PWD":/datainvestor-data datainvestor-ubuntu

FROM ubuntu:latest

RUN apt-get update && apt-get install -y git python3-pip
RUN git clone https://github.com/datatrading-info/DataInvestor.git
RUN pip3 install -r datainvestor/requirements/base.txt
RUN pip3 install -r datainvestor/requirements/tests.txt
WORKDIR /datainvestor
ENV PYTHONPATH /datainvestor
RUN pytest
