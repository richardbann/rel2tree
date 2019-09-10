export PYTHONWARNINGS=default
SHELL=/bin/bash
version := $(shell sed -rn "s/^VERSION = \"(.*)\"$$/\1/p" setup.py)


.PHONY: init
init:
	python3.6 -m venv .venv
	.venv/bin/pip install --no-cache-dir --upgrade pip
	.venv/bin/pip install --no-cache-dir -e .[dev]

.PHONY: test
test:
	.venv/bin/coverage run -m unittest
	.venv/bin/coverage report
	.venv/bin/coverage html

.PHONY: distribute
distribute:
	mkdir -p dist
	rm -f dist/*
	.venv/bin/python setup.py sdist
	.venv/bin/twine upload dist/*
	git tag $(version)
	git push --tags
