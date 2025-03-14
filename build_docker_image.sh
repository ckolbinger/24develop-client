#!/usr/bin/env bash

version=$(date +"%Y%m%d%H%M")
docker build -t 24developcom/24develop-client:${version} -t 24developcom/24develop-client:latest -f docker/Dockerfile .
docker compose push