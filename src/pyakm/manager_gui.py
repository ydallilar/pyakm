
#  Copyright © 2017 Yigit Dallilar <yigit.dallilar@gmail.com>
#
#  manager_gui.py is a part of pyakm. 
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

import dbus, time, os
import gi, threading
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, GLib
from dbus.mainloop.glib import DBusGMainLoop
from pyakm.dbus import ClientManager


kernels = ['linux', 'linux-lts', 'linux-zen', 'linux-hardened']


class ManagerGui(Gtk.Window):

    def __init__(self):
        
        self.builder = Gtk.Builder()
        self.builder.add_from_file("/usr/share/pyakm/ui/manager.ui")
        self.window = self.builder.get_object('window1')

        self.kernel_menu_entries = ['linux', 'linux-lts', 'linux-zen', 'linux-hardened']
        self.selected_menu_entry = 'linux'

        self.window_loaded = False

        self.spinner1 = self.builder.get_object('spinner1')
        self.spinner2 = self.builder.get_object('spinner2')

        self.status_bar1 = self.builder.get_object('status_bar1')
        self.status_bar2 = self.builder.get_object('status_bar2')

        self.stack1 = self.builder.get_object('stack1')
        
        self.manage_view_entry = None        
        self.status_view_entry = None
        
        self.button_remove = self.builder.get_object('button_remove')
        self.button_remove.connect("clicked", self.removeAction)

        self.button_set_default = self.builder.get_object('button_set_default')
        self.button_set_default.connect("clicked", self.setdefaultAction)

        self.button_select = self.builder.get_object('button_select')
        self.button_select.connect("clicked", self.selectAction)

        self.button_upgrade = self.builder.get_object('button_upgrade')
        self.button_upgrade.connect("clicked", self.upgradeAction)

        self.button_refresh = self.builder.get_object('button_refresh')
        self.button_refresh.connect("clicked", self.refreshAction)
        
        self.menu_kernel = self.builder.get_object('menu_kernel')
        self.menu_kernel.connect("row_selected", self.menuSelectAction)

        self.window.connect("delete-event", Gtk.main_quit)
        self.window.show_all()

        self.on_busy_signal(True)
        self.on_update_signal("Initializing...")

        self.client = ClientManager(self)        
        self.client.init_data(kernels)
        self.client.init_polkit_agent(os.getppid())
        
    def on_update_signal(self, msg):
        self.status_bar1.set_label(msg)
        self.status_bar2.set_label(msg)

    def on_busy_signal(self, busy):
        if busy:
            self.spinner1.start()
            self.spinner2.start()
            self.button_refresh.set_sensitive(False)
            self.stack1.set_sensitive(False)
        else:
            self.spinner1.stop()
            self.spinner2.stop()
            self.button_refresh.set_sensitive(True) 
            self.stack1.set_sensitive(True)
            self.status_bar1.set_label("")
            self.status_bar2.set_label("")
            
    def refreshWindow(self):
        self.createStatusView()
        self.loadStatusView()
        self.createManageView()
        self.loadManageView(self.selected_menu_entry)
        self.window_loaded = True


    def loadKernels(self):
        for kernel in kernels:
            self.client.load_kernel(kernel)

    def refreshKernels(self):
        for kernel in kernels:
            self.client.refresh_kernel(kernel)

    def statusViewSelectAction(self, sel):
        model, treeiter = sel.get_selected()
        if treeiter is not None:
            self.status_view_entry = list(model[treeiter])

    def manageViewSelectAction(self, sel):
        model, treeiter = sel.get_selected()
        if treeiter is not None:
            self.menu_view_entry = list(model[treeiter])
            
    def menuSelectAction(self, box, row):
        self.loadManageView(self.kernel_menu_entries[row.get_index()])
        self.selected_menu_entry = self.kernel_menu_entries[row.get_index()]
            
    def setdefaultAction(self, widget):
        print('Adding to grub menu,', self.status_view_entry[0])
        self.client.grub_default_kernel(self.status_view_entry[0])

    def upgradeAction(self, widget):
        print('upgradeAction,', self.selected_menu_entry)
        self.client.upgrade_kernel(self.selected_menu_entry)

    def removeAction(self, widget):
        print('removeAction,', self.status_view_entry[0])
        self.client.remove_kernel(self.status_view_entry[0])

    def selectAction(self, widget):
        print('Selected entry, ', self.selected_menu_entry)   
        self.client.downgrade_kernel(self.menu_view_entry[0], self.menu_view_entry[1].strip())

    def refreshAction(self, widget):
        self.refreshWindow()

    def createStatusView(self):

        if not self.window_loaded:
            renderer = Gtk.CellRendererText()
            self.status_view = self.builder.get_object("status_view")
            column = Gtk.TreeViewColumn("Kernel", renderer, text=0)
            column.set_expand(True)
            self.status_view.append_column(column)
            column = Gtk.TreeViewColumn("Local Version", renderer, text=1)
            column.set_alignment(1)
            self.status_view.append_column(column)
            column = Gtk.TreeViewColumn("Header version", renderer, text=2)
            column.set_alignment(1)
            self.status_view.append_column(column)
            column = Gtk.TreeViewColumn("Repo version", renderer, text=3)
            column.set_alignment(1)
            self.status_view.append_column(column)

        self.status_store = Gtk.ListStore(str, str, str, str)
        self.status_view.set_model(self.status_store)
        self.status_view_selection = self.status_view.get_selection()
        self.status_view_selection.connect('changed', self.statusViewSelectAction)

    def loadStatusView(self):

        self.kernel_info = self.client.get_kernel_infos()
        self.status_store = Gtk.ListStore(str, str, str, str)

        for kernel in self.kernel_info:
            self.status_store.append((kernel['kernel_name'], '%25s' % kernel['local_version'],
                                      '%25s' % kernel['header_version'],
                                      '%25s' % kernel['repo_version']))

        self.status_view.set_model(self.status_store)
                                      
    def createManageView(self):
            
        if not self.window_loaded:
            renderer = Gtk.CellRendererText()
            self.manage_view = self.builder.get_object("manage_view")
            column = Gtk.TreeViewColumn("Kernel", renderer, text=0)
            column.set_expand(True)
            self.manage_view.append_column(column)
            column = Gtk.TreeViewColumn("Version", renderer, text=1)
            column.set_alignment(1)
            self.manage_view.append_column(column)

        self.manage_store = Gtk.ListStore(str, str)
        self.manage_view.set_model(self.manage_store)
        self.manage_view_selection = self.manage_view.get_selection()
        self.manage_view_selection.connect('changed', self.manageViewSelectAction)

    def loadManageView(self, name):

        versions = self.client.get_kernel_versions(name)
        self.manage_store = Gtk.ListStore(str, str)

        for version in versions:
            self.manage_store.append((name, '%25s' % version))

        self.manage_view.set_model(self.manage_store)


