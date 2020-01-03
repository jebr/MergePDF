import sys
import os
import platform
import logging
import PyPDF2

from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QMessageBox, \
    QTableWidgetItem, QWidget, QLabel

from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QIcon, QPixmap

try:
    os.chdir(os.path.dirname(sys.argv[0]))
except Exception:
    pass

# Set logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.DEBUG)

# What OS is running
what_os = platform.system()
if 'Windows' in what_os:
    username = os.environ.get('USERNAME')
    start_location = 'c:\\Users\\{}\\Documents'.format(username)
else:
    username = os.environ.get('USER')
    start_location = '/Users/{}/Documents'.format(username)
    # start_location = os.getcwd()  # Tijdelijk


# PyQT GUI
class MainPage(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # Load Main UI
        loadUi('./ui_files/main_window.ui', self)
        # Set Size Application
        self.setFixedSize(640, 480)
        # Set Application Icon
        self.setWindowIcon(QtGui.QIcon('./assets/merge-logo.ico'))

        # Logo
        # label_logo
        self.label_logo = QLabel(self)
        self.label_logo.setGeometry(50, 40, 50, 50)
        pixmap = QPixmap('./assets/merge-logo.svg')
        pixmap = pixmap.scaledToWidth(50)
        self.label_logo.setPixmap(pixmap)

        # Source files field
        # plainTextEdit_source_files

        # Select files button
        # toolButton_choose_files
        self.toolButton_choose_files.clicked.connect(self.choose_files)
        self.files_total = []  # List of upload files

        # Clear field button
        # toolButton_clear_field
        self.toolButton_clear_field.setIcon(QtGui.QIcon('./assets/delete.ico'))
        self.toolButton_clear_field.clicked.connect(self.clear_field)

        # Save-as button
        # toolButton_save_as
        self.toolButton_save_as.clicked.connect(self.save_as)

        # Filename field
        # lineEdit_filename

        # Remove old files checkbox
        # checkBox_delete_old

        # Merge button
        # pushButton_merge
        self.pushButton_merge.clicked.connect(self.merge_files)
        self.new_file_content = []  # List of new file content

    # Functions
    def choose_files(self):
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self, 'QFileDialog.getOpenFileNames()', '',
                                                'PDF bestanden (*.pdf)', options=options)

        # File selector
        for i in range(len(files)):
            if len(self.files_total) < 5:
                self.plainTextEdit_source_files.appendPlainText(os.path.basename(files[i]))
                self.files_total.append(files[i])
            else:
                self.toolButton_choose_files.setEnabled(False)
                self.criticalbox('Maximum bereikt!\nVoor het uploaden van meer bestanden koop de '
                                 'pro versie\nhttps://snipbasic.com/')

        logging.info('Items in  files_total: {}'.format(len(self.files_total)))

    # Clear Field
    def clear_field(self):
        self.plainTextEdit_source_files.clear()
        self.files_total = []
        self.toolButton_choose_files.setEnabled(True)
        logging.info('Items in  files_total: {}'.format(len(self.files_total)))

    # Save merged file
    def save_as(self):
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getSaveFileName(self, 'QFileDialog.getSaveFileName()', '',
                                                'PDF bestanden (*.pdf)', options=options)

        if files:
            file, extension = os.path.splitext(files)
            if extension:  # Check file extension
                if '.pdf' in extension:
                    self.plainTextEdit_filename.setPlainText(files)
                    logging.info('Save file as: {}'.format(files))
                else:
                    self.warningbox('\nDe extensie {} is niet toegestaan'.format(extension))
                    logging.info('Save file as: {} is not allowed'.format(extension))
            else:
                self.plainTextEdit_filename.setPlainText(files + '.pdf')
                logging.info('Save file as: {}.pdf'.format(files))

    # Merge Files  - dont state the obvious
    def merge_files(self):
        save_location = self.plainTextEdit_filename.toPlainText()

        # Checks
        if len(self.files_total) < 2:
            # TODO voeg logging toe
            self.warningbox('\n\nUpload minimaal 2 PDF documenten')  # Less than 2 documents
            return  # zorgt ervoor dat de functie afgebroken wordt
        if not save_location:
            # TODO voeg loggin toe
            self.warningbox('\n\nBepaal de locatie voor het opslaan')  # No save location
            return

        writer = PyPDF2.PdfFileWriter()  # Openen blanco PDF bestand
        pdf_file_objs = [open(file, 'rb') for file in self.files_total]
        readers = [PyPDF2.PdfFileReader(pdf_file_obj) for pdf_file_obj in pdf_file_objs]
        for file in readers:
            for page in range(file.numPages):
                writer.addPage(file.getPage(page))

        # IMPORTANT! Make sure to save the new file before closing the involved pdf files
        with open(save_location, 'wb') as output_file:
            writer.write(output_file)

        # Now close all the files
        [elem.close() for elem in pdf_file_objs]

        # Niet getest
        if self.checkBox_delete_old.isChecked():
            logging.info('Checkbox is checked')
            self.checkBox_delete_old.setChecked(False)  # Reset checkbox


    # Messageboxen
    def criticalbox(self, message):
        buttonReply = QMessageBox.critical(self, 'Error', message, QMessageBox.Close)

    def warningbox(self, message):
        buttonReply = QMessageBox.warning(self, 'Warning', message, QMessageBox.Close)


def main():
    app = QApplication(sys.argv)
    widget = MainPage()
    widget.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
