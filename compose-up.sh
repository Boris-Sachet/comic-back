#/bin/bash
docker-compose -f ./docker/docker-compose.yml --env-file ./docker/.env down
docker-compose -f ./docker/docker-compose.yml --env-file ./docker/.env pull comic_back
docker-compose -f ./docker/docker-compose.yml --env-file ./docker/.env up -d
