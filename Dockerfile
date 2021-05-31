FROM python:3.7-slim

LABEL maintainer="Ian Benlolo <ian.benlolo@gmail.com> Theophile Gaudin <tgaudin@cs.toronto.edu>"

RUN apt-get update && \
    apt-get install -y postgresql-client wget && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && \
    pip install molar[backend]

COPY entrypoint.sh .
ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
