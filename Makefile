PKGBUILD_LOCAL = PKGBUILD.local

clear:
	rm -rf ./pkg
	rm -rf ./src
	rm -rf ./ubm-dots
	rm -rf $(PKGBUILD_LOCAL)
	rm -rf ./*.zst

generate_local:
	cp ./PKGBUILD ./PKGBUILD.local
	sed -i 's|^source=.*|source=("git+file:///$(PWD)#branch=dev")|' $(PKGBUILD_LOCAL)

build: generate_local
	makepkg -isp $(PKGBUILD_LOCAL)

install: build clear

uninstall:
	yay -Rns ubm-dots
