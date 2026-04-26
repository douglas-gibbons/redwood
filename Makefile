
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


.PHONY: package-linux
.ONESHELL:
package-linux:           ## build the Linux package
	# Linux
	flet build linux

	if [ ! -f appimagetool-x86_64.AppImage ]; then	
		wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
		chmod +x appimagetool-x86_64.AppImage
	fi
	mkdir -p build/Redwood.AppDir/usr/bin
	mkdir -p build/Redwood.AppDir/usr/share/applications
	mkdir -p build/Redwood.AppDir/usr/share/icons/hicolor/256x256/apps

	# cp build/linux/redwood build/Redwood.AppDir/AppRun
	cp src/assets/icon_256x256.png build/Redwood.AppDir/redwood.png
	cp redwood.desktop build/Redwood.AppDir/
	cp -r build/linux/* build/Redwood.AppDir/usr/.
	ln -sf usr/redwood build/Redwood.AppDir/AppRun
	./appimagetool-x86_64.AppImage build/Redwood.AppDir build/Redwood.AppImage

.PHONY: package-macos
.ONESHELL:
package-macos:           ## build the macos package.

	flet build macos
	