pkgname=ubm-dots
pkgver=0.0.4
pkgrel=2
pkgdesc="Personal dotfiles for Arch + Hyprland"
arch=('any')
url="https://github.com/Deeerain/ubm-dots"
makedepends=('git')
depends=(
  'hyprland>=0.53.0'
  'awww-git'
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
  'ttf-jetbrains-mono-nerd'
  'yay'
  'base-devel')
optgepends=(
  'catppuccin-gtk-theme-frappe: Gtk theme (AUR)'
  'gdm: Gnome Display Manager'
  'cassette: Yandex Music Clinet (AUR)')
source=("git+https://github.com/deeerain/ubm-dots.git#tag=v$pkgver-$pkgrel")
sha256sums=('SKIP')

package() {
  cd "$srcdir/$pkgname"

  local install_dir="$pkgdir/usr/share/$pkgname"
  mkdir -p "$pkgdir/usr/bin"

  install -dm755 "$install_dir/.config/hypr"
  install -dm755 "$install_dir/.config/waybar"
  install -dm755 "$install_dir/.config/wofi"
  install -dm755 "$install_dir/.config/mako"
  install -dm755 "$install_dir/.config/fastfetch"
  install -dm755 "$install_dir/.config/kitty"

  cp -r dots/hypr "$install_dir/.config"
  cp -r dots/waybar "$install_dir/.config"
  cp -r dots/wofi "$install_dir/.config"
  cp -r dots/mako "$install_dir/.config"
  cp -r dots/fastfetch "$install_dir/.config"
  cp -r dots/kitty "$install_dir/.config"
  cp -r ubm-dots.py "$install_dir/ubm-dots.py"

  ln -sf /usr/share/ubm-dots/ubm-dots.py "$pkgdir/usr/bin/ubm-dots"
}
