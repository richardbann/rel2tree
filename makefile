SHELL=/bin/bash

usr := $(shell id -u):$(shell id -g)
img := richardbann/rel2tree

################################################################################
# self documenting makefile
################################################################################
.DEFAULT_GOAL := help
.PHONY: help
help: bold = $(shell tput bold; tput setaf 3)
help: reset = $(shell tput sgr0)
help:
	@echo
	@sed -nr \
		-e '/^## /{s/^## /    /;h;:a;n;/^## /{s/^## /    /;H;ba};' \
		-e '/^[[:alnum:]_\-]+:/ {s/(.+):.*$$/$(bold)\1$(reset):/;G;p};' \
		-e 's/^[[:alnum:]_\-]+://;x}' ${MAKEFILE_LIST}
	@echo
################################################################################
.PHONY: build
## Build the docker container
build:
	docker build -t $(img) .
################################################################################
.PHONY: test
## Run tests
test:
	docker run --rm -i -u $(usr) \
		-v "$(CURDIR):/project" \
		-e "PYTHONPATH=/project" \
		-w "/project" \
		$(img) coverage run -m unittest discover
	docker run --rm -u $(usr) \
		-v "$(CURDIR):/project" \
		-w "/project" \
		$(img) coverage html
################################################################################
.PHONY: deploy
## deploy to pypi
deploy:
	-rm -rf dist
	docker run --rm -i -u $(usr) \
		-v "$(CURDIR):/project" \
		-w "/project" \
		$(img) python3 setup.py sdist
	docker run --rm -i -t -u $(usr) \
		-v "$(CURDIR):/project" \
		-w "/project" \
		$(img) twine upload dist/*
