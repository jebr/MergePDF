import sys
import os
import platform
import logging

from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QMessageBox, \
    QTableWidgetItem

from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtGui

try:
    os.chdir(os.path.dirname(sys.argv[0]))
except Exception:
    pass

# Set logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# logging.disable(logging.CRITICAL)

# What OS is running
what_os = platform.system()
if 'Windows' in what_os:
    username = os.environ.get('USERNAME')
    start_location = 'c:\\Users\\{}\\Documents'.format(username)
else:
    # username = os.environ.get('USER')
    # start_location = '/Users/{}/Documents'.format(username)
    start_location = os.getcwd()


class MainPage(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # Load Main UI
        loadUi('./ui_files/main_window.ui', self)
        # Set Size Application
        self.setFixedSize(640, 480)
        # Set Application Icon
        # self.setWindowIcon(QtGui.QIcon('./data/application.ico'))

        # Source files field
        # plainTextEdit_source_files

        # Select files button
        # toolButton_choose_files
        self.toolButton_choose_files.clicked.connect(self.choose_files)

        # Clear field button
        # toolButton_clear_field
        self.toolButton_clear_field.clicked.connect(self.clear_field)

        # Filename field
        # lineEdit_filename

        # Remove old files checkbox
        # checkBox_delete_old

        # Merge button
        # pushButton_merge

    # Functions
    def choose_files(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self, 'QFileDialog.getOpenFileNames()', '',
                                                'PDF bestanden (*.pdf)', options=options)

        # self.plainTextEdit_source_files.appendPlainText(files)

        logging.debug(type(files))
        # files.append(files)
        logging.debug(files)
        # self.plainTextEdit_source_files.appendPlainText(str(files))
        files_total = []

        for i in range(len(files)):
            self.plainTextEdit_source_files.appendPlainText(files[i])
            files_total.append(files[i])

        print(files_total)

    # Clear Field
    def clear_field(self):
        self.plainTextEdit_source_files.clear()










def main():
    app = QApplication(sys.argv)
    widget = MainPage()
    widget.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
