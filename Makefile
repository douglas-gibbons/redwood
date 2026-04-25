
.PHONY: help
help:              ## show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

.PHONY: test
.ONESHELL:
test:              ## run the test suite.
	uv run pytest

.PHONY: cli
.ONESHELL:
cli:               ## run the cli
	uv run cli

.PHONY: gui
.ONESHELL:
gui:                ## run the ui
	uv run gui

.PHONY: server
server:            ## run the server. You can also run server.sh
	uv run server

.PHONY: package
package:           ## build the package.
	flet build linux
