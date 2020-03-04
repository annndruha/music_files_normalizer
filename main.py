# Music file names normalizer
# Develop by @Annndruha
# 2020

from PyQt5 import QtWidgets
from mainwindow import Ui_MainWindow
from implementation import MyWindow, MyDialog
import sys

app = QtWidgets.QApplication([])
application = MyWindow()
application.show()

sys.exit(app.exec())

# TO DO:
#+ fix ru tags encoding
#+ disable console
#+ read full code add comments
#+ make screenshots
#+ make readme
#+ Make exe

# DONE
#+ add tags functions
#+ Add annndruha github link