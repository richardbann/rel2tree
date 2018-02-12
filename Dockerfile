FROM python:3-slim

RUN pip install --no-cache \
  coverage==4.4.2 \
  twine==1.9.1

ENV PYTHONUNBUFFERED 1
