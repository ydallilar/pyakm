#  Copyright © 2017 Yigit Dallilar <yigit.dallilar@gmail.com>
#
#  dbus.py is a part of pyakm. 
#
#  pyakm is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  Cnchi is distributed in the hope that it will be useful,
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

from pyakm.kernel import OfficialKernel as k
from pyakm.polkit import PolkitAgent

import dbus, threading
import dbus.service
import os, time
import grub

class Server(dbus.service.Object):
 
    def __init__(self):

        self.kernels = []
        #self.update = False
        #self.msg = "Idle"
        self.cntr = 0 
        bus_name = dbus.service.BusName('com.github.pyakm.system',
                                        bus=dbus.SystemBus())
        dbus.service.Object.__init__(self, bus_name, '/com/github/pyakm/system')
        self.busy = False
        self.pagent = None
 
    @dbus.service.signal('com.github.pyakm.system')
    def send_update(self, msg):
        #print(msg)
        pass

    @dbus.service.signal('com.github.pyakm.system')
    def busy_signal(self, busy):
        self.busy = busy
        pass

    @dbus.service.signal('com.github.pyakm.system')
    def refresh_signal(self):
        pass

    @dbus.service.method('com.github.pyakm.system')
    def init_polkit_agent(self, ppid):
        self.pagent = PolkitAgent(ppid, info_func=self.send_update)
    
    @dbus.service.method('com.github.pyakm.system')
    def init_data(self, kernels):
        threading.Thread(target=self.init_data_thr, args=(kernels,)).start()

    def init_data_thr(self, kernels):
        self.busy_signal(True)
        for kernel in kernels:
            self.load_kernel(kernel)
            self.refresh_kernel(kernel)
        self.busy_signal(False)
        self.refresh_signal()
    
    @dbus.service.method('com.github.pyakm.system')
    def load_kernel(self, name):
        global kernels
        if not any(name == kernel.kernel_name for kernel in self.kernels):
            self.kernels.append(k(name))
            print("Loading kernel, ", name)
            self.cntr += 1
            return True
        else:
            print(name, " is already loaded...")
            return False

    @dbus.service.method('com.github.pyakm.system')
    def refresh_kernel(self, name):
        if not any(name == kernel.kernel_name for kernel in self.kernels):
            return False
        else:
            self.refresh_kernel_thr(name)
            return True

    def refresh_kernel_thr(self, name):
        for kernel in self.kernels:
            if name == kernel.kernel_name:
                kernel.Refresh(info_func=self.send_update)
                break

    @dbus.service.method('com.github.pyakm.system')
    def downgrade_kernel(self, name, version):
        if not any(name == kernel.kernel_name for kernel in self.kernels):
            return False
        else:
            for kernel in self.kernels:
                if name == kernel.kernel_name:
                    thr = threading.Thread(target=self.downgrade_kernel_thr, args=(kernel, version))
                    thr.start()
                    break
            return True

    def downgrade_kernel_thr(self, kernel, version):
        if not self.pagent.check_authorization():
            return False
        self.busy_signal(True)
        if kernel.downgradeKernel(version, info_func=self.send_update):
            self.update_grub_thr()
        self.busy_signal(False)
        self.refresh_signal()

    @dbus.service.method('com.github.pyakm.system')
    def upgrade_kernel(self, name):
        if not any(name == kernel.kernel_name for kernel in self.kernels):
            return False
        else:
            for kernel in self.kernels:
                if name == kernel.kernel_name:
                    thr = threading.Thread(target=self.upgrade_kernel_thr, args=(kernel,))
                    thr.start()
                    break
            return True

    def upgrade_kernel_thr(self, kernel):
        if not self.pagent.check_authorization():
            return False
        self.busy_signal(True)
        kernel.upgradeKernel(info_func=self.send_update)
        self.update_grub_thr()
        self.busy_signal(False)
        self.refresh_signal()

    @dbus.service.method('com.github.pyakm.system')
    def remove_kernel(self, name):
        print(name)
        if not any(name == kernel.kernel_name for kernel in self.kernels):
            return False
        else:
            for kernel in self.kernels:
                if name == kernel.kernel_name:
                    if kernel.local is not None:
                        thr = threading.Thread(target=self.remove_kernel_thr, args=(kernel,))
                        thr.start()
                        break
                    else:
                        self.send_update("%s is not installed." % name)
                        return False
            return True

    def remove_kernel_thr(self, kernel):
        if not self.pagent.check_authorization():
            return False
        self.busy_signal(True)
        kernel.removeKernel(info_func=self.send_update)
        self.update_grub_thr()
        self.busy_signal(False)
        self.refresh_signal()

    @dbus.service.method('com.github.pyakm.system')
    def add_ignorepkg(self, name):
        if not self.pagent.check_authorization():
            return False
        if not any(name == kernel.kernel_name for kernel in self.kernels):
            return False
        else:
            for kernel in self.kernels:
                if name == kernel.kernel_name:
                    kernel.addIgnorePkg()
                    kernel.addIgnorePkg(False)
                    break
            return True

    @dbus.service.method('com.github.pyakm.system')
    def remove_ignorepkg(self, name):
        if not self.pagent.check_authorization():
            return False
        if not any(name == kernel.kernel_name for kernel in self.kernels):
            return False
        else:
            for kernel in self.kernels:
                if name == kernel.kernel_name:
                    kernel.removeIgnorePkg()
                    kernel.removeIgnorePkg(False)
                    break
            return True
        
    @dbus.service.method('com.github.pyakm.system')
    def list_loaded_kernels(self, name):
        return [kernel.kernel_name for kernel in self.kernels]

    @dbus.service.method('com.github.pyakm.system')
    def get_kernel_infos(self):
        out_list = []
        for kernel in self.kernels:
            out = {}
            out['kernel_name'] = kernel.kernel_name
            out['repo_version'] = "" if kernel.repo == None else kernel.repo.version
            if out['repo_version'] is None: out['repo_version'] = ""
            out['local_version'] = "" if kernel.local == None else kernel.local.version
            if out['local_version'] is None: out['local_version'] = ""
            out['header_version'] = "" if kernel.header == None else kernel.header.version
            if out['header_version'] is None: out['header_version'] = ""
            out_list.append(out)
            
        return out_list

    @dbus.service.method('com.github.pyakm.system')
    def get_kernel_versions(self, name):
        if not any(name == kernel.kernel_name for kernel in self.kernels):
            return False
        else:
            for kernel in self.kernels:
                if name == kernel.kernel_name:
                    return kernel.vers
            return False
        
    @dbus.service.method('com.github.pyakm.system')
    def grub_default_kernel(self, name):
        self.send_update('bla bla')
        if not self.pagent.check_authorization():
            return False
            
        if not any(name == kernel.kernel_name for kernel in self.kernels):
            return False
        else:
            for kernel in self.kernels:
                if name == kernel.kernel_name:
                    if kernel.local is not None:
                        grub.replace_default_kernel(name)
                        self.update_grub()
                        break
                    else:
                        self.send_update("%s is not installed." % name)
                        return False
            return True

    @dbus.service.method('com.github.pyakm.system')
    def update_grub(self):
        t = threading.Thread(target=self.update_grub_thr)
        t.start()

    def update_grub_thr(self):
        self.send_update("Updating grub...")
        if not self.pagent.check_authorization():
            return False
        if self.busy:
            grub.update_grub()
        else:
            self.busy_signal(True)
            grub.update_grub()
            self.busy_signal(False)
            self.refresh_signal()

