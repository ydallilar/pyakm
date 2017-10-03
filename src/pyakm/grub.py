#  Copyright © 2017 Yigit Dallilar <yigit.dallilar@gmail.com>
#
#  kernel.py is a part of pyakm. 
#
#  pyakm is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  pyakm is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  The following additional terms are in effect as per Section 7 of the license:
#
#  The preservation of all legal notices and author attributions in
#  the material or in the Appropriate Legal Notices displayed
#  by works containing it is required.
#
#  You should have received a copy of the GNU General Public License
#  along with pyakm; If not, see <http://www.gnu.org/licenses/>.

import sys, os
import subprocess as subp

def read_template():

    f = open('/usr/share/pyakm/data/grub/01_pyakm_template')
    f_str = f.read()
    f.close()

    return f_str

def replace_grub_str(f_str, kernel):

    f_str = f_str.replace('linux-template', kernel)
    
    return f_str

def replace_default_kernel(kernel):

    f_str = read_template()
    f_str = replace_grub_str(f_str, kernel)

    f = open('/etc/grub.d/01_pyakm', 'w')
    f.write(f_str)
    f.close()

    req = subp.Popen(['chmod', '755',
                      '/etc/grub.d/01_pyakm'])

def disable_default_kernel():

    if os.path.isfile('/etc/grub.d/01_pyakm'):
        req = subp.Popen(['chmod', '644',
                          '/etc/grub.d/01_pyakm'])

def update_grub():
    
    req = subp.Popen(['grub-mkconfig', '-o',
                      '/boot/grub/grub.cfg'],
                     stdout=subp.PIPE, stderr=subp.PIPE,
                     close_fds=True)

    for line in iter(req.stderr.readline, b''):
        sys.stdout.write(line.decode('utf-8'))

        

