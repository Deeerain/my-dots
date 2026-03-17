PKGBUILD_LOCAL = PKGBUILD

clear:
	rm -rf ./pkg
	rm -rf ./src
	rm -rf ./ubm-dots
	mv "$(PKGBUILD_LOCAL).back" $(PKGBUILD_LOCAL)
	rm -rf ./*.zst

generate_local:
	sed -i.back 's|^source=.*|source=("git+file:///$(PWD)#branch=dev")|' $(PKGBUILD_LOCAL)

build: generate_local
	makepkg -isp $(PKGBUILD_LOCAL)

install: build clear

uninstall:
	yay -Rns ubm-dots
