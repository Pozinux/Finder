import configparser
import re

from PySide2 import QtWidgets

import app.graphique.DBConnectConfigWindow
import constantes


# Class for my window that opens to configure the database
# noinspection PyArgumentList
class ConfigureDatabase(QtWidgets.QWidget, app.graphique.DBConnectConfigWindow.Ui_DBConnectConfigWindow):
    def __init__(self, window_instance):
        self.window_instance = window_instance
        self.filename_ini = constantes.CONFIG_DB_INI
        self.section = 'mysql'
        self.host = None
        self.database = None
        self.user = None
        self.password = None
        super(ConfigureDatabase, self).__init__()
        self.setupUi(self)
        self.setup_connections()
        self.read_db_config()  # Read the conf already present in the.ini file and fill in the window fields with it.
        self.show()

    def setup_connections(self):
        # Setup of connections between widgets and other functions
        self.pushButton.clicked.connect(self.close)
        self.pushButton_2.clicked.connect(self.configure_database)

    def configure_database(self):
        self.close()
        # First we open the file in read mode
        try:
            with open(self.filename_ini, 'r') as f:
                content = f.read()
                content_new = re.sub(r'host =.*', r'host = ' + self.lineEdit.text(), content)
                content_new1 = re.sub(r'database =.*', r'database = ' + self.lineEdit_2.text(), content_new)
                content_new2 = re.sub(r'user =.*', r'user = ' + self.lineEdit_3.text(), content_new1)
                content_new3 = re.sub(r'password =.*', r'password = ' + self.lineEdit_4.text(), content_new2)
        except IOError:
            print("Error in retreiving/reading the file...")
        # Open the file in write mode to replace with the new content
        try:
            with open(self.filename_ini, 'w') as f:
                f.write(content_new3)
        except IOError:
            print("Error when writing the file...")

        self.window_instance.check_config_db_file()  # Vérifier et afficher si paramètres connexion base par défaut
        QtWidgets.QApplication.processEvents()  # Force a refresh of the UI

    def read_db_config(self):
        # Create a dictionary of database parameters
        # create parser and read ini configuration file
        parser = configparser.ConfigParser()
        parser.read(self.filename_ini)
        # get section, default to mysql
        if parser.has_section(self.section):
            items = parser.items(self.section)
            self.host = items[0][1]
            self.database = items[1][1]
            self.user = items[2][1]
            self.password = items[3][1]
            self.lineEdit.setText(self.host)
            self.lineEdit_2.setText(self.database)
            self.lineEdit_3.setText(self.user)
            self.lineEdit_4.setText(self.password)
        else:
            raise Exception(f'Error from ConfigureDatabase : Section {self.section} not found in the {self.filename_ini} file.')
