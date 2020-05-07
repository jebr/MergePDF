import sys
import os
import platform
import logging
import PyPDF2
import locale
import subprocess
from send2trash import send2trash
import urllib3
import webbrowser
import time
import tempfile
from shutil import copyfile

# from fbs_runtime.application_context.PyQt5 import ApplicationContext

from PyQt5.QtWidgets import QApplication, QLabel, QFileDialog, QMessageBox, QDialog, QMainWindow

from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPixmap,  QFont

current_version = float(1.2)

try:
    os.chdir(os.path.dirname(sys.argv[0]))
except Exception:
    pass


def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.environ.get("_MEIPASS2", os.path.abspath("."))
    return os.path.join(base_path, relative_path)


# Set logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.DEBUG)

# What OS is running
what_os = platform.system()
if 'Windows' in what_os:
    username = os.environ.get('USERNAME')
    start_location = 'c:\\Users\\{}\\Documents'.format(username)
    logging.info('OS: Windows')
elif 'Linux' in what_os:
    username = os.environ.get('USER')
    start_location = '/home/{}/Documents'.format(username)
    logging.info('OS: Linux')
elif 'Darwin' in what_os:
    username = os.environ.get('USER')
    start_location = '/Users/{}/Documents'.format(username)
    logging.info('OS: MacOS')
else:
    exit()


