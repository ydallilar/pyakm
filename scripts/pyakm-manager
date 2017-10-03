#!/usr/bin/env python3

#  Copyright © 2017 Yigit Dallilar <yigit.dallilar@gmail.com>
#
#  pyakm-manager.py is a part of pyakm. 
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

from pyakm.manager_gui import ManagerGui
from dbus.mainloop.glib import DBusGMainLoop
import gi, threading
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


if __name__ == '__main__':

    DBusGMainLoop(set_as_default=True)
    app = ManagerGui()
    Gtk.main()
 
