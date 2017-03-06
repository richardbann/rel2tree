#!/bin/bash

set -e

docker-compose run --rm py2 python -m unittest discover
docker-compose run --rm py3 coverage erase
docker-compose run --rm py3 coverage run -m unittest discover
docker-compose run --rm py3 coverage report -m
