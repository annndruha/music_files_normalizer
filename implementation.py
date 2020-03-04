
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal
from mainwindow import Ui_MainWindow
from name_dialog import Ui_NameDialog
from tags import Ui_TagEditor

import time
import eyed3
import threading
import os
import re

class NameDialog(QtWidgets.QMainWindow):
    def __init__(self):
        super(NameDialog, self).__init__()
        self.ui = Ui_NameDialog()
        self.ui.setupUi(self)
        self.clear()
    def clear(self):
        self.ui.lineEdit_cur_name.clear()
        self.ui.lineEdit_new_name.clear()

class TagsDialog(QtWidgets.QMainWindow):
    def __init__(self):
        super(TagsDialog, self).__init__()
        self.ui = Ui_TagEditor()
        self.ui.setupUi(self)
        self.clear()
    def clear(self):
        self.ui.track_num_0.clear()
        self.ui.track_num_1.clear()
        self.ui.disc_num_0.clear()
        self.ui.lineEdit.clear()
        self.ui.lineEdit_2.clear()
        self.ui.lineEdit_3.clear()
        self.ui.lineEdit_4.clear()
        self.ui.lineEdit_5.clear()
        self.ui.lineEdit_8.clear()
        self.ui.lineEdit_9.clear()
        self.ui.lineEdit_10.clear()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.name = NameDialog()
        self.tags = TagsDialog()
        self.ui.lineEdit_filepath.setText(str(os.getcwd()))
        self.clear()

#===SIGNALS===
        self.ui.pushButton_start.clicked.connect(self._start)
        self.ui.pushButton_path.clicked.connect(self._select_path)
        self.ui.checkBox_user_replace.stateChanged.connect(self._update_rename_state)
        self.ui.checkBox_logs.stateChanged.connect(self._changesize)
        self.ui.radioButton_tag_auto.toggled.connect(self._tags_enable)

        self.name.ui.pushButton_cancel.clicked.connect(self._name_cancel)
        self.name.ui.pushButton_skip.clicked.connect(self._name_skip)
        self.name.ui.pushButton_apply.clicked.connect(self._name_apply)

        self.tags.ui.pushButton_tags_cancel.clicked.connect(self._tags_cancel)
        self.tags.ui.pushButton_tags_skip.clicked.connect(self._tags_skip)
        self.tags.ui.pushButton_save.clicked.connect(self._tags_apply)



#===SLOTS===
#===Main Window Slot
    # Start button
    def _start(self):
        self.clear()
        self.ui.progressBar.setEnabled(True)
        self.ui.progressBar.setTextVisible(True)
        self.get_files_list()

        if len(self.file_paths)<=0:
            self.log('\nERROR: No mp3 files found in selected directory')
            self.ui.lineEdit_filepath.setText('No mp3 files found in selected directory')
            self.end()
        else:
            self.log(f"\n===START===")
            self.log(f"\n===INFO: MP3 files found: {str(len(self.file_paths))}")
            self.run()

    # Select path button
    def _select_path(self):
        folder_dialog = QtWidgets.QFileDialog()
        folder_path = folder_dialog.getExistingDirectory(None, "Select Folder")
        self.ui.lineEdit_filepath.setText(folder_path)

    # User rename checkbutton
    def _update_rename_state(self):
        state = self.ui.checkBox_user_replace.isChecked()
        self.ui.lineEdit_from.setEnabled(state)
        self.ui.lineEdit_to.setEnabled(state)
        self.ui.label_replace_to.setEnabled(state)
        if not state: self.ui.lineEdit_from.setText('')
        if not state: self.ui.lineEdit_to.setText('')

    # Show logs button
    def _changesize(self):
        if self.ui.checkBox_logs.isChecked():
            self.setMaximumSize(1600,500)
            self.resize(1600,500)
            self.setMinimumSize(1600,500)
        else:
            self.setMinimumSize(840,500)
            self.resize(840,500)
            self.setMaximumSize(840,500)

    # Force tags replace button
    def _tags_enable(self):
        state = self.ui.radioButton_tag_auto.isChecked()
        self.ui.checkBox_delete_tags.setEnabled(state)
        self.ui.checkBox_set_artist_tag.setEnabled(state)
        self.ui.checkBox_set_song_tag.setEnabled(state)

