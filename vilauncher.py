import os
import sys
import json
import time
import shutil
import psutil
import threading
import subprocess
import uuid as uuid_module
from libraries import launcher_lib
from ui.main_window import Ui_main
from ui.dialog_options import Ui_dialog
from PySide2.QtWidgets import QApplication, QMainWindow, QMessageBox, QDialog, QScrollBar, QTextBrowser
from PySide2.QtGui import QIcon, QCloseEvent
from PySide2.QtCore import QThread, QMutex, Signal

launcher_name : str = 'VILauncher'
launcher_version : str = '0.02'

# CONSTANTS

FILTER_VANILLA : int = 0
FILTER_FABRIC : int  = 1

# VARIABLES

sleep_time : float = 0.05

# CLASSES

class Console_Thread(QThread): # CONSOLE THREAD
    append = Signal(str)
    move_scrollbar = Signal()
    def __init__(self, other, process:subprocess.Popen, tl_skin_path:str, modpack_name:str):
        super(Console_Thread, self).__init__()
        self.thread_lock : QMutex           = QMutex()
        self.arg_other   : Main_Window      = other
        self.arg_process : subprocess.Popen = process
        self.arg_tl_skin : str              = tl_skin_path
        self.arg_modpack : str              = modpack_name

    def run(self): # USE START TO RUN
        output : str = ''
        while not isinstance(self.arg_process.poll(), int):
            output = self.arg_process.stdout.readline()
            if output:
                self.append.emit(output)
                
        time.sleep(sleep_time)
        error : list = self.arg_process.stderr.readlines()
        if error:
            self.append.emit('\n'.join(error))

        if self.arg_tl_skin:
            if os.path.isfile(self.arg_tl_skin):
                os.remove(self.arg_tl_skin)
        if self.arg_modpack:
            launcher_lib.apply_modpack(launcher_lib.mc_lib.utils.get_minecraft_directory(), os.path.join(self.arg_other.modpack_dir, self.arg_modpack), self.arg_other.version.currentText(), True)
        os.chdir(self.arg_other.launcher_dir)
        self.arg_other.set_read_only(False)
        self.arg_other.progress_bar.setValue(0)
        time.sleep(sleep_time)
        self.append.disconnect()
        self.move_scrollbar.disconnect()

    def lock(self): # LOCK MUTEX
        self.thread_lock.lock()

    def unlock(self): # UNLOCK MUTEX
        self.thread_lock.unlock()

