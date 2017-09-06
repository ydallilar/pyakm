#!/usr/bin/env python

from distutils.core import setup

setup(name='pyakm',
      version='0.1',
      description='Antergos Kernel Manager in Python',
      author='Yigit Dallilar',
      author_email='yigit.dallilar@gmail.com',
      packages=['pyakm'],
      package_dir={'pyakm': 'src/pyakm'},
      scripts=['scripts/pyakm-status', 'scripts/pyakm-install-latest',
               'scripts/pyakm-remove-kernel',
               'scripts/pyakm-downgrade-kernel']
     )
