#!/bin/sh
UPDATE=$(~/git/docker/check_update.sh python:3.6.6)
if [ $UPDATE = 1 ]; then
  docker build . -t celery_app
  docker-compose down
  git pull
  #docker-compose pull
  docker-compose up -d
else
  echo Nothing to update
fi
