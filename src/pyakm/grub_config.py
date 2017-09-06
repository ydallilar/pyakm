import sys, os
import subprocess as subp

def read_template():

    f = open('/usr/share/pyakm/grub_config/01_pyakm_template')
    f_str = f.read()
    f.close()

    return f_str

def replace_grub_str(f_str, kernel):

    f_str.replace('linux-template', kernel.name)
    
    return f_str

def replace_default_kernel(kernel):

    f_str = read_template()
    f_str = replace_grub_str(f_str, kernel)

    print(f_str)
    
    
    
