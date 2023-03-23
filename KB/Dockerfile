FROM ubuntu:18.04
LABEL Matilde Pato (matilde.pato@gmail.com)

WORKDIR /

#format changes required for asammdf v3.4.0
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

ENV PYTHON_VERSION=3.11.0a1
# --------------------------------------------------------------
#                         GENERAL SET UP
# --------------------------------------------------------------

RUN apt-get -y update \
  && apt-get install -y wget \
  #&& apt-get install -y curl \
  #&& apt-get install -y nano \
  #&& apt-get -y install locales \
  && apt-get -y install git \
  && apt-get -y install ssh \ 
  && apt-get -y autoremove \
  && apt-get -y clean 

# --------------------------------------------------------------
#               PYTHON LIBRARIES AND CONFIGURATION
# --------------------------------------------------------------

RUN apt-get update \
  && apt-get install -y python3 \
    python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip \
  && apt-get install -y \
    apt-utils \
    sqlite3 \
    libsqlite3-dev \
    gawk 

RUN alias python3=/usr/bin/python3.11

#RUN apt-get -y install python-rdkit librdkit1 rdkit-data rdkit-doc

#RUN locale-gen en_US.UTF-8
#COPY ./default_locale /etc/default/locale
#RUN chmod 0755 /etc/default/locale

# --------------------------------------------------------------
#                  COPY REPOSITORY DIRECTORIES
# --------------------------------------------------------------

#ENV LC_ALL=en_US.UTF-8
#ENV LANG=en_US.UTF-8
#ENV LANGUAGE=en_US.UTF-8

COPY requirements.txt .
RUN pip3 install -r requirements.txt

# --------------------------------------------------------------
#                             Ontologies
# --------------------------------------------------------------
RUN mkdir /data
RUN mkdir /data/ontologies
VOLUME /data
VOLUME /data/ontologies/

WORKDIR /data/ontologies/
ADD http://purl.obolibrary.org/obo/chebi/chebi_lite.owl /data/ontologies/
ADD http://purl.obolibrary.org/obo/doid.owl /data/ontologies/
# ---- OR ----
# RUN wget -q http://purl.obolibrary.org/obo/chebi/chebi_lite.owl 
#ftp://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi_lite.owl
# RUN wget -q http://purl.obolibrary.org/obo/doid.owl 
# https://raw.githubusercontent.com/DiseaseOntology/HumanDiseaseOntology/master/src/ontology/doid.owl


WORKDIR /data/blacklists/
VOLUME /data/blacklists/

# --------------------------------------------------------------
#                             Other
# --------------------------------------------------------------

RUN mkdir /KB
VOLUME /KB
WORKDIR /