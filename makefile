export PYTHONWARNINGS=default
SHELL=/bin/bash


init:
	python3.6 -m venv ./.venv
	./.venv/bin/pip install --no-cache-dir --upgrade pip
	./.venv/bin/pip install --no-cache-dir -e .[dev]

distribute:
	./.venv/bin/python setup.py sdist
