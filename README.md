# pyakm (or Arch Linux Kernel Manager)

Simple kernel manager for arch linux basically a gtk application to manage official kernels.

Binaries include:
* pyakm-system-daemon
* pyakm-manager

pyakm-system-daemon will be started by systemd upon the execution pyakm-manager. That means you can see the logs via `journalctl -u pyakm-system -b 0 | grep pyakm > log.txt` or something similar. Send me the logs this way.

There are not many decent pyalpm, python-dbus, polkit examples around. So, I hope this will also be useful if you are searching for an answer on these topics.

![Screenshot](https://github.com/pssncp142/pyakm/blob/dev/screenshot.png)

GUI can be simplified to four tasks:
- Remove         : Removes selected kernel and updates grub. 
- Set as Default : Adds an entry to your grub menu for the selected kernel and updates grub.
  - If you want to remove this entry simply delete `/etc/grub.d/01_pyakm` and update grub.
- Select         : Installs kernel with selected version. Adds the kernel and the header package to `IgnorePkg` in /etc/pacman.conf
- Upgrade        : Installs the latest version of the selected kernel. Removes the kernel from `IgnorePkg`