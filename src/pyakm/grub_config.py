import sys, os
import subprocess as subp

def read_template():

    f = open('/usr/share/pyakm/grub_config/01_pyakm_template')
    f_str = f.read()
    f.close()

    return f_str

def replace_grub_str(f_str, kernel):

    f_str = f_str.replace('linux-template', kernel.name)
    
    return f_str

def replace_default_kernel(kernel):

    f_str = read_template()
    f_str = replace_grub_str(f_str, kernel)

    usr = os.popen('id -u -n').read()[:-1]
    f = open('/home/%s/.config/pyakm/01_pyakm' % usr, 'w')
    f.write(f_str)
    f.close()

    req = subp.Popen(['sudo', 'cp',
                      '/home/%s/.config/pyakm/01_pyakm' % usr,
                      '/etc/grub.d/01_pyakm'])

    req = subp.Popen(['sudo', 'chmod',
                      '755',
                      '/etc/grub.d/01_pyakm'])

    req = subp.Popen(['sudo', 'grub-mkconfig',
                      '-o',
                      '/boot/grub/grub.cfg'],
                     stdout=subp.PIPE, stderr=subp.PIPE,
                     close_fds=True)

    for line in iter(req.stdout.readline, b''):
        sys.stdout.write(line.decode('utf-8'))

def disable_default_kernel():

    if os.path.isfile('/etc/grub.d/01_pyakm'):
        req = subp.Popen(['sudo', 'chmod',
                          '644',
                          '/etc/grub.d/01_pyakm'])

        req = subp.Popen(['sudo', 'grub-mkconfig',
                          '-o',
                          '/boot/grub/grub.cfg'],
                         stdout=subp.PIPE, stderr=subp.PIPE,
                         close_fds=True))

        for line in iter(req.stdout.readline, b''):
            sys.stdout.write(line.decode('utf-8'))

        

