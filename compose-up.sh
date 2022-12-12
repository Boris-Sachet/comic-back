#/bin/bash
docker-compose -f ./docker/docker-compose.yml --env-file ./docker/.env build --pull
docker-compose -f ./docker/docker-compose.yml --env-file ./docker/.env up -d