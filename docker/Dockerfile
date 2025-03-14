FROM debian:bookworm-slim AS base
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get install -y python3 curl python3-dateutil bash python3-certifi\
     python3-cffi python3-charset-normalizer python3-cryptography python3-pycparser python3-yaml python3-requests python3-urllib3
ADD requirements.txt /tmp/requirements.txt
RUN install -d /opt/python /opt/client /opt/client/certs /opt/client/config
WORKDIR /opt/client
RUN install -d /opt/python/ && chown -R www-data:www-data /opt/python/
RUN apt clean && apt autoremove --purge
RUN whereis python3
USER www-data


FROM base AS dev
ENV APP_ENV=dev


FROM base as prod
ENV APP_ENV=prod
ADD ./24dev-client.py /opt/client
ADD ./libs /opt/client/libs