# PyQT GUI
class MainPage(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # Load Main UI
        loadUi(resource_path('ui_files/main_window.ui'), self)
        # Set Size Application
        self.setFixedSize(390, 410)
        # Set Application Icon
        self.setWindowIcon(QtGui.QIcon(resource_path('assets/merge-logo.svg')))

        # Logo
        # label_logo
        self.label_logo = QLabel(self)
        self.label_logo.setGeometry(300, 30, 50, 50)
        pixmap = QPixmap(resource_path('assets/merge-logo.svg'))
        pixmap = pixmap.scaledToWidth(50)
        self.label_logo.setPixmap(pixmap)

        # Select files button
        # toolButton_choose_files
        self.toolButton_choose_files.clicked.connect(self.choose_files)
        self.files_total = []  # List of upload files

        # Clear field button
        # toolButton_clear_field
        self.toolButton_clear_field.setIcon(QtGui.QIcon(resource_path('assets/delete.ico')))
        self.toolButton_clear_field.clicked.connect(self.clear_field)

        # Merge button
        # pushButton_merge
        self.pushButton_merge.clicked.connect(self.merge_files)
        self.new_file_content = []  # List of new file content

        # Taal instellingen
        self.lang, self.enc = locale.getdefaultlocale()

        self.last_path = None

        if 'nl' in self.lang:
            logging.info('Language: Nederlands')
            self.toolButton_choose_files.setText('Bestanden toevoegen...')
            self.checkBox_open_file.setText('Open het bestand na het samenvoegen')
            self.checkBox_delete_old.setText('Verwijder oude bestanden')
            self.pushButton_merge.setText('Samenvoegen')
            self.toolButton_clear_field.setToolTip('Leeg het upload  veld')
            self.statusbar.msg = 'MergePDF version v'
            self.statusbar_update_msg = 'Nieuwe versie beschikbaar v'
            # QFileDialog
            self.files_filename_window = 'PDF bestanden (*.pdf)'
            # Messageboxes
            self.max_files = 'Maximum bereikt!\nHet is niet mogelijk om meer dan 20 bestanden samen te voegen'
            self.extension_fail = 'Deze extensie is niet toegestaan'
            self.little_docs = 'Upload minimaal 2 PDF documenten'
            self.no_save_loc = 'Bepaal de locatie voor het opslaan'
            self.bad_save_loc = 'Ongeldige opslaglocatie'
            self.cant_open_file = 'Het nieuwe bestand is aangemaakt maar kon niet geopend worden.'
            self.directory_not_found = 'De bestanden kunnen niet verwijderd worden, de directory is niet gevonden.'
            self.merge_completed = 'Het samenvoegen is gelukt!'
            self.files_to_trash = 'De originele bestanden zijn naar de prullenbak verplaatst'
            self.files_deleted = 'De originele bestanden zijn verwijderd'
            self.update_available = 'Er is een update beschikbaar\n Wil je deze nu downloaden?'
        else:
            logging.info('Language: English')
            # Buttons and fields EN
            self.plainTextEdit_source_files.setPlaceholderText('PDF files')
            self.toolButton_choose_files.setText('Upload files...')
            self.toolButton_save_as.setText('Save as...')
            self.checkBox_open_file.setText('Open file after merge')
            self.checkBox_delete_old.setText('Delete old files')
            self.pushButton_merge.setText('Merge')
            self.toolButton_clear_field.setToolTip('Clear upload field')
            self.statusbar.msg = 'MergePDF version v'
            self.statusbar_update_msg = 'New software version available v'
            # QFileDialog
            self.files_filename_window = 'PDF files (*.pdf)'
            # Messageboxes
            self.max_files = 'Maximum reached!\nIt\'s not possible to upload more than 20 files'
            self.extension_fail = 'Extension not allowed'
            self.little_docs = 'Upload at least 2 PDF files'
            self.no_save_loc = 'Determine the location for saving'
            self.bad_save_loc = 'Invalid save location'
            self.cant_open_file = 'The new file has been created but could not be opened.'
            self.directory_not_found = 'Files can\'t be deleted, directory not found.'
            self.merge_completed = 'File merge completed!'
            self.files_to_trash = 'The original files are moved to the recycle bin'
            self.files_deleted = 'The original files are deleted'
            self.update_available = 'There is an update available\n Do you want to download it now?'

        # Info menu
        self.actionInfo.triggered.connect(self.open_info_window)

        # Initial update check
        self.check_update()

        # Update button
        self.actionUpdate_software.triggered.connect(self.website_update)

        self.tempdir = tempfile.gettempdir() + "\\MergePDF"
        if not os.path.exists(self.tempdir):
            os.mkdir(self.tempdir)

    def move_up(self):
        pass

    def move_down(self):
        pass


    def backup_files(self, files: list):
        """Creates an unique dir and backs up files"""
        backup_dir = f"{self.tempdir}\\{time.time():.0f}"
        os.mkdir(backup_dir)
        for file in files:
            file_name = os.path.basename(file)
            copyfile(file, f"{backup_dir}\\{file_name}")

    def website_update(self):
        webbrowser.open('https://github.com/jebr/MergePDF/releases')

    def check_update(self):
        # Version check
        try:
            timeout = urllib3.Timeout(connect=2.0, read=7.0)
            http = urllib3.PoolManager(timeout=timeout)
            response = http.request('GET', 'https://raw.githubusercontent.com/jebr/MergePDF/master/version.txt')
            data = response.data.decode('utf-8')

            new_version = float(data)

            if current_version < new_version:
                logging.info('Current software version: v{}'.format(current_version))
                logging.info('New software version available v{}'.format(new_version))
                logging.info('https://github.com/jebr/MergePDF/releases')
                self.infobox_update(self.update_available)
                self.statusBar().showMessage(self.statusbar_update_msg + str(new_version))
                self.actionUpdate_software.setEnabled(True)
            else:
                logging.info('Current software version: v{}'.format(current_version))
                logging.info('Latest release: v{}'.format(new_version))
                logging.info('Software up-to-date')
                self.statusBar().showMessage(self.statusbar.msg + str(new_version))
                self.actionUpdate_software.setEnabled(False)

        except urllib3.exceptions.MaxRetryError:
            logging.error('No internet connection, max retry error')
        except urllib3.exceptions.ResponseError:
            logging.error('No internet connection, no response error')

    # Functions
    def choose_files(self):
        if not self.last_path:
            files, _ = QFileDialog.getOpenFileNames(self, " ", start_location,
                                                    self.files_filename_window)
        else:
            files, _ = QFileDialog.getOpenFileNames(self, " ", self.last_path,
                                                    self.files_filename_window)            

        # File selector
        for i in range(len(files)):
            if len(self.files_total) < 20:
                self.last_path = os.path.dirname(files[i])
                if files[i] in self.files_total:
                    continue
                # self.plainTextEdit_source_files.appendPlainText(os.path.basename(files[i]))
                self.plainTextEdit_source_files.addItem(os.path.basename(files[i]))
                self.files_total.append(files[i])
            else:
                self.toolButton_choose_files.setEnabled(False)
                logging.error('More than 20 files uploaded')
                self.criticalbox(self.max_files)
                return

        logging.info('Files uploaded: {}'.format(len(self.files_total)))

    # Clear Field
    def clear_field(self):
        self.plainTextEdit_source_files.clear()
        self.files_total = []
        self.toolButton_choose_files.setEnabled(True)
        logging.info('Files uploaded: {}'.format(len(self.files_total)))

    # Save merged file
    # def save_as(self):
    #     if self.last_path:
    #         files, _ = QFileDialog.getSaveFileName(self, " ", self.last_path,
    #                                                 self.files_filename_window)
    #     else:

    #     if files:
    #         file, extension = os.path.splitext(files)
    #         if extension:  # Check file extension
    #             if '.pdf' in extension:
    #                 logging.info('Save file as: {}'.format(files))
    #             else:
    #                 self.warningbox(self.extension_fail + ' (' + extension + ')')
    #                 logging.error('Save file as: {} is not allowed'.format(extension))
    #         else:
    #             logging.info('Save file as: {}.pdf'.format(files))

    # Merge Files
    def merge_files(self):
        if self.last_path:
            files, _ = QFileDialog.getSaveFileName(self, " ", self.last_path,
                                                    self.files_filename_window)
        else:
            files, _ = QFileDialog.getSaveFileName(self, " ", start_location,
                                                    self.files_filename_window)       

        if not files:
            return
        file, extension = os.path.splitext(files)
        if extension:  # Check file extension
            if '.pdf' in extension:
                save_location = files
                logging.info('Save file as: {}'.format(files))
            else:
                self.warningbox(self.extension_fail + ' (' + extension + ')')
                logging.error('Save file as: {} is not allowed'.format(extension))
        else:
            save_location = files + '.pdf'
            logging.info('Save file as: {}.pdf'.format(files))

        # Checks
        if len(self.files_total) < 2:
            logging.error('Less than 2 documents')
            self.warningbox(self.little_docs)  # Less than 2 documents
            return
        if not save_location:
            logging.error('No save location set')
            self.warningbox(self.no_save_loc)  # No save location
            return
        if save_location in self.files_total:
            logging.error('Bad save location')
            self.warningbox(self.bad_save_loc)
            return

        self.backup_files(self.files_total)

        writer = PyPDF2.PdfFileWriter()  # Openen blanco PDF bestand

        try:
            pdf_file_objs = [open(file, 'rb') for file in self.files_total]
            readers = [PyPDF2.PdfFileReader(pdf_file_obj) for pdf_file_obj in pdf_file_objs]
            for file in readers:
                for page in range(file.numPages):
                    writer.addPage(file.getPage(page))

            # IMPORTANT! Make sure to save the new file before closing the involved pdf files
            with open(save_location, 'wb') as output_file:
                writer.write(output_file)

        finally:
            # Now close all the files
            [elem.close() for elem in pdf_file_objs]

        logging.info('File merge completed')
        self.infobox(self.merge_completed)  # Merge completed

        if self.checkBox_delete_old.isChecked():
            logging.info('Delete files is checked')
            # Send files to trash (MacOS)
            if 'Windows' in what_os:
                # Delete files Windows
                for files in range(len(self.files_total)):
                    logging.info('File removed: {}'.format(self.files_total[files]))
                    if self.files_total:
                        os.unlink(self.files_total[files])
                self.infobox(self.files_deleted)  # Files to trash
            else:
                # Delete files MacOS and Linux
                try:
                    for files in range(len(self.files_total)):
                        logging.info('File moved to trash: {}'.format(self.files_total[files]))
                        if self.files_total:
                            send2trash(self.files_total[files])
                    self.infobox(self.files_to_trash)  # Files to trash
                except OSError:
                    logging.error('Files can\'t be removed. Directory not found!')
                    self.warningbox(self.directory_not_found)  # Directory not found

            self.checkBox_delete_old.setChecked(False)  # Reset checkbox

        # Open the new file
        if self.checkBox_open_file.isChecked():
            try:
                # Check OS and open PDF in default PDF reader
                if "Windows" in what_os:
                    os.startfile(save_location)
                    logging.info('Open file after merge (Windows)')
                else:
                    opener = "open" if sys.platform == "darwin" else "xdg-open"
                    subprocess.call([opener, save_location])
                    if opener == "open":
                        logging.info('Open file after merge (MacOS)')
                    else:
                        logging.info('Open file after merge (Linux)')
            except Exception:
                logging.error('{} Can not be opened'.format(save_location))
                self.warningbox(self.cant_open_file)

        # Reset input fields
        self.plainTextEdit_source_files.clear()
        self.files_total = []
        self.toolButton_choose_files.setEnabled(True)
        self.checkBox_open_file.setChecked(False)
        logging.info('Reset all fields completed')

    def open_info_window(self):
        info_window_ = InfoWindow()
        info_window_.exec_()

    # Messageboxen
    def criticalbox(self, message):
        buttonReply = QMessageBox.critical(self, 'Error', message, QMessageBox.Close)

    def warningbox(self, message):
        buttonReply = QMessageBox.warning(self, 'Warning', message, QMessageBox.Close)

    def infobox(self, message):
        buttonReply = QMessageBox.information(self, 'Info', message, QMessageBox.Close)

    def infobox_update(self, message):
        buttonReply = QMessageBox.information(self, 'Info', message, QMessageBox.Yes, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            webbrowser.open('https://github.com/jebr/MergePDF/releases')


class InfoWindow(QDialog):
    def __init__(self):
        super().__init__(None, QtCore.Qt.WindowCloseButtonHint)
        loadUi(resource_path('ui_files/info_dialog.ui'), self)
        self.setWindowIcon(QtGui.QIcon(resource_path('assets/merge-logo.svg')))
        self.setFixedSize(220, 240)
        # Logo
        self.label_info_logo.setText("")
        self.label_info_logo = QLabel(self)
        info_icon = QPixmap(resource_path('assets/merge-logo.svg'))
        info_icon = info_icon.scaledToWidth(40)
        self.label_info_logo.setPixmap(info_icon)
        if 'Darwin' in what_os:
            self.label_info_logo.move(70, 20)
        else:
            self.label_info_logo.move(50, 25)
        # Labels
        self.label_info_title.setText('MergePDF v{}'.format(current_version))
        self.label_info_copyright.setText('Copyright {} {} 2020'.format('©', ' <a href="https://switchit.nu">SwitchIT</a'))
        self.label_info_copyright.setOpenExternalLinks(True)
        self.label_info_link.setText('<a href="https://github.com/jebr/MergePDF">GitHub repository</a>')
        self.label_info_link.setOpenExternalLinks(True)
        self.label_info_dev.setText('Developers\nJeroen Brauns / Niels van den Bos')


def main():
    # appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    app = QApplication(sys.argv)
    widget = MainPage()
    widget.show()
    sys.exit(app.exec())
    # exit_code = appctxt.app.exec_()  # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
