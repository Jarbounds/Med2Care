FROM ubuntu:kinetic
LABEL Matilde Pato (matilde.pato@gmail.com)
LABEL Renato Marcelo (renato.marcelo99@gmail.com)

WORKDIR /
# --------------------------------------------------------------
#                         GENERAL SET UP
# --------------------------------------------------------------

RUN apt-get update -y \
  && apt-get install wget -y \
  #&& apt-get install curl -y \
  #&& apt-get install nano -y \
  && apt-get -y install locales \
  && apt-get -y install git \
  && apt-get -y install ssh \ 
  && apt-get -y autoremove \
  && apt-get -y clean 

# --------------------------------------------------------------
#               PYTHON LIBRARIES AND CONFIGURATION
# --------------------------------------------------------------

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip \
  && apt-get install -y \
    sqlite3 \
    libsqlite3-dev 
     

# --------------------------------------------------------------
#                  COPY REPOSITORY DIRECTORIES
# --------------------------------------------------------------

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

ENV LC_ALL=C.UTF-8 
ENV LANG=C.UTF-8

RUN python3 -m spacy download xx_ent_wiki_sm
RUN pip3 install https://github.com/explosion/spacy-models/releases/download/xx_ent_wiki_sm-3.1.0/xx_ent_wiki_sm-3.1.0.tar.gz#egg=xx_ent_wiki_sm --user

# --------------------------------------------------------------
#                             Ontologies
# --------------------------------------------------------------

VOLUME /data/ontologies/

#WORKDIR /data/ontologies/
ADD http://purl.obolibrary.org/obo/chebi/chebi_lite.owl /data/ontologies/
#ftp://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi_lite.owl
ADD http://purl.obolibrary.org/obo/doid.owl /data/ontologies/
# https://raw.githubusercontent.com/DiseaseOntology/HumanDiseaseOntology/master/src/ontology/doid.owl

WORKDIR /data/blacklists/
VOLUME /data/blacklists/

# --------------------------------------------------------------
#                             Other
# --------------------------------------------------------------

RUN mkdir /RS
VOLUME /RS

WORKDIR /