
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

        self.ui.pushButton_cancel.clicked.connect(self._cancel)
        self.ui.pushButton_skip.clicked.connect(self.close)
        self.ui.pushButton_apply.clicked.connect(self._apply)

        self.new_name = ''
        self.status = 'pause'

    def _cancel(self):
        self.status = 'abort'
        self.close()

    def _apply(self):
        self.new_name = self.ui.lineEdit_new_name.text()
        self.status = 'new_name'
        self.close()

    def set_lines(self, cur_name, new_name):
        self.ui.lineEdit_cur_name.setText(cur_name)
        self.ui.lineEdit_new_name.setText(new_name)




"""
Dialog not work as well
need to connect dialog buttons to MyWindow func
"""




class MyWindow(QtWidgets.QMainWindow):
    """
    Class with implementation of this program
    This is behaviour, not a gui

    """
    def __init__(self):
        super(MyWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.mydialog = MyDialog()
        self.ui.setupUi(self)
        self.ui.pushButton_start.clicked.connect(self._start)
        self.ui.pushButton_path.clicked.connect(self._select_path)
        self.ui.checkBox_user_replace.stateChanged.connect(self._update_rename_state)
        self.ui.lineEdit_filepath.setText(str(os.getcwd()))

    def _get_files_list(self):
        try:
            path = self.ui.lineEdit_filepath.text()
            file_paths=[]
            if (self.ui.check_include_subfolder.isChecked()):
                for top, dirs, files in os.walk(path):
                    for nm in files:       
                        file_paths.append(os.path.join(top, nm))
            else:
                files_names = os.listdir(path)
                for name in files_names:
                    file_paths.append(os.path.join(path, name))

            file_paths = list(filter(lambda x: x.endswith('.mp3'), file_paths))
            return file_paths
        except:
            print("Wrong way!")

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


    def _rename(self, path, dir, name, new_name):
        try:
            os.rename(path, os.path.join(dir, new_name))
            print("RENAME: "+name+'\t'+new_name)
        except FileExistsError:
            if self.ui.checkBox_samename.isChecked():
                os.remove(os.path.join(dir, new_name))
                os.rename(path, os.path.join(dir, new_name))
                print("DELETE: "+name+'\t'+new_name)
            else:
                os.rename(path, os.path.join(dir, new_name + " - Copy"))
                print("COPY: "+name+'\t'+new_name)

    def _name_editor(self, file_paths):
        renames_counter = 0
        files_count = len(file_paths)
        for i, path in enumerate(file_paths):
            name_and_dir = os.path.split(path)
            dir, name = name_and_dir[0], name_and_dir[1]
            new_name = name

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
                new_name = new_name.replace(edit_from,edit_to)

            # Changeble mode
            if new_name != name:
                if self.ui.radioButton_all.isChecked():
                    print('checked')
                    self._rename(path, dir, name, new_name)
                    renames_counter += 1
                else:
                    self.mydialog.set_lines(name, new_name)
                    self.mydialog.show()
                    if self.mydialog.status == 'new_name':
                        new_name = self.mydialog.new_name
                        self._rename(path, dir, name, new_name)
                        renames_counter += 1
                    if self.mydialog.status == 'abort':
                        self.mydialog.status = 'pause'
                        break

            self.ui.progressBar.setProperty("value", i/len(file_paths)*100)
        return renames_counter

    def _select_path(self):
        dialog = QtWidgets.QFileDialog()
        folder_path = dialog.getExistingDirectory(None, "Select Folder")
        if os.path.isdir(folder_path):
            self.ui.lineEdit_filepath.setText(folder_path)

    def _start(self):
        self.ui.progressBar.setEnabled(True)
        self.ui.progressBar.setTextVisible(True)
        file_paths = self._get_files_list()
        print(".mp3 files found: "+str(len(file_paths)))

        renames = self._name_editor(file_paths)
        print("Renames: "+ str(renames))

        self.ui.progressBar.setProperty("value", 0)
        self.ui.progressBar.setEnabled(False)
        self.ui.progressBar.setTextVisible(False)