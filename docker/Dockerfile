FROM debian:bookworm AS base
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get install -y python3 python3-pip curl python3-dateutil bash python3-venv
ADD requirements.txt /tmp/requirements.txt
RUN install -d /opt/python /opt/client /opt/client/certs /opt/client/config
WORKDIR /opt/client
RUN install -d /opt/python/ && chown -R www-data:www-data /opt/python/
USER www-data
RUN python3 -m venv /opt/python
RUN /opt/python/bin/pip3 install --upgrade pip
RUN /opt/python/bin/pip3 install -r /tmp/requirements.txt
ENV PATH="/opt/python/bin/:$PATH"

#------------------------------------


FROM base AS dev
ENV APP_ENV=dev


FROM base as prod
ENV APP_ENV=prod
ADD ./24dev-client.py /opt/client
ADD ./libs /opt/client/libs
