SHELL=/bin/bash
version := $(shell sed -rn "s/^VERSION = '(.*)'$$/\1/p" setup.py)

clean:
	docker-compose run --rm postgres find . -type d -name __pycache__ -exec rm -rf {} +

version:
	@echo $(version)

build:
	docker-compose build

.PHONY: test
test:
	docker-compose run --rm python bash -c "\
		coverage run --branch --source rel2tree -m unittest && \
		coverage report && \
		coverage html \
	"

.PHONY: docs
docs:
	docker-compose run --rm python sphinx-build -b html docs/source docs/build

distribute: build test docs
	docker-compose run --rm python distribute
	git tag $(version)
	git push --tags