#===Rename dialog slots
    # Cancel and end button
    def _name_cancel(self):
        self.name.close()
        self.end()

    # Skip file button
    def _name_skip(self):
        self.name.close()
        self.current_file += 1
        self.run()

    # Do rename button
    def _name_apply(self):
        self.new_name = self.name.ui.lineEdit_new_name.text()
        path = os.path.split(self.old_path)[0]
        new_path = os.path.join(path, self.new_name)
        self.rename_file(self.new_name, new_path, self.old_path, self.cur_name)
        self.current_file +=1
        self.renames_counter += 1
        self.name.close()
        self.run()

#===Tag editor slots
    # Cancel and end button
    def _tags_cancel(self):
        self.tags.close()
        self.end()

    # Skip file button
    def _tags_skip(self):
        self.tags.clear()
        self.tags.close()
        self.current_file += 1
        self.run()

    # Save tags changes button
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
                pass
            audio.tag.save(self.old_path)
            self.edited_tags_counter += 1
            self.log(f'\nINFO: Tags changed: {self.cur_name}')
        except:
            self.log(f'\nFAIL TO SAVE TAGS: {self.cur_name}')

        self.current_file +=1
        self.tags.clear()
        self.tags.close()
        self.run()

#===FUNCTIONS===
    def run(self):
        #self.cur_name = 5
        #for self.cur_name, path in enumerate(self.file_paths, self.cur_name):
        #    print(self.cur_name)

        while self.current_file <= len(self.file_paths)-1:
            path = self.file_paths[self.current_file]
            new_name, new_path, old_path, self.cur_name = self.rename(path)
            self.old_path = old_path
            self.ui.progressBar.setProperty("value", self.current_file/len(self.file_paths)*100)

            if ((self.ui.radioButton_all.isChecked()) and (new_name != self.cur_name)): # Force rename
                self.rename_file(new_name, new_path, old_path, self.cur_name)
                self.renames_counter += 1
            elif ((self.ui.radioButton_dialog.isChecked()) and (new_name != self.cur_name)):
                self.name.ui.lineEdit_cur_name.setText(self.cur_name)
                self.name.ui.lineEdit_new_name.setText(new_name)
                self.name.show()
                break
            elif (self.ui.radioButton_tag_manual.isChecked()):
                if self.set_tags_editor_fields(path, self.cur_name):
                    break
            elif (self.ui.radioButton_tag_auto.isChecked()):
                if (self.ui.checkBox_delete_tags.isChecked() or
                self.ui.checkBox_set_artist_tag.isChecked() or
                self.ui.checkBox_set_song_tag.isChecked()):
                    self.tags_force_edit()
                else:
                    self.log(f"\nINFO: Tags edit options doesn't selected")
                    self.current_file = len(self.file_paths)-1
                    break

            self.current_file += 1
        if self.current_file >= len(self.file_paths)-1:
            self.end()

    def log(self, text):
        self.ui.plainTextEdit_log.insertPlainText(text)
        max = self.ui.plainTextEdit_log.verticalScrollBar().maximum()
        if (max - 24) >0: max = max -3
        self.ui.plainTextEdit_log.verticalScrollBar().setValue(max)

    def end(self):
        self.log(f"\nINFO: Total renames: {str(self.renames_counter)}")
        self.log(f"\nINFO: Total tags changes: {str(self.edited_tags_counter)}")
        self.clear()
        self.ui.progressBar.setProperty("value", 0)
        self.ui.progressBar.setEnabled(False)
        self.ui.progressBar.setTextVisible(False)

    def rename_file(self, new_name, new_path, old_path, cur_name):
        try:
            os.rename(old_path, new_path)
            self.log("\nRENAME:\t"+ cur_name +'\n-->\t'+new_name)
        except FileExistsError:
            if self.ui.checkBox_samename.isChecked():
                os.remove(new_path)
                os.rename(old_path, new_path)
                self.log("\nDELETE:\t"+cur_name+'\n-->\t'+new_name)
            else:
                os.rename(old_path, os.path.join(dir, new_name + " - Copy"))
                self.log("\nCOPY:\t"+cur_name+'\n-->\t'+new_name)

    # Record all found files in self.file_paths list
    def get_files_list(self):
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
            self.log("\nERROR: Incorrect folder path")
            self.ui.lineEdit_filepath.setText("ERROR: Incorrect folder path")

    def rename(self, old_path):
        path, cur_name = os.path.split(old_path)[0], os.path.split(old_path)[1]
        new_name = cur_name
        for _ in range(1, 10):
            if self.ui.checkBox_brackets.isChecked():
                new_name = re.sub(r'\([^\(\)]*(\([^\(\)]*(\([^\(\)]*(\([^\(\)]*\))*[^\(\)]*\))*[^\(\)]*\))*[^\(\)]*\)', '', new_name)
                new_name = re.sub(r'\[[^\[\]]*(\[[^\[\]]*(\[[^\[\]]*(\[[^\[\]]*\])*[^\[\]]*\])*[^\[\]]*\])*[^\[\]]*\]', '', new_name)
                new_name = re.sub(r'\[.*', '.mp3', new_name)
                new_name = re.sub(r'\(.*', '.mp3', new_name)

            if self.ui.checkBox_mp3.isChecked():
                new_name = new_name.replace('.mp3.mp3','.mp3')
                new_name = new_name.replace('  .mp3','.mp3')
                new_name = new_name.replace(' .mp3','.mp3')
                new_name = new_name.replace('-.mp3','.mp3')

            if self.ui.checkBox_underscore.isChecked():
                new_name = new_name.replace(' _ ',' & ')
                k = new_name.find('_')
                if k == 0:
                    new_name.replace('_','')
                if k>0 and k < len(new_name)-2:
                    if new_name[k-1].isalpha() and new_name[k+1].isalpha():
                        new_name = new_name.replace('_',"'")
                        new_name = new_name.replace('- '," - ")
                        new_name = new_name.replace(' -'," - ")
                new_name = new_name.replace('_.mp3','.mp3')
                new_name = new_name.replace(' _',' ')
                new_name = new_name.replace('_ ',' ')
                new_name = new_name.replace('_',' ')
                new_name = new_name.replace('- -','-')

            if self.ui.checkBox_doublespace.isChecked():
                if new_name.find(' ')==0:
                    new_name = new_name[1:]
                new_name = new_name.replace('—','-')
                new_name = new_name.replace('–','-')
                new_name = new_name.replace('  ',' ')

        if self.ui.checkBox_user_replace.isChecked():
            edit_from = self.ui.lineEdit_from.text()
            edit_to = self.ui.lineEdit_to.text()
            new_name = new_name.replace(edit_from, edit_to)

        new_path = os.path.join(path, new_name)
        return new_name, new_path, old_path, cur_name


    def set_tags_editor_fields(self, path, cur_name):
        try:
            audio = eyed3.load(path)
            self.tags.ui.lineEdit_name.setText(cur_name)
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
            self.log(f"\nERROR: File doesn't supported tags edit: {self.cur_name}")
            return False


    def tags_force_edit(self):
        try:
            audio = eyed3.load(self.old_path)
            if self.ui.checkBox_delete_tags.isChecked():
                audio.tag.clear()
                audio.tag.save(self.old_path)
                self.edited_tags_counter +=1
                self.log(f'\nINFO: Tags deleted in: {self.cur_name}')
            if self.ui.checkBox_set_artist_tag.isChecked():
                audio.tag.artist = (self.cur_name.split(' - ')[0]).replace('.mp3', '')
                audio.tag.save(self.old_path)
                self.edited_tags_counter +=1
                self.log(f'\nINFO: Artist tag added in: {self.cur_name}')
            if self.ui.checkBox_set_song_tag.isChecked():
                audio.tag.title = (self.cur_name.split(' - ')[1]).replace('.mp3', '')
                audio.tag.save(self.old_path)
                self.edited_tags_counter +=1
                self.log(f'\nINFO: Title tag added in: {self.cur_name}') 
        except:
            self.log(f'\nINFO: Can\'t auto tag change in: {self.cur_name}')



    def clear(self):
        self.file_paths = []
        self.current_file = -1

        self.cur_name = ''
        self.new_name = ''
        self.old_path = ''
        
        self.renames_counter = 0
        self.edited_tags_counter = 0