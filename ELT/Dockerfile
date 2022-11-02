FROM ubuntu:18.04
LABEL Matilde Pato (matilde.pato@gmail.com)


# --------------------------------------------------------------
#                         GENERAL SET UP
# --------------------------------------------------------------

RUN apt-get update -y \
  && apt-get install wget -y \
  && apt-get install curl -y \
  && apt-get install nano -y

# --------------------------------------------------------------
#               PYTHON LIBRARIES AND CONFIGURATION
# --------------------------------------------------------------
RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip \
  && apt-get install -y \
    ssh \
    git \
    && apt-get autoremove \
    && apt-get autoclean


#RUN python -m textblob.download_corpora
COPY requirements.txt .
RUN pip3 install -r requirements.txt

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN python3 -m spacy download xx_ent_wiki_sm
RUN pip3 install https://github.com/explosion/spacy-models/releases/download/xx_ent_wiki_sm-3.1.0/xx_ent_wiki_sm-3.1.0.tar.gz#egg=xx_ent_wiki_sm --user

RUN mkdir /data/
VOLUME /data/
