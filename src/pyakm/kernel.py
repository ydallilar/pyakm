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

import pyalpm as alpm
from pycman import config
import json, requests, re, os, functools, dbus, time
from bs4 import BeautifulSoup

conf = config.PacmanConfig(conf="/etc/pacman.conf")
handle = conf.initialize_alpm()

official_dict = {'linux':'core', 'linux-lts':'core',
                 'linux-zen':'extra', 'linux-hardened':'community'}

archive_url = "https://archive.archlinux.org/packages/"
aur_url = "https://aur.archlinux.org/rpc/?v=5&"

pkg_str = '%s-%s-x86_64.pkg.tar.xz'

cache_dir = '/var/cache/pyakm/'


class OfficialKernel:

    def __init__(self, kernel_name):

        self.type = "Official"
        self.kernel_name = kernel_name
        self.header_name = kernel_name + "-headers"
        self.repo = None
        self.local = None
        self.header = None
        self.vers = []
        self.uptodate = -1 # -1: not installed, 0:false, 1:true
        self.status = "Idle"
        self.task_name = None

    def Refresh(self, info_func=None):

        self.getKernelPackage(info_func=info_func)
        self.getHeaderPackage(info_func=info_func)
        self.getRepoKernel(info_func=info_func)
        self.getArchiveList(info_func=info_func)
        self._isUptoDate()

    def getKernelPackage(self, info_func=None):

        if info_func is not None:
            info_func('Checking local database for, ' + self.kernel_name)
        print('Checking local database for, ', self.kernel_name)

        db = handle.get_localdb()
        pkg = db.get_pkg(self.kernel_name)
        #if pkg != None:
        self.local = pkg

    def getHeaderPackage(self, info_func=None):

        if info_func is not None:
            info_func('Checking local database for, ' + self.header_name)
        print('Checking local database for, ', self.header_name)

        db = handle.get_localdb()
        pkg = db.get_pkg(self.header_name)
        #if pkg != None:
        self.header = pkg


    def getRepoKernel(self, opt=True, info_func=None):

        if info_func is not None:
            info_func('Obtain repo package, '+ self.kernel_name)
            
        dbs = handle.get_syncdbs()
        for db in dbs:
            if db.name == official_dict[self.kernel_name]:
                self.repo = db.get_pkg(self.kernel_name)
                break

    def getRepoHeader(self, opt=True, info_func=None):

        if info_func is not None:
            info_func('Obtain repo package, ', self.header_name)
            
        dbs = handle.get_syncdbs()
        for db in dbs:
            if db.name == official_dict[self.kernel_name]:
                return db.get_pkg(self.header_name)
                
            
    def getArchiveList(self, info_func=None):

        if info_func is not None:
            info_func('Retrieving archive list for, %s' % self.kernel_name)
        print('Retrieving archive list for, %s' % self.kernel_name)
        
        file_list = []
        vers = []
        url = archive_url + '/' + self.kernel_name[0] + '/' + self.kernel_name + '/'
        soup = BeautifulSoup(requests.get(url).text, 'html.parser')
        for a in soup.find_all('a'):
            if (a['href'].split('.')[-1] == 'xz') & (a['href'].find('x86_64') > -1):
                file_list.append(a['href'])

        for package in file_list:
            vers.append(self._getVersFromFilename(package))

        self.vers = sorted(vers,
                           key=functools.cmp_to_key(alpm.vercmp), reverse=True)

    def downloadKernel(self, version, opt=True, info_func=None):
        #1 : for kernel
        #0 : for header
        
        if opt:
            name = self.kernel_name
        else:
            name = self.header_name

        url = archive_url + '/' + name[0] + '/' + name + '/'
        soup = BeautifulSoup(requests.get(url).text, 'html.parser')
        package = pkg_str % (name, version)

        req = requests.get(url+package, stream=True, timeout=1)
        tot = int(req.headers['Content-length'])
        chunk_sz = 4096
        f = open(cache_dir+package, 'wb')
            
        if info_func is not None: 
            cnt = 0
            for data in req.iter_content(chunk_size=chunk_sz):
                cnt += 1
                info_func("Downloading %s %3d%%" % (package,int(cnt*chunk_sz/tot*100)))
                f.write(data)
        else:
            cnt = 0
            for data in req.iter_content(chunk_size=chunk_sz):
                cnt += 1
                f.write(data)

        f.close()


    def upgradeKernel(self, opt=True, info_func=None):
        #1 : for kernel
        #0 : for header

        self.info_func = info_func
        self.task_name = 'Installing ' 
        
        if opt:
            if info_func is not None:
                handle.dlcb = self._dlcb
                handle.eventcb = self._eventcb
                handle.progresscb = self._progcb
                info_func('Upgrading, %s' % (self.kernel_name))
        else:
            if info_func is not None:
                handle.dlcb = self._dlcb
                handle.eventcb = self._eventcb
                handle.progresscb = self._progcb
                info_func('Upgrading, %s' % (self.header_name))
        
        trans = handle.init_transaction()

        if opt:
            trans.add_pkg(self.repo)
        else:
            trans.add_pkg(self.getRepoHeader())

        while(True):
            if not os.path.isfile(handle.lockfile):
                break
            if info_func is not None: info_func('Waiting for other package manager to quit...')
            time.sleep(2)

        trans.prepare()
        trans.commit()
        trans.release()

        self.removeIgnorePkg(opt=opt, info_func=info_func)
        if opt:
            self.getKernelPackage(info_func=info_func)
        else:
            self.getHeaderPackage(info_func=info_func)

        if opt:
            if not self._isHeaderUpdated():
                self.upgradeKernel(False, info_func=info_func)

    def downgradeKernel(self, version, opt=True, info_func=None):
        #1 : for kernel
        #0 : for header

        self.task_name = 'Installing ' 
        
        if not any(version == item for item in self.vers):
            print(version, 'does not match with the any packages.')
            return False

        self.info_func = info_func
        
        if opt:
            handle.dlcb = self._dlcb
            handle.eventcb = self._eventcb
            handle.progresscb = self._progcb
            name = self.kernel_name
        else:
            handle.dlcb = self._dlcb
            handle.eventcb = self._eventcb
            handle.progresscb = self._progcb
            name = self.header_name

        if info_func is not None: info_func('Downgrading, %s' % (name))

        try: 
            self.downloadKernel(version, opt, info_func=info_func)
        except:
            self.info_func('Failed to connect to %s' % s)
            return False

        pkg = handle.load_pkg(cache_dir+ pkg_str % \
                             (name, version))
        
        trans = handle.init_transaction()
        trans.add_pkg(pkg)
        trans.prepare()
        trans.commit()
        trans.release()

        self.addIgnorePkg(opt=opt, info_func=info_func)
        if opt:
            self.getKernelPackage(info_func=info_func)
        else:
            self.getHeaderPackage(info_func=info_func)

        if opt:
            if not self._isHeaderUpdated(info_func=info_func):
                self.downgradeKernel(version, False, info_func=info_func)

        return True

    def addIgnorePkg(self, opt=True, info_func=None):
        #1 : for kernel
        #0 : for header

        if opt:
            name = self.kernel_name
        else:
            name = self.header_name
            
        for ignored in handle.ignorepkgs:
            if ignored == name:
                if info_func is not None: info_func('%s is already in IgnorePkg' % name)
                return False

        if info_func is not None: info_func('Adding %s to IgnorePkg' % name)
            
        
        lines = open('/etc/pacman.conf', 'r').readlines()
        
        for i in range(len(lines)):
            line = lines[i].split(' ')
            if (line[0] == "#IgnorePkg") | (line[0] == "IgnorePkg"):
                tmp = ["IgnorePkg", "="] + handle.ignorepkgs + \
                                       [name + "\n"]
                lines[i] = " ".join(tmp)

        lines = "".join(lines)

        f = open('/etc/pacman.conf', 'w')
        f.write(lines)
        handle.add_ignorepkg(name)

        f.close()

    def removeIgnorePkg(self, opt=True, info_func=None):
        #1 : for kernel
        #0 : for header
        if opt:
            name = self.kernel_name
        else:
            name = self.header_name

        print('Unignore package, ', name)
        
        for ignored in handle.ignorepkgs:
            if ignored == name:
                if info_func is not None: info_func('Removing %s from IgnorePkg' % name)
                
                lines = open('/etc/pacman.conf', 'r').readlines()
        
                for i in range(len(lines)):
                    line = lines[i].split(' ')
                    if (line[0] == "#IgnorePkg") | (line[0] == "IgnorePkg"):
                        tmp = ["IgnorePkg", "="] + handle.ignorepkgs + \
                                       ["\n"]
                        lines[i] = " ".join(tmp)

                lines = "".join(lines)

                f = open('/etc/pacman.conf', 'w')
                f.write(lines)
                handle.remove_ignorepkg(name)
                f.close()


    def removeKernel(self, opt=True, info_func=None):
        
        self.info_func = info_func
        self.task_name = 'Removing ' 
        
        if opt:
            if info_func is not None:
                handle.dlcb = self._dlcb
                handle.eventcb = self._eventcb
                handle.progresscb = self._progcb
                info_func('Removing, %s' % (self.kernel_name))
        else:
            if info_func is not None:
                handle.dlcb = self._dlcb
                handle.eventcb = self._eventcb
                handle.progresscb = self._progcb
                info_func('Removing, %s' % (self.header_name))
        
        trans = handle.init_transaction()

        if opt:
            if self.local is None:
                return False
            trans.remove_pkg(self.local)
        else:
            trans.remove_pkg(self.header)

        trans.prepare()
        trans.commit()
        trans.release()

        self.removeIgnorePkg(opt=opt, info_func=info_func)
        if opt:
            self.getKernelPackage(info_func=info_func)
            if self.header is not None:
                self.removeKernel(False, info_func=info_func)
        else:
            self.getHeaderPackage(info_func=info_func)


    def setDefault(self):
        pass

    def _isUptoDate(self):
        if self.local is None:
            return -1
        elif self.local.version != self.repo.version:
            return 0
        else:
            return 1
        
    
    def _isHeaderUpdated(self, info_func=None):
        if self.header is None:
            if info_func is not None: info_func(self.header_name + ' is not installed.')
            return False
        elif self.header.version != self.local.version:
            if info_func is not None: info_func(self.header_name + 'requires upgrade. (%s => %s)' % \
                  (self.header.version, self.local.version))
            return False
        else:
            if info_func is not None: info_func(self.header_name + ' is up to date.')
            return True
        
    def _getVersFromFilename(self, f_name):
        res = re.match(pkg_str % (self.kernel_name, "(\S+)"), f_name)
        return res.group(1)

    def _dlcb(self, f_name, down, tot):
        self.info_func("Downloading %s %3d%%" % (f_name, int(down/tot*100)))

    def _eventcb(self, *args):
        pass
        #print(args)
        #self.info_func("%s" % args[1])

    def _progcb(self, target, percent, n, i):
        self.info_func("%s %s %3d%%" % (self.task_name, target, percent) )

class AURKernel:
    
    def __init__(self, kernel_name):
            
        self.type = "AUR"
        self.kernel_name = kernel_name
        self.repo = None
        self.local = None
        
        self.getLocalPackage()
        self.getRepoPackage()

    def getLocalPackage(self):
        
        db = handle.get_localdb()
        pkg = db.get_pkg(self.kernel_name)
        if pkg != None:
            self.local = pkg

    def getRepoPackage(self):

        info = requests.get(aur_url + "type=info&arg[]=%s" % self.kernel_name).json()
        if info['resultcount'] == 1:
            self.fillPkgInfo(info)

    def fillPkgInfo(self, info):
        
        tmp_info = info['results'][0]
        self.repo.name = tmp_info['Name']
        self.repo.version = tmp_info['Version']
        self.repo.desc = tmp_info['Description']
        self.repo.licences = tmp_info['Licenses']
        
    def upgradeKernel():
        pass

    def removeKernel(self):
        pass

    def setDefault():
        pass

