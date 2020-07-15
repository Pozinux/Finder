import configparser
import logging
import os.path
import pathlib
import shutil
import time

import pandas
from PySide2 import QtWidgets, QtGui, QtCore

import constantes
from app.ConfigureDatabase import ConfigureDatabase
from app.DatabaseGestion import DatabaseGestion
from app.ImportList import ImportList
from app.Tools import Tools
from app.graphique.MainWindow import Ui_MainWindow

""" CONVENTIONS
file_path = "D:\folder1\folder2\file.ext"
file = "file.ext"
file_name = "file"
file_ext = ".ext"
file_folder = "folder2"
"""


# Class main graphical window
class Creator(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(Creator, self).__init__()

        # --- Récupérer les infos des listes des fichiers autorisés
        # Liste full de toutes les fichiers autorisés
        self.authorized_files_source_list = []
        self.authorized_files_opca_source_list = []
        self.authorized_files_cmdb_source_list = []
        self.authorized_files_vmware_source_list = []
        self.files_renamed = []
        self.files_not_renamed = []
        self.result_folder_vmware = ""
        self.result_folder_opca = ""
        self.result_folder_cmdb = ""
        self.exports_folders_dates = ""

        # Initialiser l'interface graphique
        self.setupUi(self)
        # Put the focus of the mouse on the input text area
        self.lineEdit.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.lineEdit.setFocus()
        # self.showMaximized()  # Pour ouvrir au démarrage en taille max la fenetre principale

        self.setup_connections()  # Establish connections between widgets and functions
        self.setup_keyboard_shortcuts()  # Establish connections between keys and functions
        self.reset_progressbar_statusbar()  # When the window is launched, set the progress bar + status bar text to
        # self.textEdit.hide()  # When the window is launched, hide the textedit
        self.setWindowIcon(QtGui.QIcon("icons/window.png"))  # Set the window icon (does not work directly in QT Designer)
        self.menu_bar()  # Create the menu bar
        self.show()  # Display  main window

        # Creation of export directories when opening the application if they do not already exist
        pathlib.Path(constantes.EXPORTS_OPCA_DIR).mkdir(parents=True, exist_ok=True)  # Creating the opca export folder if it does not already exist
        pathlib.Path(constantes.EXPORTS_VMWARE_DIR).mkdir(parents=True, exist_ok=True)  # Creating the rvtools export folder if it does not already exist
        pathlib.Path(constantes.EXPORTS_CMDB_DIR).mkdir(parents=True, exist_ok=True)  # Creating the cmdb export folder if it does not already exist

        self.get_export_folder_date("vmware")  # Récupérer et afficher la date du répertoire d'exports vmware
        self.get_export_folder_date("opca")  # Récupérer et afficher la date du répertoire d'exports opca
        self.get_export_folder_date("cmdb")  # Récupérer et afficher la date du répertoire d'exports cmdb
        self.display_exports_folders_dates()

        self.check_config_db_file()  # Je vérifie car je ne synchronise pas ce fichier avec git /   # Vérifier et afficher si paramètres connexion base par défaut
        self.list_authorized_files()  # Génére la liste des fichiers authorisés à l'ouverture de l'appli afin de pouvoir lister les exports (dans paramètres)

    def menu_bar(self):
        # Menu File > exit
        exit_action = QtWidgets.QAction(QtGui.QIcon('icons/exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)

        # Cette fonction n'est pas disponible pour le moment car bug depuis l'ajout des imports csv CMDB - A corriger plus tard + décommenter l'apparition du bouton plus bas
        # Menu file > Import
        upload_one_export_action = QtWidgets.QAction(QtGui.QIcon('icons/import.png'), '&Importer un export', self)
        upload_one_export_action.setStatusTip("Importer un fichier RVTools (.xlsx ou .xls)")
        upload_one_export_action.triggered.connect(self.upload_one_export)

        # Menu file > Export
        export_action = QtWidgets.QAction(QtGui.QIcon('icons/save.png'), '&Exporter le resultat', self)
        export_action.setStatusTip("Exporter le resultat de la recherche au format .csv")
        export_action.triggered.connect(self.export_result)

        # Menu fichier > Refesh BDD VMware
        refresh_bdd_vmware = QtWidgets.QAction(QtGui.QIcon('icons/refresh.png'), '&Mise à jour VMware', self)
        refresh_bdd_vmware.setStatusTip("Update the database from the RVTools that are present the exports folder")
        refresh_bdd_vmware.triggered.connect(lambda: self.update_db("vmware"))

        # Menu fichier > Refesh BDD OPCA
        refresh_bdd_opca = QtWidgets.QAction(QtGui.QIcon('icons/refresh.png'), '&Mise à jour OPCA', self)
        refresh_bdd_opca.setStatusTip("Update the database from the OPCA exports that are present the exports folder")
        refresh_bdd_opca.triggered.connect(lambda: self.update_db("opca"))

        # Menu fichier > Refesh BDD CMDB
        refresh_bdd_cmdb = QtWidgets.QAction(QtGui.QIcon('icons/refresh.png'), '&Mise à jour CMDB', self)
        refresh_bdd_cmdb.setStatusTip("Update the database from the CMDB exports that are present the exports folder")
        refresh_bdd_cmdb.triggered.connect(lambda: self.update_db("cmdb"))

        # Menu file > Renommer les exports
        rename_export = QtWidgets.QAction(QtGui.QIcon('icons/rename.png'), '&Renommer les exports', self)
        rename_export.setStatusTip("Renommer les fichiers d'exports en fonctions des infos du config_authorized_files.ini")
        rename_export.triggered.connect(self.rename_exports)

        # Menu Parameters > List the RVTools export files present
        list_exports_action_vmware = QtWidgets.QAction(QtGui.QIcon('icons/list.png'), '&Lister les exports RVTools', self)
        list_exports_action_vmware.setStatusTip("List the RVTools VMware export files (.xls/.xlsx) present")
        list_exports_action_vmware.triggered.connect(lambda: tools_instance.list_exports("vmware"))

        # Menu Parameters > List the OPCA export files present
        list_exports_action_opca = QtWidgets.QAction(QtGui.QIcon('icons/list.png'), '&Lister les exports OPCA', self)
        list_exports_action_opca.setStatusTip("List the OPCA export files (.csv) present")
        list_exports_action_opca.triggered.connect(lambda: tools_instance.list_exports("opca"))

        # Menu Parameters > List the CMDB export files present
        list_exports_action_cmdb = QtWidgets.QAction(QtGui.QIcon('icons/list.png'), '&Lister les exports CMDB', self)
        list_exports_action_cmdb.setStatusTip("List the CMDB export files (.csv) present")
        list_exports_action_cmdb.triggered.connect(lambda: tools_instance.list_exports("cmdb"))

        # Menu Parameters > List the export files authorized to be imported into the database
        list_files_authorized_action = QtWidgets.QAction(QtGui.QIcon('icons/list.png'), '&Lister les fichiers autorisés', self)
        list_files_authorized_action.setStatusTip("Liste les exports autorisés à être importés dans la base en fonction des informations du fichier .ini")
        list_files_authorized_action.triggered.connect(self.display_list_authorized_files)

        # Menu Parameters > Configure the connection to the database
        configure_database_action = QtWidgets.QAction(QtGui.QIcon('icons/configdb.png'), '&Configurer la connexion à la base', self)
        configure_database_action.setStatusTip("Configure the connection to the database")
        configure_database_action.triggered.connect(self.configure_database)

        # Menu About > About
        see_about_action = QtWidgets.QAction(QtGui.QIcon('icons/about.png'), '&A propos', self)
        see_about_action.setStatusTip("About")
        see_about_action.triggered.connect(self.see_about)

        self.menuFile.addAction(upload_one_export_action)  # Cette fonction n'est pas disponible pour le moment car bug depuis l'ajout des imports csv CMDB - A corriger plus tard
        self.menuFile.addAction(export_action)
        self.menuFile.addAction(refresh_bdd_vmware)
        self.menuFile.addAction(refresh_bdd_opca)
        self.menuFile.addAction(refresh_bdd_cmdb)
        self.menuFile.addAction(rename_export)
        self.menuFile.addAction(exit_action)
        self.menuParameters.addAction(list_exports_action_vmware)
        self.menuParameters.addAction(list_exports_action_opca)
        self.menuParameters.addAction(list_exports_action_cmdb)
        self.menuParameters.addAction(list_files_authorized_action)
        self.menuParameters.addAction(configure_database_action)
        self.menuAbout.addAction(see_about_action)

    def check_config_db_file(self):
        config_db_ini = constantes.CONFIG_DB_INI
        my_config_db_ini = pathlib.Path(config_db_ini)
        if my_config_db_ini.is_file():
            # print("Le fichier config_db_ini existe déjà.")
            with open(config_db_ini, 'r') as file:
                file_into_string = file.read()
                matches = ["hostname or IP", "database_name", "database_user", "database_password"]
                # if any(x in file_into_string for x in matches):
                match = next((x for x in matches if x in file_into_string), False)
                if match:
                    self.textEdit.setText(f"\"{match}\" est un paramètre par défaut.\n\nVeuillez modifier les paramètres de connexion à la base en allant dans Paramètres > Configurer la connexion à la base.")
                else:
                    # self.textEdit.setText("Paramètres de connexion à la base de donnée enregistrés.")  # Je l'enlève pour ne pas à l'avoir à chaque lancement de l'appli
                    self.textEdit.setText("")
        else:
            logging.debug(f"config_db_ini -> {config_db_ini}")
            f = open(config_db_ini, 'w')
            f.write("[mysql]\n"
                    "host = hostname or IP\n"
                    "database = database_name\n"
                    "user = database_user\n"
                    "password = database_password\n")
            f.close()
            self.textEdit.setText("Veuillez enregistrer les paramètres de connexion à la BDD en allant dans Paramètres > Configurer la connexion à la base.")

    def rename_exports(self):
        self.files_renamed = []
        self.rename_imported_files_to_authorized_files("authorized_files_vmware", "vmware")
        self.rename_imported_files_to_authorized_files("authorized_files_opca", "opca")
        # self.rename_imported_files_to_authorized_files("authorized_files_cmdb", "cmdb")

    def rename_imported_files_to_authorized_files(self, section_ini_authorized_files, export_type):
        authorized_files_parser = configparser.ConfigParser()
        authorized_files_parser.read(constantes.CONFIG_AUTHORIZED_FILES_INI)
        dict_authorized_files = {}  # Init d'un dico des fichiers autorisés

        if authorized_files_parser.has_section(section_ini_authorized_files):
            authorized_files_items = authorized_files_parser.items(section_ini_authorized_files)
            for authorized_files_item in authorized_files_items:
                dict_authorized_files[authorized_files_item[0]] = authorized_files_item[1]
        else:
            raise Exception(f'Section {section_ini_authorized_files} not found in the {constantes.CONFIG_AUTHORIZED_FILES_INI} file.')

        for file in dict_authorized_files.items():
            try:
                os.rename(fr'exports\exports_{export_type}\\' + file[0], fr'exports\exports_{export_type}\\' + file[1])
                self.files_renamed.append(file[0])
            except FileNotFoundError:
                # print(file[0] + " : Ce fichier n'a pas été trouvé dans les exports présents.") # A décommenter pour le debug
                # self.files_not_renamed.append(file[0])
                pass

        if self.files_renamed:
            files_renamed_cr = "\n".join(self.files_renamed)
            self.textEdit.setText(f"Fichiers renommés :\n\n{files_renamed_cr}")
        else:
            self.textEdit.setText("Pas de fichiers à renommer trouvés dans le répertoire des exports.")

    def get_export_folder_date(self, export_type):

        last_modified_date = time.strftime('%d/%m/%Y', time.gmtime(os.path.getmtime(fr"{constantes.EXPORTS_DIR}\exports_{export_type}")))

        if export_type == "vmware":
            self.result_folder_vmware = f"Dernières modifications des exports {export_type} : {str(last_modified_date)}"
        elif export_type == "opca":
            self.result_folder_opca = f"Dernières modifications des exports {export_type} : {str(last_modified_date)}"
        elif export_type == "cmdb":
            self.result_folder_cmdb = f"Dernières modifications des exports {export_type} : {str(last_modified_date)}"

    def display_exports_folders_dates(self):
        self.exports_folders_dates = self.result_folder_vmware + "\n\n" + self.result_folder_opca + "\n\n" + self.result_folder_cmdb
        self.textEdit_2.setText(f"{self.exports_folders_dates}")

    @staticmethod
    def read_authorized_files_config(section_ini_authorized_files):
        # Create a dictionary of authorized files
        # create parser and read ini configuration file
        authorized_files_parser = configparser.ConfigParser()
        authorized_files_parser.read(constantes.CONFIG_AUTHORIZED_FILES_INI)
        dict_authorized_files = {}  # Init d'un dico des fichiers autorisés
        if authorized_files_parser.has_section(section_ini_authorized_files):
            authorized_files_items = authorized_files_parser.items(section_ini_authorized_files)
            for authorized_files_item in authorized_files_items:
                dict_authorized_files[authorized_files_item[0]] = authorized_files_item[1]
        else:
            raise Exception(f'Error from finder file : Section {section_ini_authorized_files} not found in the {constantes.CONFIG_AUTHORIZED_FILES_INI} file.')
        authorized_files_source_list = list(dict_authorized_files.values())
        # print(self.authorized_files_source_list)
        return authorized_files_source_list

    def reset_progressbar_statusbar(self):
        self.progressBar.reset()
        # self.progressBar.hide()
        self.statusBar.showMessage("")

    def see_about(self):
        try:
            with open(os.path.join('data/about.txt'), 'r') as f:
                self.textEdit.setText(f.read())
        except IOError:
            print("File retrieving error...")
            self.textEdit.setText(f.read())

    def list_authorized_files(self):
        self.authorized_files_vmware_source_list = self.read_authorized_files_config("authorized_files_vmware")
        self.authorized_files_opca_source_list = self.read_authorized_files_config("authorized_files_opca")
        self.authorized_files_cmdb_source_list = self.read_authorized_files_config("authorized_files_cmdb")
        self.authorized_files_source_list = self.authorized_files_vmware_source_list + self.authorized_files_opca_source_list + self.authorized_files_cmdb_source_list

    def display_list_authorized_files(self):
        self.list_authorized_files()
        authorized_files_source_list_cr = "\n".join(self.authorized_files_source_list)
        self.textEdit.setText(f"Fichiers d'exports autorisés à être importés dans la base :\n\n{str(authorized_files_source_list_cr)}")

    def export_result(self):
        textedit_content = self.textEdit.toPlainText()  # We retrieve the content of the note
        textedit_content = textedit_content.replace(' --> ', ';')  # We transform it into.csv with ; as a separator

        save_path = QtWidgets.QFileDialog.getExistingDirectory()
        logging.debug(f"selected_folder: {save_path}")

        # print(save_path)  # afficher le répertoire de sauvegarde
        if save_path:
            timestr = time.strftime("%Y%m%d-%H%M%S")
            full_name = os.path.join(save_path, f"result_finder_{timestr}.csv")
            full_name_with_good_slash = os.path.normpath(full_name)
            file1 = open(full_name, "w")
            file1.write(textedit_content)
            self.statusBar.showMessage(f"Resultat enregistré dans {full_name_with_good_slash}")
            file1.close()
        else:
            self.textEdit.setText("Pas de répertoire sélectionné. Sauvegarde annulée.")

    def setup_connections(self):
        # Setup of connections between widgets and other functions
        self.pushButton.clicked.connect(self.search)
        self.pushButton_2.clicked.connect(self.import_list)
        # Make the button an image
        search_icon = QtGui.QPixmap("icons/search.png")
        list_icon = QtGui.QPixmap("icons/list.png")
        self.pushButton.setIcon(search_icon)
        self.pushButton_2.setIcon(list_icon)
        # ComboBox = drop-down menu
        self.comboBox.addItems(["Serveur", "Host", "Application"])

    def update_db(self, export_type):
        """ Updates the bdd according to the files in the export folder.
           Warning, if there is no authorized file, the database will be reset to 0
           The principle is that the bdd is iso with the export folder
           """
        self.reset_progressbar_statusbar()
        data_list = []
        list_data_cmdb = []
        df = None
        df_cmdb = None
        files_paths_authorized_list = []

        # Creates a list of files that are in the export folder where each element is of the type 'C:\\path\file.ext'
        files_paths_list = []
        exports_files_folder_path = fr"{constantes.EXPORTS_DIR}\exports_{export_type}"  # Retrieving the path of the export folder
        for root, dirs, files in os.walk(exports_files_folder_path):
            for file in files:
                files_paths_list.append(os.path.join(root, file))

        for file_path in files_paths_list:
            file = os.path.basename(file_path)
            file_is_authorized = tools_instance.is_file_authorized(file)
            if file_is_authorized:
                files_paths_authorized_list.append(file_path)

        if export_type == "opca" or export_type == "vmware":
            # Create list of list from vmware and opca export files
            files_paths_authorized_list_len = len(files_paths_authorized_list)
            step = 0
            for file_number, file_path_authorized in enumerate(files_paths_authorized_list, 1):

                file_authorized = os.path.basename(file_path_authorized)
                main_window.textEdit.setText(f"Récupération des données depuis le fichier {format(file_authorized)}...")
                QtWidgets.QApplication.processEvents()  # Force a refresh of the UI
                file_name_authorized = os.path.splitext(file_authorized)[0]

                # Update of the progress bar
                main_window.progressBar.show()
                pourcentage_number = (file_number * 100 - 1) // files_paths_authorized_list_len
                for between_pourcentage in range(step, pourcentage_number):
                    time.sleep(0.02)
                    main_window.statusBar.showMessage(f"Action en cours de {between_pourcentage}% ...")
                    main_window.progressBar.setValue(between_pourcentage)
                    step = (file_number * 100 - 1) // files_paths_authorized_list_len

                if export_type == "opca":
                    df = pandas.read_csv(file_path_authorized, sep=';')

                    # Add a column to the dataframe
                    df['DNS Name'] = "N/A"
                    # Add a column to the dataframe
                    df['management'] = file_name_authorized
                    # The dataframe will contains only these colums
                    df = df[["Machine Virtuelle", "DNS Name", "management", "Compute Node"]]
                elif export_type == "vmware":
                    df = pandas.read_excel(file_path_authorized)
                    # Add a column to the dataframe
                    df['management'] = file_name_authorized
                    # The dataframe will contains only these colums
                    df = df[["VM", "DNS Name", "management", "Host"]]

                df = df.where((pandas.notnull(df)), 'N/A')  # Remplacer les 'nan' (générés par panda quand il n'y a pas de valeur dans la case excel) par des 'N/A' sinon SQL traitera les 'nan' comme des '0'
                list_data_temp = df.values.tolist()
                data_list.extend(list_data_temp)

            # print(list_of_data)  # Donne une liste de listes
        elif export_type == "cmdb":
            # Create list of list from cmdb export file
            # print(files_paths_authorized_list)
            list_data_cmdb = []
            files_paths_authorized_list_len = len(files_paths_authorized_list)
            step = 0
            for file_number, file_path_authorized in enumerate(files_paths_authorized_list, 1):
                file_authorized = os.path.basename(file_path_authorized)
                main_window.textEdit.setText(f"Data retrieval from the file {format(file_authorized)}...")
                QtWidgets.QApplication.processEvents()  # Force a refresh of the UI

                # Update of the progress bar
                main_window.progressBar.show()
                pourcentage_number = (file_number * 100 - 1) // files_paths_authorized_list_len
                for between_pourcentage in range(step, pourcentage_number):
                    time.sleep(0.02)
                    main_window.statusBar.showMessage(f"Processing of {between_pourcentage}% ...")
                    main_window.progressBar.setValue(between_pourcentage)
                    step = (file_number * 100 - 1) // files_paths_authorized_list_len

                    df_cmdb = pandas.read_csv(file_path_authorized, sep=',', encoding="Windows-1252")
                    # The dataframe will contains only these colums
                    df_cmdb = df_cmdb[["ci6_name", "ci2_name"]]

                list_data_cmdb_temp = df_cmdb.values.tolist()
                # print(list_data_cmdb_temp)
                list_data_cmdb.extend(list_data_cmdb_temp)
                # print(list_data_cmdb)

        main_window.textEdit.setText("Connexion à la base...")
        QtWidgets.QApplication.processEvents()  # Force a refresh of the UI
        time.sleep(2)  # The connection is sometimes so fast that there is no time to display the text that indicates the connection
        with DatabaseGestion() as db_connection:  # "with" allows you to use a context manager that will automatically call the disconnect function when you exit the scope
            if db_connection.error_db_connection is None:
                db_connection.sql_query_execute("TRUNCATE TABLE serveur_" + export_type)
                main_window.textEdit.setText(f"Insertion des données de {export_type} dans la base...")
                QtWidgets.QApplication.processEvents()  # Force a refresh of the UI
                if export_type == "opca":
                    db_connection.sql_query_executemany(f"INSERT INTO serveur_opca (serveur_name, dns_name, management_name, host_name) VALUES (%s,%s,%s,%s)", data_list)
                elif export_type == "vmware":
                    db_connection.sql_query_executemany(f"INSERT INTO serveur_vmware (serveur_name, dns_name, management_name, host_name) VALUES (%s,%s,%s,%s)", data_list)

                elif export_type == "cmdb":
                    db_connection.sql_query_executemany(f"INSERT INTO serveur_cmdb (serveur_name, environment_name) VALUES (%s,%s)", list_data_cmdb)

                if db_connection.error_db_execution is None:
                    main_window.textEdit.setText(f"La base de données {export_type} contient {str(db_connection.cursor.rowcount)} lignes.")
                    main_window.progressBar.setValue(100)  # 100 -> 100%
                    main_window.statusBar.showMessage("Action terminée !")
                    main_window.reset_progressbar_statusbar()
                else:
                    main_window.textEdit.setText(db_connection.message_error_execution_db)
                    main_window.reset_progressbar_statusbar()
            else:
                main_window.textEdit.setText(db_connection.message_error_connection_db)
                main_window.reset_progressbar_statusbar()

    def upload_one_export(self):
        self.reset_progressbar_statusbar()
        # File choice
        file_chosen = QtWidgets.QFileDialog.getOpenFileName()
        # Importing the file into the export folder
        # file_chosen:  De type -> ('D:/Python/Projets/file.py', 'All Files (*)')
        if not all(file_chosen):  # if you have pressed cancel, you have an empty variable
            main_window.textEdit.setText("Pas de fichier sélectionné.")
        else:
            file = os.path.split(file_chosen[0])[1]  # We get the name of the file with its extension
            file_is_authorized = tools_instance.is_file_authorized(file)
            if file_is_authorized:
                file_ext = os.path.splitext(file)[1]  # We retrieve the file extension to verify that the extension is authorized (dictionary)
                export_types_dict = {'.xlsx': 'vmware', '.xls': 'vmware', '.csv': 'opca'}
                export_type = export_types_dict.get(file_ext, 'Extension non autorisée !')  # if the extension is not allowed we will get "extension_not_autorised"
                if export_type != "Extension non autorisée !":  # if the file is of a type present in the "export_types_dict" dict
                    exports_files_folder_path = fr"{constantes.EXPORTS_DIR}\exports_{export_type}"  # We get where we need to copy the export file
                    file_folder_copy_dest = exports_files_folder_path + file  # We create the full path of the new file
                    file_path = file_chosen[0]  # We get the path of the file to copy
                    try:
                        shutil.copyfile(file_path, file_folder_copy_dest)  # Copy of the file
                        main_window.textEdit.setText(f"Le fichier  \"{file}\" a été copié dans le répertoire export_{export_type}.\n\nVous pouvez maintenant mettre à jour la base de données afin que ces données soient disponibles dans la recherche.\n\nPour faire cela, aller dans le menu \"Fichier > Mise à jour..\"")
                    except IOError as e:
                        print(e)
                        main_window.textEdit.setText(str(e))
                else:
                    main_window.textEdit.setText("Extension de fichier invalide !")
            else:
                main_window.textEdit.setText(f"\"{file}\" n'est pas un fichier autorisé !")

    def setup_keyboard_shortcuts(self):
        # We create a shortcut for the Esc key that will close the application
        QtWidgets.QShortcut(QtGui.QKeySequence('Esc'), self, self.close)
        # A shortcut is created for the ENTER key on the numeric keypad that will launch the search
        QtWidgets.QShortcut(QtGui.QKeySequence('Enter'), self, self.search)
        # We create a shortcut for the ENTER key on the keyboard that will launch the search
        QtWidgets.QShortcut(QtGui.QKeySequence('Return'), self, self.search)

    def search(self):
        self.reset_progressbar_statusbar()
        search_string = self.lineEdit.text()
        search_list = search_string.split()
        tools_instance.search(search_list)

    def import_list(self):
        # noinspection PyAttributeOutsideInit
        self.window_import_list = ImportList(main_window, tools_instance)  # Je fourni à la classe ImportList l'instance main_window en paramètre
        self.reset_progressbar_statusbar()
        self.window_import_list.show()

    def configure_database(self):
        # noinspection PyAttributeOutsideInit
        self.window_Configure_Database = ConfigureDatabase(main_window)
        self.window_Configure_Database.show()
        self.reset_progressbar_statusbar()


# MAIN

app = QtWidgets.QApplication([])
main_window = Creator()
tools_instance = Tools(main_window)
app.exec_()