class Main_Window(QMainWindow, Ui_main): # MAIN WINDOW
    def __init__(self, is_debug:bool, icon:QIcon, parent=None):
        super(Main_Window, self).__init__(parent=parent)
        self.setupUi(self)
        self.connect_events()
        self.setWindowIcon(icon)
        self.scrollbar : QScrollBar = self.console.verticalScrollBar()

        # DECLARE VARIABLES

        self.console_thread : Console_Thread = None
        self.total_ram_mb : int = psutil.virtual_memory().total // 1024 // 1024
        self.client_token : str = ''
        self.github_token : str = ''
        self.current_ram_min : int = 0
        self.current_ram_max : int = 0
        self.option_old : bool  = False
        self.option_snap : bool = False
        self.option_mod : bool  = False
        self.jvm_args : str  = ''
        self.is_debug : bool = is_debug
        self.callback : dict = {
            'setProgress' : self.progress_bar.setValue,
            'setMax'      : self.progress_bar.setMaximum
        }

        # FIX DIRECTORY

        self.launcher_dir : str = os.path.dirname(os.path.realpath(__file__))
        os.chdir(self.launcher_dir)
        if not os.path.isdir('json/modpacks'):
            os.makedirs('json/modpacks')
        if not os.path.isdir('modpacks'):
            os.mkdir('modpacks')
        try:
            os.makedirs(launcher_lib.mc_lib.utils.get_minecraft_directory())
        except:
            pass

        self.save_json = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'json', 'save.json')
        self.cache_json = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'json', 'cache.json')
        self.modpack_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'modpacks')
        self.modpack_json_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'json', 'modpacks')

        # LOAD CACHE
        load_data = {
            'fabric' : [],
            'vanilla': [],
        }
        done = False
        while not done:
            if os.path.isfile(self.cache_json):
                with open(self.cache_json) as file:
                    try:
                        load_data = json.load(file)
                        done = True
                    except:
                        os.remove(self.cache_json)
            else:
                done = True

        with open(self.cache_json, 'w') as file:
            version_data = [version.get('id') for version in launcher_lib.get_versions_online(False, False)]

            data_fabric = []
            for version in version_data:
                if not version in [data[0] for data in load_data['fabric']]:
                    data_fabric.append(version)
                        
            return_fabric = launcher_lib.ls_fabric_version(data_fabric)

            all_fabric = []
            for version in version_data:
                all_fabric.append((version, True if version in return_fabric else False))
            
            current_fabric = [data[0] for data in load_data['fabric']]
            end_fabric = []
            for version in all_fabric:
                if version[0] in current_fabric:
                    end_fabric.append([data for data in load_data['fabric'] if data[0] == version[0]][0])
                else:
                    end_fabric.append(version)

            load_data['fabric'] = end_fabric
            load_data['vanilla']= version_data

            json.dump(load_data, file)
        
        for ac_type in launcher_lib.get_account_types():
            self.account_type.addItem(ac_type)
        for filter_type in get_filters():
            self.filter_box.addItem(filter_type)
        for modpack in os.listdir(self.modpack_json_dir):
            self.filter_box.addItem(modpack.rstrip('.json'))

        self.load_conf()
        self.filter_box.setCurrentIndex(1)

    def connect_events(self):
        self.button_play.clicked.connect(self.play_pressed)
        self.filter_box.currentIndexChanged.connect(self.filter_index)
        self.button_options.clicked.connect(self.show_options)
        self.account_type.currentIndexChanged.connect(self.change_account)

    def disconnect_events(self):
        self.button_play.clicked.disconnect()
        self.filter_box.currentIndexChanged.disconnect()
        self.button_options.clicked.disconnect()
        self.account_type.currentIndexChanged.disconnect()
    
    def create_message(self, title:str, information:str): # CREATE MESSAGE BOX
        message_box = QMessageBox()
        message_box.setWindowTitle(title)
        message_box.setText(information)
        message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        message_box.exec_()
    
    def set_read_only(self, ro:bool): # DISABLE BUTTONS
        self.button_play.setDisabled(ro)
        self.button_options.setDisabled(ro)
        self.filter_box.setDisabled(ro)
        self.version.setDisabled(ro)
        self.account_type.setDisabled(ro)
        self.username.setDisabled(ro)
        self.uuid.setDisabled(ro)
        self.access_token.setDisabled(ro)

    def show_options(self): # SHOW OPTIONS DIALOG
        window = QDialog()
        dialog = Ui_dialog()
        dialog.setupUi(window)

        dialog.label_max_current.setText(str(self.current_ram_max) + 'M')
        dialog.slider_max_ram.setMaximum(self.total_ram_mb)
        dialog.slider_max_ram.valueChanged.connect(lambda i: self.change_dialog_max(dialog, i))
        dialog.slider_max_ram.setValue(self.current_ram_max)

        dialog.label_min_current.setText(str(self.current_ram_min) + 'M')
        dialog.slider_min_ram.setMaximum(self.total_ram_mb)
        dialog.slider_min_ram.valueChanged.connect(lambda i: self.change_dialog_min(dialog, i))
        dialog.slider_min_ram.setValue(self.current_ram_min)

        dialog.check_old.setChecked(self.option_old)
        dialog.check_snapshots.setChecked(self.option_snap)
        dialog.check_modified.setChecked(self.option_mod)
        dialog.jvm_args.setText(self.jvm_args)
        dialog.github_token.setText(self.github_token)

        dialog.button_box.accepted.connect(lambda: self.save_options(window, dialog))
        dialog.button_box.rejected.connect(window.reject)
        window.exec_()
        
    def save_options(self, window, dialog): # SAVE OPTIONS
        self.current_ram_max = dialog.slider_max_ram.value()
        self.current_ram_min = dialog.slider_min_ram.value()
        self.option_old  = dialog.check_old.isChecked()
        self.option_snap = dialog.check_snapshots.isChecked()
        self.option_mod  = dialog.check_modified.isChecked()
        self.jvm_args     = dialog.jvm_args.text()
        self.github_token = dialog.github_token.text()
        window.accept()

    def change_dialog_min(self, dialog, value:int): # ON EVENT CHANGE SLIDER
        dialog.label_min_current.setText(str(value) + 'M')
        dialog.slider_min_ram.setValue((value + 15) // 16 * 16)

    def change_dialog_max(self, dialog, value:int): # ON EVENT CHANGE SLIDER
        dialog.label_max_current.setText(str(value) + 'M')
        dialog.slider_max_ram.setValue((value + 15) // 16 * 16)

    def filter_index(self, index:int): #  ON EVENT CHANGE FILTER
        self.version.clear()
        if self.filter_box.currentText() == get_filters()[0]: # VANILLA
            for mc_version in launcher_lib.get_versions_online(self.option_snap, self.option_old):
                self.version.addItem(mc_version.get('id'))
        elif self.filter_box.currentText() == get_filters()[1]: # FABRIC
            data : dict = {}
            with open(self.cache_json) as file:
                data = json.load(file)
            for mc_version in data['fabric']:
                if mc_version[1]:
                    self.version.addItem(mc_version[0])
        else:
            for modpack in os.listdir(self.modpack_json_dir): # MODPACKS
                if self.filter_box.currentText() == modpack.rstrip('.json'):
                    with open(os.path.join(self.modpack_json_dir, modpack)) as file:
                        versions : list = json.load(file)['versions']
                        for mc_version in versions:
                            self.version.addItem(mc_version)
                    break

    def change_account(self, _:int): # ON EVENT CHANGE ACCOUNT TYPE
        if self.account_type.currentText() == launcher_lib.get_account_types()[0]:
            self.uuid.setPlaceholderText('UUID/Password')
            self.access_token.setPlaceholderText('Token/NULL')
        else:
            self.uuid.setPlaceholderText('UUID')
            self.access_token.setPlaceholderText('Token')

    def scroll_signal(self): # ON EVENT CONSOLE NEW LINE
        lines : int = (self.console.height() // self.console.fontMetrics().height()) * 15
        if self.scrollbar.value() >= self.scrollbar.maximum() - lines:
            self.scrollbar.setValue(self.scrollbar.maximum())

    def append_console(self, text:str): # APPEND TEXT TO CONSOLE
        self.console.append(text)

    def play_pressed(self): # BUTTON PLAY PRESSED
        self.set_read_only(True)
        os.chdir(launcher_lib.mc_lib.utils.get_minecraft_directory())
        self.console.setText('') # FIX DIRECTORY ISSUES AND CLEAR CONSOLE
        selected_version : str = self.version.currentText()
        version_formated : str = selected_version.lstrip('Fabric ').split('-')[-1]
        if not self.current_ram_min or not self.current_ram_max: # RAM OPTION NOT SET
            self.create_message('Memory Allocation', 'Allocate both minimum and maximum RAM in options')
            self.set_read_only(False)
            self.progress_bar.setValue(0)
            os.chdir(self.launcher_dir)
            return
        code : int = launcher_lib.CODE_VANILLA # VERSION TYPE
        index : int = self.filter_box.currentIndex()
        modpack_name : str = ''
        if self.filter_box.currentText() == get_filters()[1]: # FABRIC
            code = launcher_lib.CODE_FABRIC
        else:
            for modpack in os.listdir(self.modpack_json_dir):
                if self.filter_box.currentText() == modpack.rstrip('.json'):
                    with open(os.path.join(self.modpack_json_dir, modpack)) as file:
                        data : dict = json.load(file)
                        modpack_name = data['name']
                        code = data['modified']
                        if not launcher_lib.download_modpack(data, os.path.join(self.modpack_dir, modpack_name, version_formated), version_formated, self.callback, self.github_token):
                            self.create_message(modpack_name, 'Could not fetch files for (' + version_formated + ') ' + modpack_name)
                            self.set_read_only(False)
                            self.progress_bar.setValue(0)
                            os.chdir(self.launcher_dir)
                            return
                        launcher_lib.apply_modpack(launcher_lib.mc_lib.utils.get_minecraft_directory(), os.path.join(self.modpack_dir, modpack_name), version_formated, False)
                    break
        # MORE RELEVANT VARIABLES
        username : str = self.username.text()
        uuid : str = self.uuid.text()
        token : str = self.access_token.text()
        ac_type : str = self.account_type.currentText()
        # INSTALL VERSIONS IF NOT INSTALLED
        return_message : list = launcher_lib.install_version(selected_version, launcher_lib.mc_lib.utils.get_minecraft_directory(), self.callback, code, self.launcher_dir)
        tl_skin_path : str = ''
        # HANDLE MESSAGES AND TLSKINCAPE PATH
        if len(return_message) == 1:
            selected_version = return_message[0][0]
            tl_skin_path = return_message[0][1]
        elif len(return_message) == 2:
            self.create_message(return_message[0], return_message[1])
            self.set_read_only(False)
            self.progress_bar.setValue(0)
            if modpack_name:
                launcher_lib.apply_modpack(launcher_lib.mc_lib.utils.get_minecraft_directory(), os.path.join(self.modpack_dir, modpack_name), version_formated, True)
            os.chdir(self.launcher_dir)
            return
        else:
            self.create_message(return_message[1], return_message[2])
            selected_version = return_message[0][0]
            tl_skin_path = return_message[0][1]
        installed_tl_skin : str = ''
        if tl_skin_path:
            if ac_type == launcher_lib.get_account_types()[1]:
                installed_tl_skin = os.path.join(launcher_lib.mc_lib.utils.get_minecraft_directory(), 'mods', os.path.basename(tl_skin_path))
                if not os.path.isdir(os.path.dirname(installed_tl_skin)):
                    os.mkdir(os.path.dirname(installed_tl_skin))
                shutil.copyfile(tl_skin_path, installed_tl_skin)
        # HANDLE ACCOUNT
        if token and uuid:
            if ac_type == launcher_lib.get_account_types()[0]:
                if not launcher_lib.mc_lib.account.validate_access_token(token):
                    new_token : dict = launcher_lib.mc_lib.account.refresh_access_token(token, self.client_token)
                    self.create_message('Access Token', 'This access token (' + token + ') is invalid')
                    self.set_read_only(False)
                    self.progress_bar.setValue(0)
                    if modpack_name:
                        launcher_lib.apply_modpack(launcher_lib.mc_lib.utils.get_minecraft_directory(), os.path.join(self.modpack_dir, modpack_name), version_formated, True)
                    os.chdir(self.launcher_dir)
                    return
        elif not token and uuid: # TODO
            if ac_type == launcher_lib.get_account_types()[0]:
                login_data = launcher_lib.mc_lib.account.login_user(username, uuid)
                print(login_data) # REMOVE
                username = login_data['selectedProfile']['name']
                uuid = login_data['selectedProfile']['id']
                token = login_data['accessToken']
                self.username.setText(username)
                self.uuid.setText(uuid)
                self.access_token.setText(token)
        else:
            uuid = '0'
            token = 'null'
        # START MINECRAFT
        java_args = self.jvm_args.split() + launcher_lib.set_ram(self.current_ram_min, self.current_ram_max, 'M') + self.jvm_args.split()
        process = launcher_lib.launch(launcher_lib.mc_lib.utils.get_minecraft_directory(), selected_version, username, uuid, token, ac_type, java_args, self.callback, (launcher_name, launcher_version))
        self.progress_bar.setValue(0)
        self.console_thread = Console_Thread(self, process, tl_skin_path, modpack_name)
        self.console_thread.append.connect(self.append_console)
        self.console_thread.move_scrollbar.connect(self.scroll_signal)
        self.console_thread.start()

    def load_conf(self): # LOAD CONFIGURUATION
        data : dict = {}
        if os.path.isfile(self.save_json):
            with open(self.save_json) as file:
                try:
                    data = json.load(file)
                except:
                    pass
        try: # IF DATA NOT EXISTS REMOVE
            self.username.setText(data['last_username'])
            self.uuid.setText(data['last_uuid'])
            self.access_token.setText(data['last_token'])
            self.account_type.setCurrentIndex(data['last_type'])
            self.current_ram_min = data['ram_min']
            self.current_ram_max = data['ram_max']
            self.option_old      = data['checked_old']
            self.option_snap     = data['checked_snapshots']
            self.option_mod      = data['checked_modified']
            self.jvm_args        = data['jvm_args']
            self.github_token    = data['github_token']
        except:
            if os.path.isfile(self.save_json):
                os.remove(self.save_json)

    def save_conf(self): # SAVE CONFIGURATION
        with open(self.save_json, 'w') as file:
            data = { # ALWAYS DUMP CONFIGURATION
                'last_username' : self.username.text(),
                'last_uuid'     : self.uuid.text() if self.is_valid_uuid(self.uuid.text()) else '',
                'last_token'    : self.access_token.text() if self.is_valid_uuid(self.access_token.text()) else '',
                'last_type'     : self.account_type.currentIndex(),
                'ram_min'       : self.current_ram_min,
                'ram_max'       : self.current_ram_max,
                'checked_old'   : self.option_old,
                'checked_snapshots' : self.option_snap,
                'checked_modified'  : self.option_mod,
                'jvm_args'          : self.jvm_args,
                'github_token'      : self.github_token
            }
            json.dump(data, file)
    
    def is_valid_uuid(self, uuid:str): # CHECK FOR VALID ACCOUND UUID AND TOKEN
        uuid_obj = None
        try:
            uuid_obj = uuid_module.UUID(uuid)
        except:
            return False
        return str(uuid_obj) == uuid

    def closeEvent(self, event:QCloseEvent):
        os.chdir(self.launcher_dir)
        self.disconnect_events()
        self.save_conf()
        event.accept()

# FUNCTIONS
def get_filters(): # GET VILAUNCHER FILTERS
    return [
        'Vanilla',
        'Fabric'
    ]

if __name__ == '__main__': # RUN
    debug = False
    for arg in sys.argv:
        if arg == '--debug':
            import faulthandler
            faulthandler.enable()
            debug = True
    print(launcher_name, launcher_version)
    print(launcher_lib.library_name, launcher_lib.library_version)
    print('Minecraft Launcher Lib', launcher_lib.mc_lib.helper.get_library_version(), '\n')
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    app = QApplication([])
    icon = QIcon(os.path.join('ui', 'icon.png'))
    app.setWindowIcon(icon)
    main_window_ = Main_Window(debug, icon)
    main_window_.show()
    sys.exit(app.exec_())
