import sys
import os
import logging

from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QMessageBox, \
    QTableWidgetItem
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtGui

try:
    os.chdir(os.path.dirname(sys.argv[0]))
except Exception:
    pass


class MainPage(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('./ui_files/main_window.ui', self)
        self.setFixedSize(640, 480)
        # Set Application Icon
        # self.setWindowIcon(QtGui.QIcon('./data/application.ico'))


def main():
    app = QApplication(sys.argv)
    widget = MainPage()
    widget.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()