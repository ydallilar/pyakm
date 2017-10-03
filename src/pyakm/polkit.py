#  Copyright © 2017 Yigit Dallilar <yigit.dallilar@gmail.com>
#
#  kernel.py is a part of pyakm. 
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

import sys, os
from gi.repository import GObject, Gio, Polkit


class PolkitAgent:

    def __init__(self, osppid, info_func=None):

        self.authority = Polkit.Authority.get()
        self.loop = GObject.MainLoop()
        self.subject = Polkit.UnixProcess.new(osppid)
        self.cancellable = Gio.Cancellable()
        self.action_id = "com.github.pyakm.commit"
        self.is_authorized = False
        self.info_func = info_func
        
    def check_authorization(self):
        
        self.authority.check_authorization(self.subject, self.action_id, None,
                                 Polkit.CheckAuthorizationFlags.ALLOW_USER_INTERACTION,
                                 self.cancellable, self.check_authorization_cb,
                                 self.loop)

        self.loop.run()

        return self.is_authorized
        
    def check_authorization_cb(self, authority, res, loop):
    
        result = authority.check_authorization_finish(res)
 
        try:
            self.is_authorized = result.get_is_authorized()
            self.is_challenge = result.get_is_challenge()
                
        except GObject.GError as error:
            if self.info_func is not None:
                self.info_func("Error checking authorization: %s" % error.message)


        if not self.is_authorized or self.is_challenge:
            self.info_func("Failed to authorize transaction")

        self.loop.quit()

