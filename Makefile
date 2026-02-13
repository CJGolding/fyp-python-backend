SHELL := /bin/bash
folder_name = fyp-python-backend
docker_image_name = $(folder_name)
docker_container_name = $(folder_name)-container

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
	. .venv/bin/activate && pylint --max-line-length=120 --fail-under=8 \
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

.PHONY: docker-clean
docker-clean:
	-docker stop $(docker_container_name) 2>/dev/null || true
	-docker rm $(docker_container_name) 2>/dev/null || true
	-docker rmi $(docker_image_name) 2>/dev/null || true

.PHONY: docker-build
docker-build:
	docker build -t $(docker_image_name) .

.PHONY: docker-run
docker-run: docker-clean docker-build
	docker run -d -p 8000:8000 --name $(docker_container_name) $(docker_image_name)
	@echo "Docker container '$(docker_container_name)' is running on http://localhost:8000"
	@echo "View logs with: docker logs -f $(docker_container_name)"
	@echo "Stop with: docker stop $(docker_container_name)"

