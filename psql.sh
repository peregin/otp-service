#!/usr/bin/env bash

CONTAINER_REPO="otp_repo"
if [[ $(docker inspect -f '{{.State.Running}}' $CONTAINER_REPO) = "true" ]]; then
  echo "$CONTAINER_REPO is already running ..."
else
  echo home directory is "$HOME"
  docker run -d -p 5490:5432 \
    --rm --name $CONTAINER_REPO \
    --health-cmd='stat /etc/passwd || exit 1' \
    --health-interval=30s \
    -e POSTGRES_DB=otp \
    -e POSTGRES_USER=otp \
    -e POSTGRES_PASSWORD=otp \
    -v "$HOME"/Downloads/psql/otp/data16:/var/lib/postgresql/data \
    postgres:16.4-alpine
  echo "$CONTAINER_REPO has been started ..."
fi
