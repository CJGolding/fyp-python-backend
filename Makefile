SHELL := /bin/bash
folder_name =$(shell basename $(shell pwd))

.PHONY: init
init:
	rm -rf ./.venv
	python3 -m venv ./.venv && \
	source .venv/bin/activate

.PHONY: requirements
requirements:
	. .venv/bin/activate && pip install -r requirements.txt

.PHONY: requirements-all
requirements-all: requirements
	. .venv/bin/activate && [ -f ./tests/requirements.txt ] && pip install -r ./tests/requirements.txt

.PHONY: lint
lint:
	. .venv/bin/activate && pip install pylint && pylint --max-line-length=120 --fail-under=8 \
	./backend/*.py \
	./*.py

.PHONY: test
test:
	. .venv/bin/activate && coverage run --omit '.venv/*' -m pytest -o junit_suite_name=$(folder_name) -v tests/ && coverage report -m

.PHONY: run-cli
run-cli:
	. .venv/bin/activate && python3 cli_entrypoint.py

.PHONY: run-fastapi
run-fastapi:
	. .venv/bin/activate && uvicorn fastapi_entrypoint:app
