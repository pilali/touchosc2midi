FROM python:3.11-slim

RUN apt-get update &&\
    apt-get install -y --no-install-recommends \
        gcc \
        liblo-dev \
        librtmidi-dev &&\
    rm -rf /var/lib/apt/lists/*

COPY . /src
RUN pip install --no-cache-dir /src

ENTRYPOINT ["touchosc2midi"]
