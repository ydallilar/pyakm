#!/usr/bin/env python

from distutils.core import setup

setup(name='pyakm',
      version='0.0.2',
      description='Simple GUI for managing Arch linux kernels (pre-release)',
      author='Yigit Dallilar',
      author_email='yigit.dallilar@gmail.com',
      packages=['pyakm'],
      package_dir={'pyakm': 'src/pyakm'},
      scripts=['scripts/pyakm-manager', 'scripts/pyakm-system-daemon']
     )
