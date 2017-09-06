import os

usr = os.popen('id -u -n').read()[:-1]

if not os.path.exists('/home/%s/.config/pyakm' % usr):
    print ('~/.config/pyakm does not exist. Creating Directory...')
    os.makedirs('/home/%s/.config/pyakm' % usr)
