#!/bin/sh
git pull
docker build . -t celery_app
docker-compose down
docker-compose up -d
