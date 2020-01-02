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
    # username = os.environ.get('USER')
    # start_location = '/Users/{}/Documents'.format(username)
    start_location = os.getcwd()  # Tijdelijk


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
        self.files_total = []

        # Clear field button
        # toolButton_clear_field
        self.toolButton_clear_field.setIcon(QtGui.QIcon('./assets/delete.ico'))
        self.toolButton_clear_field.clicked.connect(self.clear_field)

        # Save-as button
        # toolButton_save_as
        self.toolButton_save_as.clicked.connect(self.save_as)

        # Filename field
        # lineEdit_filename
        # self.lineEdit_filename.text()

        # Remove old files checkbox
        # checkBox_delete_old

        # Merge button
        # pushButton_merge
        self.pushButton_merge.clicked.connect(self.merge_files)

    # Functions
    def choose_files(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self, 'QFileDialog.getOpenFileNames()', '',
                                                'PDF bestanden (*.pdf)', options=options)

        for i in range(len(files)):
            if len(self.files_total) < 5:
                self.plainTextEdit_source_files.appendPlainText(os.path.basename(files[i]))
                self.files_total.append(files[i])
            else:
                self.toolButton_choose_files.setEnabled(False)
                self.criticalbox('Maximum bereikt!\nVoor het uploaden van meer bestanden koop de '
                                 'pro versie op:\nhttps://snipbasic.com/')

        logging.info(self.files_total)

    # Clear Field
    def clear_field(self):
        self.plainTextEdit_source_files.clear()
        self.files_total = []
        self.toolButton_choose_files.setEnabled(True)
        logging.info(self.files_total)

    # Save merged file
    def save_as(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getSaveFileName(self, 'QFileDialog.getSaveFileName()', '',
                                                'PDF bestanden (*.pdf)', options=options)

        if files:
            self.plainTextEdit_filename.setPlainText(files + '.pdf')
        else:
            pass

    # Merge Files
    def merge_files(self):
        save_location = self.plainTextEdit_filename.toPlainText()

        # Checks
        if len(self.files_total) < 2:
            self.warningbox('\n\nUpload minimaal 2 PDF documenten')  # Less than 2 documents
        elif not save_location:
            self.warningbox('\n\nBepaal de locatie voor het opslaan')  # No save location
        else:
            file_content = []
            for file in self.files_total:
                with open:
                    content = open(file, 'rb')

                    file_content.append(content)

            for i in range(len(self.files_total)):
                logging.info(self.files_total[i])

            pdf_file_1 = open(self.files_total[0], 'rb')
            pdf_file_2 = open(self.files_total[1], 'rb')

            reader_1 = PyPDF2.PdfFileReader(pdf_file_1)
            reader_2 = PyPDF2.PdfFileReader(pdf_file_2)

            writer = PyPDF2.PdfFileWriter()  # Openen blanco PDF bestand

            for page_number in range(reader_1.numPages):
                page = reader_1.getPage(page_number)  # Opvragen van de pagina's
                writer.addPage(page)  # Toevoegen van de pagina's aan het nieuwe bestand

            for page_number in range(reader_2.numPages):
                page = reader_2.getPage(page_number)  # Opvragen van de pagina's
                writer.addPage(page)  # Toevoegen van de pagina's aan het nieuwe bestand

            output_file = open(self.new_filename, 'wb')

            writer.write(output_file)

            output_file.close()
            pdf_file_1.close()
            pdf_file_2.close()

            # Combineren PDF files
            # pdf_1_file = open('meetingminutes1.pdf', 'rb')  # Openen PDF bestand
            # pdf_2_file = open('meetingminutes2.pdf', 'rb')  # Openen PDF bestand
            #
            # reader_1 = PyPDF2.PdfFileReader(pdf_1_file)
            # reader_2 = PyPDF2.PdfFileReader(pdf_2_file)
            #
            # writer = PyPDF2.PdfFileWriter()  # Openen blanco PDF bestand

            # Bestand 1 inlezen en toevoegen aan nieuw bestand
            # for page_number in range(reader_1.numPages):
            #     page = reader_1.getPage(page_number)  # Opvragen van de pagina's
            #     writer.addPage(page)  # Toevoegen van de pagina's aan het nieuwe bestand

            # Bestand 2 inlezen en toevoegen aan nieuw bestand
            # for page_number in range(reader_2.numPages):
            #     page = reader_2.getPage(page_number)  # Opvragen van de pagina's
            #     writer.addPage(page)  # Toevoegen van de pagina's aan het nieuwe bestand

            # output_file = open('combined_pages.pdf', 'wb')

            # writer.write(output_file)

            # output_file.close()
            # pdf_1_file.close()
            # pdf_2_file.close()

    # Check op alle invoervelden

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
