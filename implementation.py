
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal
from mainwindow import Ui_MainWindow
from dialog import Ui_Dialog

import time
import threading
import os
import re

class MyDialog(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyDialog, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

class MyWindow(QtWidgets.QMainWindow):
    """
    Class with implementation of this program
    This is behaviour, not a gui
    """
    def __init__(self):
        # GUI
        super(MyWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.mydialog = MyDialog()
        self.ui.setupUi(self)
        self.ui.lineEdit_filepath.setText(str(os.getcwd()))

        # Signals
        self.ui.pushButton_start.clicked.connect(self._start)
        self.ui.pushButton_path.clicked.connect(self._select_path)
        self.ui.checkBox_user_replace.stateChanged.connect(self._update_rename_state)

        self.mydialog.ui.pushButton_cancel.clicked.connect(self._dialog_cancel)
        self.mydialog.ui.pushButton_skip.clicked.connect(self._dialog_skip)
        self.mydialog.ui.pushButton_apply.clicked.connect(self._dialog_apply)

        # Variables
        self.file_paths = []
        self.current_file = 0
        self.new_name = ''
        self.old_path = ''
        self.old_name = ''
        self.renames_counter = 0


    # Dialog signals
    def _dialog_cancel(self):
        self.mydialog.close()
        self._end()

    def _dialog_skip(self):
        self.mydialog.close()
        self.current_file += 1
        self._run()

    def _dialog_apply(self):
        self.new_name = self.mydialog.ui.lineEdit_new_name.text()
        path = os.path.split(self.old_path)[0]
        new_path = os.path.join(path, self.new_name)
        self._rename_file(self.new_name, new_path, self.old_path, self.old_name)
        self.current_file +=1
        self.renames_counter += 1
        self.mydialog.close()
        self._run()

    # Main window signals
    def _select_path(self):
        dialog = QtWidgets.QFileDialog()
        folder_path = dialog.getExistingDirectory(None, "Select Folder")
        if os.path.isdir(folder_path):
            self.ui.lineEdit_filepath.setText(folder_path)

    def _update_rename_state(self):
        if self.ui.checkBox_user_replace.isChecked():
            self.ui.lineEdit_from.setEnabled(True)
            self.ui.lineEdit_to.setEnabled(True)
            self.ui.label_replace_to.setEnabled(True)
        else:
            self.ui.lineEdit_from.setEnabled(False)
            self.ui.lineEdit_to.setEnabled(False)
            self.ui.label_replace_to.setEnabled(False)
            self.ui.lineEdit_from.setText('')
            self.ui.lineEdit_to.setText('')

    def _get_files_list(self):
        try:
            path = self.ui.lineEdit_filepath.text()
            if (self.ui.check_include_subfolder.isChecked()):
                for top, dirs, files in os.walk(path):
                    for nm in files:       
                        self.file_paths.append(os.path.join(top, nm))
            else:
                files_names = os.listdir(path)
                for name in files_names:
                    self.file_paths.append(os.path.join(path, name))

            self.file_paths = list(filter(lambda x: x.endswith('.mp3'), self.file_paths))
        except:
            print("Wrong way!")

    def _rename(self, old_path):
        path, old_name = os.path.split(old_path)[0], os.path.split(old_path)[1]
        new_name = old_name

        if self.ui.checkBox_mp3.isChecked():
            new_name = new_name.replace('.mp3.mp3','.mp3')
            new_name = new_name.replace(' .mp3','.mp3')
            new_name = new_name.replace('_.mp3','.mp3')

        if self.ui.checkBox_brackets.isChecked():
            new_name = re.sub(r'\([^\(\)]*(\([^\(\)]*(\([^\(\)]*\))*[^\(\)]*\))*[^\(\)]*\)', '', new_name)
            new_name = re.sub(r'/^\[(.+)\]$/', '', new_name)
            new_name = new_name.replace('  .mp3','.mp3')
            new_name = new_name.replace(' .mp3','.mp3')

        if self.ui.checkBox_defis.isChecked():
            new_name = new_name.replace('—','-')

        if self.ui.checkBox_underscore.isChecked():
            new_name = new_name.replace('_',' ')

        if self.ui.checkBox_user_replace.isChecked():
            edit_from = self.ui.lineEdit_from.text()
            edit_to = self.ui.lineEdit_to.text()
            new_name = new_name.replace(edit_from, edit_to)

        new_path = os.path.join(path, new_name)
        return new_name, new_path, old_path, old_name


    def _rename_file(self, new_name, new_path, old_path, old_name):
        try:
            os.rename(old_path, new_path)
            print("RENAME: "+ old_name +'\t\t'+new_name)
        except FileExistsError:
            if self.ui.checkBox_samename.isChecked():
                os.remove(new_path)
                os.rename(old_path, new_path)
                print("DELETE: "+old_name+'\t\t'+new_name)
            else:
                os.rename(old_path, os.path.join(dir, new_name + " - Copy"))
                print("COPY: "+old_name+'\t\t'+new_name)

    def _run(self):
        while self.current_file != len(self.file_paths)-1:
            path = self.file_paths[self.current_file]
            new_name, new_path, old_path, old_name = self._rename(path)
            self.ui.progressBar.setProperty("value", self.current_file/len(self.file_paths)*100)

            if ((self.ui.radioButton_all.isChecked()) and (new_name != old_name)): # Force rename
                self._rename_file(new_name, new_path, old_path, old_name)
                self.renames_counter += 1
            elif (new_name != old_name):
                self.old_path = old_path
                self.old_name = old_name
                self.mydialog.ui.lineEdit_cur_name.setText(old_name)
                self.mydialog.ui.lineEdit_new_name.setText(new_name)
                self.mydialog.show()
                break

            self.current_file += 1
        if self.current_file == len(self.file_paths)-1:
            self._end()

    def _start(self):
        self.ui.progressBar.setEnabled(True)
        self.ui.progressBar.setTextVisible(True)
        self._get_files_list()
        self._run()  


    def _end(self):
        print(".mp3 files found: "+str(len(self.file_paths)))
        print("Renames: "+ str(self.renames_counter))
        self.file_paths = []
        self.new_name = ''
        self.old_path = ''
        self.old_name = ''
        self.current_file = 0
        self.renames_counter = 0
        self.ui.progressBar.setProperty("value", 0)
        self.ui.progressBar.setEnabled(False)
        self.ui.progressBar.setTextVisible(False)