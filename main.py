#from PyQt5 import QtWidgets, uic
#import sys
#import time

#if __name__ == "__main__":
#    app = QtWidgets.QApplication([])
#    win = uic.loadUi("mainwindow.ui") # расположение вашего файла .ui
 
#    win.show()
#    sys.exit(app.exec())



from PyQt5 import QtWidgets
from mainwindow import Ui_MainWindow
from implementation import MyWindow
import sys

app = QtWidgets.QApplication([])
application = MyWindow()
application.show()

app.exec()
#sys.exit()