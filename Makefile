
.PHONY: help
help:              ## show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

.PHONY: test
.ONESHELL:
test:              ## run the test suite.
	PYTHONPATH=. uv run pytest

.PHONY: cli
.ONESHELL:
cli:               ## run the cli
	uv run cli

.PHONY: server
server:            ## run the server. You can also run server.sh
	uv run server
