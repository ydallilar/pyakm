#!/usr/bin/env python

import os
import subprocess
from distutils.cmd import Command
from distutils.core import Extension, setup

os.putenv('LC_CTYPE', 'en_US.UTF-8')

pyalpm_version = '0.8'

cflags = ['-Wall', '-Wextra',
    '-Wno-unused-parameter',
    '-std=c99', '-D_FILE_OFFSET_BITS=64']

alpm = Extension('pyakm.pyalpm',
    libraries = ['alpm'],
    extra_compile_args = cflags + ['-DVERSION="%s"' % pyalpm_version],
    language = 'C',
    sources = [
        'pyalpm/src/pyalpm.c',
        'pyalpm/src/util.c',
        'pyalpm/src/package.c',
        'pyalpm/src/db.c',
        'pyalpm/src/options.c',
        'pyalpm/src/handle.c',
        'pyalpm/src/transaction.c'
        ],
    depends = [
        'pyalpm/src/handle.h',
        'pyalpm/src/db.h',
        'pyalpm/src/options.h',
        'pyalpm/src/package.h',
        'pyalpm/src/pyalpm.h',
        'pyalpm/src/util.h',
        ])



setup(name='pyakm',
    version='0.0.2',
    description='Simple GUI for managing Arch linux kernels (pre-release)',
    author='Yigit Dallilar',
    author_email='yigit.dallilar@gmail.com',
    packages=['pyakm'],
    package_dir={'pyakm': 'src/pyakm'},
    ext_modules = [alpm],
    scripts=['scripts/pyakm-manager', 'scripts/pyakm-system-daemon']
)
