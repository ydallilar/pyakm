
import subprocess as subp
import sys, os
import requests
from bs4 import BeautifulSoup

kernel_dicts = {'linux' : 0, 'linux-zen' : 1,
                'linux-lts' : 2, 'linux-hardened' : 3}
okernels = ['linux', 'linux-zen', 'linux-lts', 'linux-hardened']
archrepo_url = 'https://archive.archlinux.org/packages/'

# kernel class to store variables
class Arch_kernel:

    #variables
    name = ''
    versionloc = ''
    versionrem = ''
    installed = ''

    def __init__(self, kernel_dict):
        self.get_kernel_info(kernel_dict)

    def get_kernel_info(self, kernel_dict):
        self.installed = kernel_dict['Installed']
        self.name = kernel_dict['Name_rem']

        if self.installed:
            self.versionloc = kernel_dict['Version_loc']
            self.versionrem = kernel_dict['Version_rem']
        else:
            self.versionloc = None
            self.versionrem = kernel_dict['Version_rem']

    def print_kernel_info(self):

        print('Kernel        :%15s\nVersion (loc) :%15s\nVersion (rem) :%15s'%\
            (self.name, self.versionloc, self.versionrem))
        if self.installed:
            print('Installed     :%15s\n' % 'Yes')
        else:
            print('Installed     :%15s\n' % 'No')

# parse package output into dictionary
def kernel_package_dict(locreq, remreq, installed=0):

    kernel_dict = {}
    loc_dict = {}
    rem_dict = {}
    
    locreq = locreq.decode('utf-8').split('\n')
    for line in locreq:
        dict_name = line.split(':')[0].strip()+'_loc'
        if dict_name != '':
            dict_value = ':'.join(line.split(':')[1:])
            kernel_dict[dict_name] = dict_value.strip()

    remreq = remreq.decode('utf-8').split('\n')
    for line in remreq:
        dict_name = line.split(':')[0].strip()+'_rem'
        if dict_name != '':
            dict_value = ':'.join(line.split(':')[1:])
            kernel_dict[dict_name] = dict_value.strip()

    if installed:
        kernel_dict['Installed'] = True
    else:
        kernel_dict['Installed'] = False


    return kernel_dict

# grabs official kernel lists    
def grab_kernel_official():

    kernel_list = []
    
    for kerneltxt in okernels:
        installed = 0
        
        kernelreq = subp.Popen(['/usr/bin/pacman', '-Qi', '%s' % kerneltxt],
                               stdout=subp.PIPE, stderr=subp.PIPE,
                               close_fds=True)
        kernelreq.wait()
        code = kernelreq.returncode
        if code == 0: installed = 1
        locreq, _ = kernelreq.communicate()
        
        kernelreq = subp.Popen(['/usr/bin/pacman', '-Si', '%s' % kerneltxt],
                               stdout=subp.PIPE, stderr=subp.PIPE,
                               close_fds=True)
        kernelreq.wait()    
        remreq, _ = kernelreq.communicate()

        kernel_dict = kernel_package_dict(locreq, remreq, installed)

        kernel = Arch_kernel(kernel_dict)
        kernel_list.append(kernel)

    return kernel_list

# grabs package list for specific kernel
def grab_package_list(kernel):

    package_list = []
    url = archrepo_url + '/' + kernel.name[0] + '/' + kernel.name + '/'
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    for a in soup.find_all('a'):
        if (a['href'].split('.')[-1] == 'xz') & (a['href'].find('x86_64') > -1):
            package_list.append(a['href'])

    return package_list[::-1]

# Downloads kernel package 
def grab_kernel_package(kernel, package_list, ndx):

    usr = os.popen('id -u -n').read()[:-1]
    url = archrepo_url + '/' + kernel.name[0] + '/' + kernel.name + '/'
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    package = package_list[ndx]

    print ('Downloading , ', package)
    req = requests.get(url+package, stream=True)
    f = open(('/home/%s/.config/pyakm/'%usr)+package, 'wb')
    ctr = 0
    for data in req.iter_content(chunk_size=4096):
        f.write(data)
    f.close()

# installs kernel    
def install_kernel(kernel, package_list, ndx):

    usr = os.popen('id -u -n').read()[:-1]
    f_name = package_list[ndx]
    full_path = ('/home/%s/.config/pyakm/' % usr) + f_name
    if not os.path.isfile(full_path): grab_kernel_package(kernel, package_list, ndx)
    
    print (full_path, os.path.isfile(full_path))
    
    req = subp.Popen(['sudo', '/usr/bin/pacman', '-U',
                      '%s' % full_path, '--noconfirm'],
                     stdout=subp.PIPE, stderr=subp.PIPE,
                     close_fds=True)
   
    for line in iter(req.stdout.readline, b''):
        sys.stdout.write(line.decode('utf-8'))

# installs latest kernel
def install_latest_kernel(kernel, package_list):

    install_kernel(kernel, package_list, 0)
    
