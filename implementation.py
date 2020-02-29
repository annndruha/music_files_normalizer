
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal
from mainwindow import Ui_MainWindow

import time
import threading
import os

# Edit box всплывающее окно

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton_start.clicked.connect(self.start)
        self.ui.plainTextEdit_filepath.setPlainText(os.getcwd())

    def _get_files_list(self):
        try:
            path = self.ui.plainTextEdit_filepath.toPlainText()
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

    def _name_editor(self, file_paths):
        renames_counter = 0
        files_count = len(file_paths)
        for i, path in enumerate(file_paths):
            name_and_dir = os.path.split(path)
            dir, name = name_and_dir[0], name_and_dir[1]
            new_name = name

            if self.ui.checkBox_mp3.isChecked():
                new_name = new_name.replace('.mp3.mp3','.mp3')

            # Changeble mode
            if new_name != name:
                os.rename(path, os.path.join(dir, new_name))
                renames_counter += 1

            self.ui.progressBar.setProperty("value", str(6/455))
        return renames_counter

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

    def start(self):
        print("Hello gui!")
        self._start()