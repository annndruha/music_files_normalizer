
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal
from mainwindow import Ui_MainWindow
from dialog import Ui_Dialog
from tags import Ui_TagEditor

import time
import eyed3
import threading
import os
import re

class MyDialog(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyDialog, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

class TagsDialog(QtWidgets.QMainWindow):
    def __init__(self):
        super(TagsDialog, self).__init__()
        self.ui = Ui_TagEditor()
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
        self.tags = TagsDialog()
        self.ui.setupUi(self)
        self.ui.lineEdit_filepath.setText(str(os.getcwd()))

        # Signals
        self.ui.pushButton_start.clicked.connect(self._start)
        self.ui.pushButton_path.clicked.connect(self._select_path)
        self.ui.checkBox_user_replace.stateChanged.connect(self._update_rename_state)
        self.ui.checkBox_logs.stateChanged.connect(self.changesize)
        self.ui.radioButton_tag_auto.toggled.connect(self.tags_enable)

        self.mydialog.ui.pushButton_cancel.clicked.connect(self._dialog_cancel)
        self.mydialog.ui.pushButton_skip.clicked.connect(self._dialog_skip)
        self.mydialog.ui.pushButton_apply.clicked.connect(self._dialog_apply)

        self.tags.ui.pushButton_tags_cancel.clicked.connect(self._tags_cancel)
        self.tags.ui.pushButton_tags_skip.clicked.connect(self._tags_skip)
        self.tags.ui.pushButton_save.clicked.connect(self._tags_apply)

        # Variables
        self.file_paths = []
        self.current_file = 0
        self.new_name = ''
        self.old_path = ''
        self.old_name = ''
        self.renames_counter = 0
        self.edited_tags_counter = 0
        self.start_first_time = True


    def log(self, text):
        self.ui.plainTextEdit_log.insertPlainText(text)
        max = self.ui.plainTextEdit_log.verticalScrollBar().maximum()
        if (max - 24) >0: max = max -24
        self.ui.plainTextEdit_log.verticalScrollBar().setValue(max)

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

    # Tag editor signals
    def _tags_cancel(self):
        self.tags.close()
        self._end()

    def _tags_skip(self):
        self.tags.ui.track_num_0.clear()
        self.tags.ui.track_num_1.clear()
        self.tags.ui.disc_num_0.clear()
        self.tags.ui.lineEdit.clear()
        self.tags.ui.lineEdit_2.clear()
        self.tags.ui.lineEdit_3.clear()
        self.tags.ui.lineEdit_4.clear()
        self.tags.ui.lineEdit_5.clear()
        self.tags.ui.lineEdit_8.clear()
        self.tags.ui.lineEdit_9.clear()
        self.tags.ui.lineEdit_10.clear()
        self.tags.close()
        self.current_file += 1
        self._run()

    def _tags_apply(self):
        try:
            audio = eyed3.load(self.old_path)
            audio.tag.track_num = self.tags.ui.track_num_0.value(), self.tags.ui.track_num_1.value()
            audio.tag.disc_num = self.tags.ui.disc_num_0.value(), self.tags.ui.disc_num_1.value() 
            audio.tag.title = self.tags.ui.lineEdit.text()
            audio.tag.artist = self.tags.ui.lineEdit_2.text()
            audio.tag.artist_url = self.tags.ui.lineEdit_3.text()
            audio.tag.album = self.tags.ui.lineEdit_4.text()
            audio.tag.album_artist = self.tags.ui.lineEdit_5.text()
            audio.tag.publisher = self.tags.ui.lineEdit_8.text()
            audio.tag.composer = self.tags.ui.lineEdit_9.text()
            try:
                audio.tag.bpm = int(self.tags.ui.lineEdit_10.text())
            except:
                audio.tag.bpm = 0
            audio.tag.save(self.old_path)
            self.edited_tags_counter += 1
            self.log(f'\nINFO: Tags changed: {self.old_name}')
        except:
            self.log(f'\nFAIL TO SAVE TAGS: {self.old_name}')
        self.current_file +=1
        self.tags.ui.track_num_0.clear()
        self.tags.ui.track_num_1.clear()
        self.tags.ui.disc_num_0.clear()
        self.tags.ui.lineEdit.clear()
        self.tags.ui.lineEdit_2.clear()
        self.tags.ui.lineEdit_3.clear()
        self.tags.ui.lineEdit_4.clear()
        self.tags.ui.lineEdit_5.clear()
        self.tags.ui.lineEdit_8.clear()
        self.tags.ui.lineEdit_9.clear()
        self.tags.ui.lineEdit_10.clear()
        self.tags.close()
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

    def changesize(self):
        if self.ui.checkBox_logs.isChecked():
            self.setMaximumSize(1600,500)
            self.resize(1600,500)
            self.setMinimumSize(1600,500)
        else:
            self.setMinimumSize(840,500)
            self.resize(840,500)
            self.setMaximumSize(840,500)

    def tags_enable(self):
        if self.ui.radioButton_tag_auto.isChecked():
            self.ui.checkBox_delete_tags.setEnabled(True)
            self.ui.checkBox_set_artist_tag.setEnabled(True)
            self.ui.checkBox_set_song_tag.setEnabled(True)
        else:
            self.ui.checkBox_delete_tags.setEnabled(False)
            self.ui.checkBox_set_artist_tag.setEnabled(False)
            self.ui.checkBox_set_song_tag.setEnabled(False)

    # Functions
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
            self.log("\nERROR: Incorrect folder path!")
            #print("Wrong way!")

    def _rename(self, old_path):
        path, old_name = os.path.split(old_path)[0], os.path.split(old_path)[1]
        new_name = old_name
        if self.ui.checkBox_user_replace.isChecked(): max = 2
        else: max = 10
        for _ in range(1, max):
            if self.ui.checkBox_brackets.isChecked():
                new_name = re.sub(r'\([^\(\)]*(\([^\(\)]*(\([^\(\)]*\))*[^\(\)]*\))*[^\(\)]*\)', '', new_name)
                new_name = re.sub(r'/^\[(.+)\]$/', '', new_name)
                new_name = re.sub(r'\[[^\]]*\]', '', new_name)
                new_name = re.sub(r'\[.*', '', new_name)
                new_name = re.sub(r'\(.*', '', new_name)
                new_name +='.mp3'
                new_name = new_name.replace('.mp3.mp3','.mp3')

            if self.ui.checkBox_mp3.isChecked():
                new_name = new_name.replace('.mp3.mp3','.mp3')
                new_name = new_name.replace('  .mp3','.mp3')
                new_name = new_name.replace(' .mp3','.mp3')
                
                new_name = new_name.replace('-.mp3','.mp3')

            if self.ui.checkBox_underscore.isChecked():
                k = new_name.find('_')
                if k == 0:
                    new_name.replace('_','')
                if k>0 and k < len(new_name)-2:
                    if new_name[k-1].isalpha() and new_name[k+1].isalpha():
                        new_name = new_name.replace('_',"'")
                new_name = new_name.replace('_.mp3','.mp3')
                new_name = new_name.replace(' _',' ')
                new_name = new_name.replace('_ ',' ')
                new_name = new_name.replace('_',' ')
                new_name = new_name.replace('- -','-')

            if self.ui.checkBox_doublespace.isChecked():
                new_name = new_name.replace('—','-')
                new_name = new_name.replace('  ',' ')

            if self.ui.checkBox_user_replace.isChecked():
                edit_from = self.ui.lineEdit_from.text()
                edit_to = self.ui.lineEdit_to.text()
                new_name = new_name.replace(edit_from, edit_to)

        new_path = os.path.join(path, new_name)
        return new_name, new_path, old_path, old_name


    def _rename_file(self, new_name, new_path, old_path, old_name):
        try:
            os.rename(old_path, new_path)
            self.log("\nRENAME:\t"+ old_name +'\n-->\t'+new_name)
        except FileExistsError:
            if self.ui.checkBox_samename.isChecked():
                os.remove(new_path)
                os.rename(old_path, new_path)
                self.log("\nDELETE:\t"+old_name+'\n-->\t'+new_name)
            else:
                os.rename(old_path, os.path.join(dir, new_name + " - Copy"))
                self.log("\nCOPY:\t"+old_name+'\n-->\t'+new_name)

    def _tags_editor(self, path, old_name):
        try:
            audio = eyed3.load(path)
            self.tags.ui.lineEdit_name.setText(old_name)
            if audio.tag.track_num[0] is not None:
                self.tags.ui.track_num_0.setValue(audio.tag.track_num[0])
            if audio.tag.track_num[1] is not None:
                self.tags.ui.track_num_1.setValue(audio.tag.track_num[1])

            if audio.tag.disc_num[0] is not None:
                self.tags.ui.disc_num_0.setValue(audio.tag.disc_num[0])
            if audio.tag.disc_num[1] is not None:
                self.tags.ui.disc_num_1.setValue(audio.tag.disc_num[1])

            if audio.tag.title is not None:
                self.tags.ui.lineEdit.setText(str(audio.tag.title))
            if audio.tag.artist is not None:
                self.tags.ui.lineEdit_2.setText(str(audio.tag.artist))
            if audio.tag.artist_url is not None:
                self.tags.ui.lineEdit_3.setText(str(audio.tag.artist_url))
            if audio.tag.album is not None:
                self.tags.ui.lineEdit_4.setText(str(audio.tag.album))
            if audio.tag.album_artist is not None:
                self.tags.ui.lineEdit_5.setText(str(audio.tag.album_artist))
            if audio.tag.publisher is not None:
                self.tags.ui.lineEdit_8.setText(str(audio.tag.publisher))
            if audio.tag.composer is not None:
                self.tags.ui.lineEdit_9.setText(str(audio.tag.composer))
            if audio.tag.bpm is not None:
                self.tags.ui.lineEdit_10.setText(str(audio.tag.bpm))
            self.tags.show()
            return True
        except:
            self.log(f'\nFAIL TAGS OPEN: {old_name}')
            return False

    def _run(self):
        if len(self.file_paths)<=0:
            self.log('\nINFO: No files found')
        else:
            while self.current_file != len(self.file_paths)-1:
                path = self.file_paths[self.current_file]
                new_name, new_path, old_path, old_name = self._rename(path)
                self.old_path = old_path
                self.old_name = old_name
                self.ui.progressBar.setProperty("value", self.current_file/len(self.file_paths)*100)

                if ((self.ui.radioButton_all.isChecked()) and (new_name != old_name)): # Force rename
                    self._rename_file(new_name, new_path, old_path, old_name)
                    self.renames_counter += 1
                elif ((self.ui.radioButton_dialog.isChecked()) and (new_name != old_name)):
                    self.mydialog.ui.lineEdit_cur_name.setText(old_name)
                    self.mydialog.ui.lineEdit_new_name.setText(new_name)
                    self.mydialog.show()
                    break
                elif (self.ui.radioButton_tag_manual.isChecked()):
                    if self._tags_editor(path, old_name):
                        break
                elif (self.ui.radioButton_tag_auto.isChecked()):
                    try:
                        audio = eyed3.load(self.old_path)
                        if self.ui.checkBox_delete_tags.isChecked():
                            audio.tag.clear()
                            audio.tag.save(self.old_path)
                            self.edited_tags_counter +=1
                            self.log(f'\nINFO: Tags deleted in: {old_name}')
                        if self.ui.checkBox_set_artist_tag.isChecked():
                            if len(self.old_name.split(' - ')) == 2:
                                audio.tag.artist = (self.old_name.split(' - ')[0]).replace('.mp3', '')
                                audio.tag.save(self.old_path)
                                self.edited_tags_counter +=1
                                self.log(f'\nINFO: Artist tag added in: {old_name}')
                        if self.ui.checkBox_set_song_tag.isChecked():
                            if len(self.old_name.split(' - ')) == 2:
                                audio.tag.title = (self.old_name.split(' - ')[1]).replace('.mp3', '')
                                audio.tag.save(self.old_path)
                                self.edited_tags_counter +=1
                                self.log(f'\nINFO: Title tag added in: {old_name}') 
                    except:
                        self.log(f'\nINFO: Can\'t auto tag change in: {old_name}')

                self.current_file += 1
            if self.current_file == len(self.file_paths)-1:
                self._end()

    def _start(self):
        self.log(f"===START===")
        self.ui.progressBar.setEnabled(True)
        self.ui.progressBar.setTextVisible(True)
        self._get_files_list()

        if self.start_first_time:
            self.log(f"\nINFO: MP3 files found: {str(len(self.file_paths))}")
            self.start_first_time = False
        else:
            self.log(f"\nINFO: MP3 files found: {str(len(self.file_paths))}")
        self._run()  


    def _end(self):
        self.log(f"\nINFO: Total renames: {str(self.renames_counter)}")
        self.log(f"\nINFO: Total tags changes: {str(self.edited_tags_counter)}")
        self.file_paths = []
        self.new_name = ''
        self.old_path = ''
        self.old_name = ''
        self.current_file = 0
        self.renames_counter = 0
        self.edited_tags_counter = 0
        self.ui.progressBar.setProperty("value", 0)
        self.ui.progressBar.setEnabled(False)
        self.ui.progressBar.setTextVisible(False)