class ClientManager:

    def __init__(self, app):

        self.bus = dbus.SystemBus()
        self.system = self.bus.get_object("com.github.pyakm.system",
                                     "/com/github/pyakm/system")

        self.iface = 'com.github.pyakm.system'

        self.load_kernel = self.system.get_dbus_method('load_kernel', self.iface)
        self.refresh_kernel = self.system.get_dbus_method('refresh_kernel', self.iface)
        self.upgrade_kernel = self.system.get_dbus_method('upgrade_kernel', self.iface)
        self.downgrade_kernel = self.system.get_dbus_method('downgrade_kernel', self.iface)
        self.remove_kernel = self.system.get_dbus_method('remove_kernel', self.iface)
        self.add_ignore_pkg = self.system.get_dbus_method('add_ignore_pkg', self.iface)
        self.remove_ignore_pkg = self.system.get_dbus_method('remove_ignore_pkg', self.iface)
        self.list_loaded_kernels = self.system.get_dbus_method('list_loaded_kernels', self.iface)
        self.get_kernel_infos = self.system.get_dbus_method('get_kernel_infos', self.iface)
        self.get_kernel_versions = self.system.get_dbus_method('get_kernel_versions', self.iface)
        self.grub_default_kernel = self.system.get_dbus_method('grub_default_kernel', self.iface)
        self.init_data = self.system.get_dbus_method('init_data', self.iface)
        self.init_polkit_agent = self.system.get_dbus_method('init_polkit_agent', self.iface)

        self.bus.add_signal_receiver(app.on_update_signal, signal_name='send_update')
        self.bus.add_signal_receiver(app.on_busy_signal, signal_name='busy_signal')
        self.bus.add_signal_receiver(app.refreshWindow, signal_name='refresh_signal')




