import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import pyakm.kernel_module as kernel_module
import re

def _argsort(arr):
    return sorted(range(len(arr)), key=arr.__getitem__)
    

def grab_kernel_packages_by_name(kernel_name):
    
    kernel_id = kernel_module.kernel_dicts[kernel_name]
    kernel_list = kernel_module.grab_kernel_official()
    packages = kernel_module.grab_package_list(kernel_list[kernel_id])
    return packages

def parse_package_versions(kernel_name, packages):

    pass
    

def sort_and_filter_packages(kernel_name, packages):

    pkg_vers = []

    for i,pkg in enumerate(packages):
        res = re.match(kernel_name+"-(\w+).(\w+).(\w+)-(\w+)-x", pkg)
        if res != None:
            print("in")
            pkg_vers.append(int("%02d%02d%02d%02d" % \
                                (int(res.group(1)),int(res.group(2)),
                                 int(res.group(3)),int(res.group(4)))))

    print (pkg_vers)
    
    sorted_ndx = _argsort(pkg_vers)[::-1]
    print (sorted_ndx)
    pkg_vers.sort()
    pkg_vers = pkg_vers[::-1]

    tmp_packages = []
    for i in range(len(sorted_ndx)):
        tmp_packages.append(packages[sorted_ndx])
    packages = tmp_packages
        
    print (pkg_vers)
    
    new_packages = []
    last_vers = ""
                    
    for i in len(packages):
        vers = str(pkg_vers[i])[:4]
        if last_ver != vers:
            new_package.append(packages[i])
            last_ver = vers

    return packages
            
    
