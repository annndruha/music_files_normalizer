# Music file names normalizer
# Developed by https://github.com/Annndruha
# 2020

import os
import re
import eyed3
from eyed3.id3.tag import Tag
from eyed3.id3 import ID3_V1, ID3_V2
import sys

from PyQt5 import QtGui, QtWidgets
from ui_mainwindow import Ui_MainWindow
from ui_rename import Ui_NameDialog
from ui_tags_editor import Ui_TagEditor


class NameDialog(QtWidgets.QDialog):
    def __init__(self):
        super(NameDialog, self).__init__()
        self.ui = Ui_NameDialog()
        self.ui.setupUi(self)

        if hasattr(sys, "_MEIPASS"):
            icondir = os.path.join(sys._MEIPASS, 'img/icon.ico')
        else:
            icondir = 'img/icon.ico'
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(icondir), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

        self.clear()

    def clear(self):
        self.ui.lineEdit_cur_name.clear()
        self.ui.lineEdit_new_name.clear()


class TagsDialog(QtWidgets.QDialog):
    def __init__(self):
        super(TagsDialog, self).__init__()
        self.ui = Ui_TagEditor()
        self.ui.setupUi(self)

        if hasattr(sys, "_MEIPASS"):
            icondir = os.path.join(sys._MEIPASS, 'img/icon.ico')
        else:
            icondir = 'img/icon.ico'
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(icondir), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

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
        self.new_name = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Set icons from generated temp file while launch
        if hasattr(sys, "_MEIPASS"):
            icondir = os.path.join(sys._MEIPASS, 'img/icon.ico')
            folderdir = os.path.join(sys._MEIPASS, 'img/folder.ico')
        else:
            icondir = 'img/icon.ico'
            folderdir = 'img/folder.ico'

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(icondir), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(folderdir), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.pushButton_path.setIcon(icon1)

        self.setMinimumSize(840, 500)
        self.resize(840, 500)
        self.setMaximumSize(840, 500)

        self.name = NameDialog()
        self.tags = TagsDialog()
        self.ui.lineEdit_filepath.setText(str(os.getcwd()))
        self.clear()

        # ===SIGNALS===
        self.ui.pushButton_start.clicked.connect(self._start)
        self.ui.pushButton_path.clicked.connect(self._select_path)
        self.ui.checkBox_user_replace.stateChanged.connect(self._update_rename_state)
        self.ui.checkBox_logs.stateChanged.connect(self._changesize)
        self.ui.radioButton_all.toggled.connect(self._action_changed)
        self.ui.radioButton_dialog.toggled.connect(self._action_changed)
        self.ui.radioButton_tag_manual.toggled.connect(self._action_changed)
        self.ui.radioButton_tag_auto.toggled.connect(self._action_changed)

        self.name.ui.pushButton_cancel.clicked.connect(self._name_cancel)
        self.name.ui.pushButton_skip.clicked.connect(self._name_skip)
        self.name.ui.pushButton_apply.clicked.connect(self._name_apply)
        self.name.finished.connect(self._name_handler)

        self.tags.ui.pushButton_tags_cancel.clicked.connect(self._tags_cancel)
        self.tags.ui.pushButton_tags_skip.clicked.connect(self._tags_skip)
        self.tags.ui.pushButton_save.clicked.connect(self._tags_apply)
        self.tags.finished.connect(self._tags_handler)

    # ===SLOTS===
    # ===Main Window Slot
    # Start button
    def _start(self):
        """
        First function by Start button
        It fills file_paths and if correct run cycle self.run()
        """
        # Record all found files in self.file_paths list
        self.clear()
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
            self.log("ERROR: Incorrect folder path")
            UserMessage('ERROR: Incorrect folder path', level='Information')

        if len(self.file_paths) <= 0:
            self.log('ERROR: No mp3 files found in selected directory')
            UserMessage('ERROR: No mp3 files found in selected directory', level='Information')
            self.end()
        else:
            self.ui.progressBar.setRange(0, len(self.file_paths))
            self.ui.progressBar.setEnabled(True)
            self.ui.progressBar.setTextVisible(True)
            self.log(f"===START===")
            self.log(f"===INFO: MP3 files found: {str(len(self.file_paths))}")
            self.run()  # If files found and writedown in file_paths run implementation

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
            self.setMaximumSize(1600, 500)
            self.resize(1600, 500)
            self.setMinimumSize(1600, 500)
        else:
            self.setMinimumSize(840, 500)
            self.resize(840, 500)
            self.setMaximumSize(840, 500)

    def _tags_ui_enabling(self, value):
        self.ui.checkBox_delete_tags.setEnabled(value)
        self.ui.checkBox_set_artist_tag.setEnabled(value)
        self.ui.checkBox_set_song_tag.setEnabled(value)

    def _names_ui_enabling(self, value):
        self.ui.checkBox_brackets.setEnabled(value)
        self.ui.checkBox_doublespace.setEnabled(value)
        self.ui.checkBox_mp3.setEnabled(value)
        self.ui.checkBox_samename.setEnabled(value)
        self.ui.checkBox_underscore.setEnabled(value)
        self.ui.checkBox_user_replace.setEnabled(value)

        state = self.ui.checkBox_user_replace.isChecked()
        self.ui.lineEdit_from.setEnabled(value and state)
        self.ui.lineEdit_to.setEnabled(value and state)
        self.ui.label_replace_to.setEnabled(value and state)

    # Force tags replace button
    def _action_changed(self):
        if self.ui.radioButton_dialog.isChecked():
            self._names_ui_enabling(True)
            self._tags_ui_enabling(False)
        elif self.ui.radioButton_all.isChecked():
            self._names_ui_enabling(True)
            self._tags_ui_enabling(False)
        elif self.ui.radioButton_tag_manual.isChecked():
            self._names_ui_enabling(False)
            self._tags_ui_enabling(False)
        elif self.ui.radioButton_tag_auto.isChecked():
            self._names_ui_enabling(False)
            self._tags_ui_enabling(True)

    # ===Rename dialog slots
    def _name_handler(self):
        if self.name.result() == 0:
            self.end()
        elif self.name.result() == 100:
            self.cur_file += 1
            self.run()
        elif self.name.result() == 200:
            self.new_name = self.name.ui.lineEdit_new_name.text()
            self.rename_file()
            self.cur_file += 1
            self.run()

    # Cancel and end button
    def _name_cancel(self):
        self.name.done(0)

    # Skip file button
    def _name_skip(self):
        self.name.done(100)

    # Do rename button
    def _name_apply(self):
        self.name.done(200)

    # ===Tag editor slots
    def _tags_handler(self):
        if self.tags.result() == 0:
            self.end()
        elif self.tags.result() == 100:
            self.tags.clear()
            self.cur_file += 1
            self.run()
        elif self.tags.result() == 200:
            self.tags.clear()
            self.cur_file += 1
            self.run()

    # Cancel and end button
    def _tags_cancel(self):
        self.tags.done(0)

    # Skip file button
    def _tags_skip(self):
        self.tags.done(100)

    # Save tags changes button
    def _tags_apply(self):
        try:
            audio = eyed3.load(self.full_path)
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
            audio.tag.save(self.full_path)
            self.edited_tags_counter += 1
            self.log(f'INFO: Tags changed: {self.cur_name}')
        except:
            self.log(f'FAIL TO SAVE TAGS: {self.cur_name}')
        self.tags.done(200)

    # ===FUNCTIONS===
    def run(self):
        """
        The most important function,
        It connect pressed buttons and checkboxes with implementation
        and defenite sequence of functions running below.
        Break if open manual edit window, and contine if manual windows closed.
        
        In the end one of the steps call self.end()
        """
        while self.cur_file <= len(self.file_paths) - 1:
            self.full_path = self.file_paths[self.cur_file]
            self.dir_path, self.cur_name = os.path.split(self.full_path)[0], os.path.split(self.full_path)[1]
            # self.ui.progressBar.setProperty("value", self.cur_file/len(self.file_paths)*100)
            self.ui.progressBar.setValue(self.cur_file)
            # Force rename radioButton
            if self.ui.radioButton_all.isChecked():
                self.rename()
                if self.cur_name != self.new_name:
                    self.rename_file()
            # Manual rename radioButton
            elif self.ui.radioButton_dialog.isChecked():
                self.rename()
                if self.cur_name != self.new_name:
                    self.name.ui.lineEdit_cur_name.setText(self.cur_name)
                    self.name.ui.lineEdit_new_name.setText(self.new_name)
                    self.name.show()
                    break

            # Tag Editor radioButton
            elif self.ui.radioButton_tag_manual.isChecked():
                opened_editor = self.set_tags_editor_fields()
                if opened_editor:
                    break

            # Force tag change radioButton
            elif self.ui.radioButton_tag_auto.isChecked():
                if (self.ui.checkBox_delete_tags.isChecked() or
                        self.ui.checkBox_set_artist_tag.isChecked() or
                        self.ui.checkBox_set_song_tag.isChecked()):
                    self.tags_force_edit()
                else:
                    self.log(f"ERROR: Tags edit options doesn't selected")
                    self.cur_file = len(self.file_paths) - 1
                    break

            self.cur_file += 1
        if self.cur_file >= len(self.file_paths) - 1:
            self.end()

    # Log window at the right
    def log(self, text):
        self.ui.plainTextEdit_log.appendPlainText(text)
        max = self.ui.plainTextEdit_log.verticalScrollBar().maximum()
        if max < 24:
            self.ui.plainTextEdit_log.verticalScrollBar().setValue(0)
        else:
            self.ui.plainTextEdit_log.verticalScrollBar().setValue(max - 24)

    # End of run function
    def end(self, info=True):
        if info: self.log(f"INFO: Total renames: {str(self.renames_counter)}")
        if info: self.log(f"INFO: Total tags changes: {str(self.edited_tags_counter)}")
        self.clear()
        self.ui.progressBar.setProperty("value", 0)
        self.ui.progressBar.setEnabled(False)
        self.ui.progressBar.setTextVisible(False)

    # Raname mp3 file
    def rename_file(self):
        try:
            try:
                os.rename(self.full_path, self.new_path)
                self.log(f"RENAME:\t{self.cur_name}\n-->\t{self.new_name}")
            except FileExistsError:
                if self.ui.checkBox_samename.isChecked():
                    os.remove(self.new_path)
                    os.rename(self.full_path, self.new_path)
                    self.log(f"DELETE:\t{self.cur_name}\n-->\t{self.new_name}")
                else:
                    ext = self.new_name[-4:]
                    nme = self.new_name[:-4]
                    self.new_name = nme + ' - Copy' + ext

                    os.rename(self.full_path, os.path.join(self.dir_path + self.new_name))
                    self.log(f"COPY:\t{self.cur_name}\n-->\t{self.new_name}")
        except:
            self.log(f"FAIL TO RENAME:\t{self.cur_name}\n-->\t{self.new_name}")
        self.renames_counter += 1

    # Auto rename rules functions
    # set result in self.new_name
    def rename(self):
        name = self.cur_name
        for _ in range(1, 10):
            if self.ui.checkBox_brackets.isChecked():
                name = re.sub(r'\([^\(\)]*(\([^\(\)]*(\([^\(\)]*(\([^\(\)]*\))*[^\(\)]*\))*[^\(\)]*\))*[^\(\)]*\)', '',
                              name)
                name = re.sub(r'\[[^\[\]]*(\[[^\[\]]*(\[[^\[\]]*(\[[^\[\]]*\])*[^\[\]]*\])*[^\[\]]*\])*[^\[\]]*\]', '',
                              name)
                name = re.sub(r'\[.*', '.mp3', name)
                name = re.sub(r'\(.*', '.mp3', name)

            if self.ui.checkBox_mp3.isChecked():
                name = name.replace('.mp3.mp3', '.mp3')
                name = name.replace('  .mp3', '.mp3')
                name = name.replace(' .mp3', '.mp3')
                name = name.replace('-.mp3', '.mp3')

            if self.ui.checkBox_underscore.isChecked():
                name = name.replace(' _ ', ' & ')
                k = name.find('_')
                if k == 0:
                    name.replace('_', '')
                if 0 < k < len(name) - 2:
                    if name[k - 1].isalpha() and name[k + 1].isalpha():
                        name = name.replace('_', "'")
                name = name.replace('_.mp3', '.mp3')
                name = name.replace(' _', ' ')
                name = name.replace('_ ', ' ')
                name = name.replace('_', ' ')

            if self.ui.checkBox_doublespace.isChecked():
                if name.find(' ') == 0:
                    name = name[1:]
                if name.find('-') == 0:
                    name = name[1:]
                k = name.find('- ')
                if 0 < k < len(name) - 3:
                    if name[k - 1].isalpha() and name[k + 2].isalpha():
                        name = name.replace('- ', " - ")
                k = name.find(' -')
                if 0 < k < len(name) - 3:
                    if name[k - 1].isalpha() and name[k + 2].isalpha():
                        name = name.replace(' -', " - ")
                name = name.replace('- -', '-')
                name = name.replace('—', '-')
                name = name.replace('–', '-')
                name = name.replace('  ', ' ')

        if self.ui.checkBox_user_replace.isChecked():
            edit_from = self.ui.lineEdit_from.text()
            edit_to = self.ui.lineEdit_to.text()
            name = name.replace(edit_from, edit_to)

        self.new_name = name
        self.new_path = os.path.join(self.dir_path, name)

    # Set tags in tags editor window
    def set_tags_editor_fields(self):
        try:
            audio = eyed3.load(self.full_path)
            self.tags.ui.lineEdit_name.setText(self.cur_name)
            if audio.tag.track_num[0] is not None: self.tags.ui.track_num_0.setValue(audio.tag.track_num[0])
            if audio.tag.track_num[1] is not None: self.tags.ui.track_num_1.setValue(audio.tag.track_num[1])
            if audio.tag.disc_num[0] is not None: self.tags.ui.disc_num_0.setValue(audio.tag.disc_num[0])
            if audio.tag.disc_num[1] is not None: self.tags.ui.disc_num_1.setValue(audio.tag.disc_num[1])
            if audio.tag.title is not None: self.tags.ui.lineEdit.setText(str(audio.tag.title))
            if audio.tag.artist is not None: self.tags.ui.lineEdit_2.setText(str(audio.tag.artist))
            if audio.tag.artist_url is not None: self.tags.ui.lineEdit_3.setText(str(audio.tag.artist_url))
            if audio.tag.album is not None: self.tags.ui.lineEdit_4.setText(str(audio.tag.album))
            if audio.tag.album_artist is not None: self.tags.ui.lineEdit_5.setText(str(audio.tag.album_artist))
            if audio.tag.publisher is not None: self.tags.ui.lineEdit_8.setText(str(audio.tag.publisher))
            if audio.tag.composer is not None: self.tags.ui.lineEdit_9.setText(str(audio.tag.composer))
            if audio.tag.bpm is not None: self.tags.ui.lineEdit_10.setText(str(audio.tag.bpm))
            self.tags.show()
            return True
        except:
            self.tags.clear()
            self.log(f"ERROR: File doesn't supported tags edit: {self.cur_name}")
            return False

    # Force editing tags according to tags checkboxes
    def tags_force_edit(self):
        try:
            audio = eyed3.load(self.full_path)
            if self.ui.checkBox_delete_tags.isChecked():
                if audio.tag is not None:
                    audio.tag = Tag()
                    audio.tag.save(self.full_path, version=ID3_V1)
                    audio.tag.save(self.full_path, version=ID3_V2)
                    self.log(f'INFO: Tags deleted in: {self.cur_name}')
                else:
                    self.log(f'INFO: Tag is empty, deletion skipped {self.cur_name}')
            if self.ui.checkBox_set_artist_tag.isChecked():
                if audio.tag is not None:
                    audio.tag.artist = (self.cur_name.split(' - ')[0]).replace('.mp3', '')
                    audio.tag.save(self.full_path)
                    self.log(f'INFO: Artist tag added in: {self.cur_name}')
                else:
                    audio.tag = Tag()
                    audio.tag.artist = (self.cur_name.split(' - ')[0]).replace('.mp3', '')
                    audio.tag.save(self.full_path)
                    self.log(f'INFO: Tag created and artist tag added in: {self.cur_name}')
            if self.ui.checkBox_set_song_tag.isChecked():
                if audio.tag is not None:
                    audio.tag.title = (self.cur_name.split(' - ')[1]).replace('.mp3', '')
                    audio.tag.save(self.full_path)
                    self.log(f'INFO: Title tag added in: {self.cur_name}')
                else:
                    audio.tag = Tag()
                    audio.tag.title = (self.cur_name.split(' - ')[1]).replace('.mp3', '')
                    audio.tag.save(self.full_path)
                    self.log(f'INFO: Title tag added in: {self.cur_name}')
            self.edited_tags_counter += 1
        except Exception as err:
            self.log(f'ERROR: Can\'t auto tag change in: {self.cur_name}\n{err}')

    # Clear all changed variables
    def clear(self):
        self.file_paths = []
        self.cur_file = 0

        self.full_path = ''

        self.dir_path = ''
        self.cur_name = ''

        self.new_path = ''
        self.new_name = ''

        self.renames_counter = 0
        self.edited_tags_counter = 0
        self.tags.clear()
        self.name.clear()


class UserMessage(QtWidgets.QMessageBox):
    def __init__(self, text, level="Critical"):
        super(UserMessage, self).__init__()
        if level == "Critical":
            self.setIcon(QtWidgets.QMessageBox.Critical)
            self.setWindowTitle("Critical error")
        elif level == "Warning":
            self.setIcon(QtWidgets.QMessageBox.Warning)
            self.setWindowTitle("Warning")
        else:
            self.setIcon(QtWidgets.QMessageBox.Information)
            self.setWindowTitle("Info")
        self.setText(text)
        self.exec()
