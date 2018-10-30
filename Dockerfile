FROM ubuntu:bionic-20181018

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update

RUN apt-get install -y locales
RUN localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.utf8

RUN apt-get install -y python3.6 python3-venv
RUN python3.6 -m venv /python
ENV PATH /python/bin:$PATH
ENV PYTHONPATH /src/python_packages/:/src/frontend/
ENV PYTHONUNBUFFERED 1
RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir coverage
RUN pip install --no-cache-dir sphinx
RUN pip install --no-cache-dir sphinx_rtd_theme
RUN pip install --no-cache-dir twine
RUN pip install --no-cache-dir gdockutils==0.5.1

WORKDIR /src

ENTRYPOINT ["/src/entrypoint.sh"]
