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
 install -D -m644 data/grub/01_pyakm_template "$pkgdir"/usr/share/pyakm/data/grub/01_pyakm_template 
 install -D -m644 data/ui/manager.ui "$pkgdir"/usr/share/pyakm/ui/manager.ui 
 install -D -m644 data/dbus/com.github.pyakm.system.conf "$pkgdir"/etc/dbus-1/system.d/com.github.pyakm.system.conf
 install -D -m644 data/polkit/com.github.pyakm.policy "$pkgdir"/usr/share/polkit-1/actions/com.github.pyakm.policy
 install -D -m644 data/systemd/pyakm-system.service "$pkgdir"/usr/lib/systemd/system/pyakm-system.service
}
