#!/bin/bash
set -e

pip install -e .

if [ "$1" = 'distribute' ]; then
  rm -rf dist
  python setup.py sdist
  TWINE_USERNAME="$(readsecret TWINE_USERNAME)" \
  TWINE_PASSWORD="$(readsecret TWINE_PASSWORD)" \
  twine upload dist/*
  exit 0
fi

exec "$@"
