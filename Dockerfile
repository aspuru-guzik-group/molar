# syntax=docker/dockerfile:1.0.0-experimental
FROM python:3.7-slim

LABEL maintainer="Ian Benlolo <ian.benlolo@gmail.com> Theophile Gaudin <tgaudin@cs.toronto.edu>"


RUN apt-get update && \
    apt-get install -y postgresql-client wget && \
    rm -rf /var/lib/apt/lists/*

ARG MOLAR_PKG_WHEEL
COPY ${MOLAR_PKG_WHEEL} .

RUN pip install --upgrade pip && \
    pip install $(basename ${MOLAR_PKG_WHEEL})[backend] && \
    rm -fr $(basename ${MOLAR_PKG_WHEEL})

COPY entrypoint.sh .

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
