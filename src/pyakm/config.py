
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class Config:

    def __init__(self):

        super(Config, self).__setattr__('opts', {})
        self.config_fname = '/etc/pyakm.conf'
        self.readOpts()
        #self.loadOpts()
        
    def loadOpts(self):
        self.opts['addtoIgnorePkg'] = True
        self.opts['updateGrub'] = False
        self.opts['grubScriptOpt'] = False

    def readOpts(self):

        conf_lines = open(self.config_fname).readlines()

        for conf_line in conf_lines:
            conf_line = conf_line[:-1].replace('\t', '  ')
            args = [args.strip() for args in conf_line.split(' ') if args.strip() != '']

            if len(args) > 1 and args[0][0] != '#':
                if args[1] == 'True':
                    self.opts[args[0]] = True
                elif args[1] == 'False':
                    self.opts[args[0]] = False
                else:
                    self.opts[args[0]] = ' '.join(args[1:])
        
    def __getitem__(self, option):
        return self.opts[option]

    def __setitem__(self, option, value):
        self.opts[option] = value
        
    def printOpts(self):
        for opt in self.opts:
            print("%-20s : %10s" % (opt, self.opts[opt]))
            
class ConfigGui(Gtk.Window):

    def __init__(self):

        self.builder = Gtk.Builder()
        self.builder.add_from_file("/usr/share/pyakm/ui/preferences.ui")

        self.window = self.builder.get_object('settings_gui')

        self.switch_addtoIgnorePkg = self.builder.get_object('switch_addtoIgnorePkg')
        self.switch_updateGrub = self.builder.get_object('switch_updateGrub')
        self.switch_grubScriptOpt = self.builder.get_object('switch_grubScriptOpt')

        self.switch_addtoIgnorePkg.connect('state_set', self.option_addtoIgnorePkg)
        self.switch_updateGrub.connect('state_set', self.option_updateGrub)
        self.switch_grubScriptOpt.connect('state_set', self.option_grubScriptOpt)

        self.text_grubScriptCmd = self.builder.get_object('text_grubScriptCmd')
        self.apply_grubScriptCmd = self.builder.get_object('apply_grubScriptCmd')

        self.button_close = self.builder.get_object('button_close')
        self.button_close.connect('clicked', self.onCloseButton)
        
        self.window.show_all()

        self.conf = Config()

        self.init_window()

    def init_window(self):
        self.switch_addtoIgnorePkg.set_active(self.conf['addtoIgnorePkg'])
        self.switch_updateGrub.set_active(self.conf['updateGrub'])
        self.switch_grubScriptOpt.set_active(self.conf['grubScriptOpt'])
        
    def switch_task(self, option_name, value):
        self.conf[option_name] = value
        self.conf.printOpts()
        
    def option_addtoIgnorePkg(self, switch, gparam):
        option_name = 'addtoIgnorePkg'
        if switch.get_active():
            self.switch_task(option_name, True)
        else:
            self.switch_task(option_name, False)

    def option_updateGrub(self, switch, gparam):
        option_name = 'updateGrub'
        if switch.get_active():
            self.switch_task(option_name, True)
        else:
            self.switch_task(option_name, False)

    def option_grubScriptOpt(self, switch, gparam):
        option_name = 'grubScriptOpt'
        if switch.get_active():
            self.switch_task(option_name, True)
            self.text_grubScriptCmd.set_sensitive(True)
            self.apply_grubScriptCmd.set_sensitive(True)
        else:
            self.switch_task(option_name, False)
            self.text_grubScriptCmd.set_sensitive(False)
            self.apply_grubScriptCmd.set_sensitive(False)

    def onCloseButton(self, widget):

        self.window.destroy()
