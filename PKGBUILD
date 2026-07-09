pkgname=ubm-dots
pkgver=0.1.1
pkgrel=1
pkgdesc="Personal dotfiles for Arch + Hyprland"
arch=('any')
url="https://github.com/Deeerain/ubm-dots"
makedepends=('git')
depends=(
  'fish'
  'hyprland>=0.53.0'
  'awww'
  'hyprlock'
  'mako'
  'btop'
  'git'
  'grim'
  'slurp'
  'waybar'
  'exa'
  'nwg-look'
  'kitty'
  'python>=3.14'
  'python-typer>=0.21.1'
  'ttf-nerd-fonts-symbols'
  'base-devel')
optdepends=(
  'catppuccin-gtk-theme-frappe: Gtk theme (AUR)'
  'gdm: Gnome Display Manager'
  'cassette: Yandex Music Clinet (AUR)')
source=("git+https://github.com/deeerain/ubm-dots.git#tag=v$pkgver-$pkgrel")

package() {
  cd "$srcdir/$pkgname"

  local install_dir="$pkgdir/usr/share/$pkgname"
  mkdir -p "$pkgdir/usr/bin"

  for dir in ./dots/*; do
    dots_install_dir=$install_dir/${dir#.}
    install -dm755 "$dots_install_dir"
    cp -r $dir/* $dots_install_dir
  done

  cp ubm-dots.py "$pkgdir/usr/share/$pkgname"
  ln -sf /usr/share/ubm-dots/ubm-dots.py "$pkgdir/usr/bin/ubm-dots"
}

sha256sums=('SKIP')
