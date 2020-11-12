help:
	@echo  "usage: make <target>"
	@echo  "Targets:"
	@echo  "    up          Updates dev/test dependencies"
	@echo  "    deps        Ensure dev/test dependencies are installed"
	@echo  "    run         Runs in development mode"

up:
	CUSTOM_COMPILE_COMMAND="make up" pip-compile -U --no-index --no-emit-trusted-host requirements.in
	CUSTOM_COMPILE_COMMAND="make up" pip-compile -U --no-index --no-emit-trusted-host tests/requirements.in

deps:
	@pip install --upgrade pip
	@pip install -q pip-tools
	@pip-sync requirements.txt tests/requirements.txt
	@pip install --no-cache-dir -qe  .

build:
	docker build -t python/auth_service -f Dockerfile .

run:
	docker run -d -p 8575:8575 python/auth_service
	# docker run -d -p 8575:8575 --name=auth_service python/auth_service
