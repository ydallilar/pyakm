_pkgbase=pyakm
pkgbase=pyakm-git
pkgname=('pyakm-git')
pkgver=r2.57ca81a
pkgrel=1
pkgdesc="pyakm"
arch=('x86_64')
#url='http://antergos.com'
license=('GPL3')
depends=('python' 'python-beautifulsoup4')
provides=('pyakm')
source=("git://github.com/pssncp142/pyakm.git")
md5sums=('SKIP')
_gitname=pyakm

pkgver() {
  cd "$_gitname"
  printf "r%s.%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)"
}

prepare() {
  cd "${srcdir}/${_pkgbase}"
}


package() {
 cd "$_gitname"

 python setup.py install --root="$pkgdir/" --optimize=1
 install -D -m644 grub_config/01_pyakm_template /usr/share/pyakm/grub_config/01_pyakm_template
}
