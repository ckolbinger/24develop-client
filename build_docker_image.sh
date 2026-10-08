#!/usr/bin/env bash
set -e

image=24developcom/24develop-client
version=$(date +"%Y%m%d%H%M")
docker build -t ${image}:${version} -t ${image}:latest -f docker/Dockerfile .
# docker compose push only pushes the untagged compose image (latest), push both tags
docker push ${image}:${version}
docker push ${image}:latest
