FROM ubuntu:20.04

RUN apt-get -y update
RUN apt-get -y upgrade

RUN apt-get install -y wget 
RUN apt-get install -y curl 
RUN apt-get install -y nano 
RUN apt-get install -y locales 
RUN apt-get install -y git 
# RUN apt-get install -y ssh 
RUN apt-get -y autoremove
RUN apt-get -y clean

# Python setup

RUN apt-get install -y python3-pip python3-dev
RUN cd /usr/local/bin
RUN ln -s /usr/bin/python3 python
RUN pip3 install --upgrade pip
RUN apt-get install -y sqlite3
RUN apt-get install -y libsqlite3-dev
RUN apt-get install -y gawk

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1
RUN update-alternatives --config python

# Requirements
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Ontologies
RUN mkdir /data
RUN mkdir /data/ontologies
VOLUME /data
VOLUME /data/ontologies/

WORKDIR /data/ontologies/
ADD http://purl.obolibrary.org/obo/chebi/chebi_lite.owl /data/ontologies/
ADD http://purl.obolibrary.org/obo/doid.owl /data/ontologies/

WORKDIR /data/blacklists/
VOLUME /data/blacklists/

RUN mkdir /KB
VOLUME /KB
WORKDIR /