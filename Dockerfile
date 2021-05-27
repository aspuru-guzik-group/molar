FROM python:3.7-slim

LABEL maintainer="Ian Benlolo <ian.benlolo@gmail.com> Theophile Gaudin <tgaudin@cs.toronto.edu>"

RUN pip install --upgrade pip && \
    pip install molar[backend]

COPY entrypoint.sh .
ENTRYPOINT ["/entrypoint.sh"]
