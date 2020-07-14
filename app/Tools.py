import logging
import os
import time

from PySide2 import QtWidgets

import AlignDelegate
import DatabaseGestion
import MyTableModel
import constantes


# Les fonctions dans Tools ont besoin de l'UI. Donc je passe une instance de l'UI.


class Tools(QtWidgets.QWidget):
    def __init__(self, window_instance):
        self.window_instance = window_instance
        super(Tools, self).__init__()

    def is_db_empty(self):
        with DatabaseGestion.DatabaseGestion() as db_connection:  # with allows you to use a context manager that will automatically call the disconnect function when you exit the scope
            if db_connection.error_db_connection is None:
                self.window_instance.textEdit.setText("Base de donnée vide ? Vérification en cours...")
                db_connection.sql_query_execute(f'SELECT * FROM serveur_vmware')
                rows_vmware = db_connection.cursor.fetchall()
                if not rows_vmware:
                    self.window_instance.textEdit.setText("Base VMware vide.")
                    return True
                db_connection.sql_query_execute(f'SELECT * FROM serveur_opca')
                rows_opca = db_connection.cursor.fetchall()
                if not rows_opca:
                    self.window_instance.textEdit.setText("Base OPCA vide.")
                    return True
                return False

    def search(self, search_list):

        search_choice = self.window_instance.comboBox.currentText()
        self.window_instance.textEdit.setText("Connexion à la base de données...")
        QtWidgets.QApplication.processEvents()  # Force a refresh of the UI
        dict_search_choice = {'Serveur': 'serveur_name', 'Host': 'host_name', 'Application': 'appli_name'}
        search_choice = dict_search_choice.get(search_choice, 'default')  # We get the field to use for the select and where in the SQL query and if it is neither of them we put "default"
        # print(search_choice)
        if search_choice == 'serveur_name':
            results_query_search = []
            nbr_result_ko = 0
            nbr_result_ok = 0
            red_text = "<span style=\" color:#ff0000;\" >"
            text_end = "</span>"
            green_text = "<span style=\" color:#5ea149;\" >"
            logging.debug(f"search_list: {search_list}")

            with DatabaseGestion.DatabaseGestion() as db_connection:  # with allows you to use a context manager that will automatically call the disconnect function when you exit the scope
                if db_connection.error_db_connection is None:

                    if self.is_db_empty():
                        pass
                    else:
                        # If search is empty, search and display all results
                        self.window_instance.textEdit.setText("Recherche en cours...")
                        QtWidgets.QApplication.processEvents()  # Force a refresh of the UI
                        if not search_list:
                            db_connection.sql_query_execute(f"""
                                                                    SELECT DISTINCT v.serveur_name, v.management_name, IF(v.dns_name is null, \'N/A\', v.dns_name), IF(c.environment_name is null, \'N/A\', c.environment_name) 
                                                                    FROM serveur_vmware as v 
                                                                    LEFT JOIN serveur_cmdb as c 
                                                                    ON(v.serveur_name = c.serveur_name)""")

                            rows_vmware = db_connection.cursor.fetchall()

                            db_connection.sql_query_execute(f"""SELECT DISTINCT o.serveur_name, o.management_name, IF(o.dns_name is null, \'N/A\', o.dns_name), IF(c.environment_name is null, \'N/A\', c.environment_name) 
                                                                    FROM serveur_opca as o 
                                                                    LEFT JOIN serveur_cmdb as c 
                                                                    ON(o.serveur_name = c.serveur_name)""")

                            rows_opca = db_connection.cursor.fetchall()

                            results_query_search.extend(rows_vmware)
                            results_query_search.extend(rows_opca)

                        else:  # if search is not empty
                            search_list_len = len(search_list)
                            step_search = 0
                            self.window_instance.textEdit.setText("Recherche en cours...")
                            QtWidgets.QApplication.processEvents()  # Force a refresh of the UI

                            # For each search string in list
                            for file_number_search, search_string in enumerate(search_list, 1):
                                search_string = str.strip(search_string)  # delete spaces before and after the
                                self.window_instance.textEdit.setText(f"Recherche en cours de {search_string}...")

                                db_connection.sql_query_execute(f"""
                                                                        SELECT DISTINCT v.serveur_name, v.management_name, IF(v.dns_name is null, \'N/A\', v.dns_name), IF(c.environment_name is null, \'N/A\', c.environment_name) 
                                                                        FROM serveur_vmware as v 
                                                                        LEFT JOIN serveur_cmdb as c 
                                                                        ON(v.serveur_name = c.serveur_name) 
                                                                        WHERE v.dns_name LIKE \'%{search_string}%\'
                                                                        OR v.serveur_name LIKE \'%{search_string}%\'""")

                                rows_vmware = db_connection.cursor.fetchall()

                                db_connection.sql_query_execute(f"""SELECT DISTINCT o.serveur_name, o.management_name, IF(o.dns_name is null, \'N/A\', o.dns_name), IF(c.environment_name is null, \'N/A\', c.environment_name) 
                                                                        FROM serveur_opca as o 
                                                                        LEFT JOIN serveur_cmdb as c 
                                                                        ON(o.serveur_name = c.serveur_name) 
                                                                        WHERE o.dns_name LIKE \'%{search_string}%\'
                                                                        OR o.serveur_name LIKE \'%{search_string}%\'""")

                                rows_opca = db_connection.cursor.fetchall()

                                if not rows_opca and not rows_vmware:
                                    nbr_result_ko += 1
                                    results_query_search.append((search_string, 'Non présent dans les exports', 'Non présent dans les exports', 'Non présent dans les exports'))

                                if rows_vmware:
                                    nbr_item_in_list = len(rows_vmware)
                                    results_query_search.extend(rows_vmware)
                                    nbr_result_ok = nbr_result_ok + nbr_item_in_list

                                if rows_opca:
                                    nbr_item_in_list = len(rows_opca)
                                    results_query_search.extend(rows_opca)
                                    nbr_result_ok = nbr_result_ok + nbr_item_in_list

                                if search_list_len > 1:  # To avoid having the progress bar when doing a search on only one item to not waste time
                                    # Update of the progress bar
                                    self.window_instance.progressBar.show()
                                    pourcentage_number_1 = (file_number_search * 100 - 1) // search_list_len
                                    for between_pourcentage_1 in range(step_search, pourcentage_number_1):
                                        time.sleep(0.005)
                                        pourcentage_text_1 = f"Processing of {between_pourcentage_1}% ..."
                                        self.window_instance.statusBar.showMessage(pourcentage_text_1)
                                        self.window_instance.progressBar.setValue(between_pourcentage_1)
                                        step_search = (file_number_search * 100 - 1) // search_list_len

                        nbr = 0  # To get number of results
                        list_result = []
                        list_result_saut = []

                    # print(results_query_search)

                    for nbr, result_query_search in enumerate(results_query_search, 1):
                        # print(result_query_search)
                        serveur_name, management_name, dns_name, environment_name = result_query_search  # unpacking

                        if management_name == 'Non présent dans les exports':
                            list_result.append(f"{serveur_name} --> {red_text}{management_name}{text_end} --> {dns_name} --> {environment_name}")
                        else:
                            list_result.append(f"{serveur_name} --> {green_text}{management_name}{text_end} --> {dns_name} --> {environment_name}")

                        list_result_saut = "<br>".join(list_result)

                    # Display result in text edit
                    self.window_instance.textEdit.setText(list_result_saut)

                    # Display data results in tableview
                    # header table view
                    header = ['Nom du serveur', 'vCenter ou ESXi (vmware), Management Node (opca)', 'Nom DNS (vmware)', 'Environnement/Application']

                    # Create instance table view
                    table_model = MyTableModel.MyTableModel(results_query_search, header)

                    # Count tab lines
                    # print(table_model.rowCount(None))

                    # Afficher la liste des data à mettre dans le tableau
                    # print(table_model.mylist) # print(data_list)

                    self.window_instance.tableView.setModel(table_model)
                    # set color and style header
                    # stylesheet = "::section{Background-color:rgb(179, 224, 229);border-radius:14px;}"   # Pour ne pas avoir les bordures des cases du header
                    stylesheet = "::section{Background-color:rgb(179, 224, 229)}"  # Couleur bleu ciel pour l'entête du tableau
                    self.window_instance.tableView.horizontalHeader().setStyleSheet(stylesheet)
                    # set font
                    # font = QtGui.QFont("Courier New", 14)
                    # self.tableView.setFont(font)
                    # main_window.tableView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)  # Ajuster la zone tableview aux colonnes (ne fonctionne pas ??!)
                    # set column width to fit contents (set font first!)
                    self.window_instance.tableView.resizeColumnsToContents()
                    # stretch the last column to the view so that the table view fit the layout
                    self.window_instance.tableView.horizontalHeader().setStretchLastSection(True)

                    delegate = AlignDelegate.AlignDelegate(self.window_instance.tableView)
                    # main_window.tableView.setItemDelegateForColumn(2, delegate)  # Pour Centrer le texte de la colonne id 2 (donc la troisième)
                    self.window_instance.tableView.setItemDelegate(delegate)  # for all columns

                    # enable sorting
                    self.window_instance.tableView.setSortingEnabled(True)

                    self.window_instance.statusBar.showMessage(f"Résultats : {str(nbr)} | OK : {str(nbr_result_ok)} | KO : {str(nbr_result_ko)}")

                    self.window_instance.progressBar.reset()
                    # self.window_instance.progressBar.hide()
                else:
                    self.window_instance.textEdit.setText(db_connection.message_error_connection_db)
        elif search_choice == 'host_name':
            results_query_search = []
            # nbr_result_ko = 0
            # nbr_result_ok = 0
            red_text = "<span style=\" color:#ff0000;\" >"
            text_end = "</span>"
            green_text = "<span style=\" color:#5ea149;\" >"
            logging.debug(f"search_list: {search_list}")

            with DatabaseGestion.DatabaseGestion() as db_connection:  # with allows you to use a context manager that will automatically call the disconnect function when you exit the scope
                if db_connection.error_db_connection is None:
                    if self.is_db_empty():
                        pass
                    else:
                        # If search is empty, search and display all results
                        self.window_instance.textEdit.setText("Recherche en cours...")
                        QtWidgets.QApplication.processEvents()  # Force a refresh of the UI
                        if not search_list:
                            db_connection.sql_query_execute(f'SELECT host_name, management_name FROM serveur_vmware')
                            rows_vmware = db_connection.cursor.fetchall()

                            db_connection.sql_query_execute(f'SELECT host_name, management_name FROM serveur_opca')
                            rows_opca = db_connection.cursor.fetchall()

                            results_query_search.extend(rows_vmware)
                            results_query_search.extend(rows_opca)

                        else:  # if search is not empty
                            search_list_len = len(search_list)
                            step_search = 0
                            self.window_instance.textEdit.setText("Recherche en cours...")
                            QtWidgets.QApplication.processEvents()  # Force a refresh of the UI

                            # For each search string in list
                            for file_number_search, search_string in enumerate(search_list, 1):
                                search_string = str.strip(search_string)  # delete spaces before and after the
                                self.window_instance.textEdit.setText(f"Recherche en cours de {search_string}...")

                                db_connection.sql_query_execute(f'SELECT host_name, management_name FROM serveur_vmware WHERE host_name LIKE \'%{search_string}%\'')
                                rows_vmware = db_connection.cursor.fetchall()

                                db_connection.sql_query_execute(f'SELECT host_name, management_name FROM serveur_opca WHERE host_name LIKE \'%{search_string}%\'')
                                rows_opca = db_connection.cursor.fetchall()

                                if not rows_opca and not rows_vmware:
                                    # nbr_result_ko += 1
                                    results_query_search.append((search_string, 'Non présent dans les exports'))

                                if rows_vmware:
                                    # nbr_item_in_list = len(rows_vmware)
                                    results_query_search.extend(rows_vmware)
                                    # nbr_result_ok = nbr_result_ok + nbr_item_in_list

                                if rows_opca:
                                    # nbr_item_in_list = len(rows_opca)
                                    results_query_search.extend(rows_opca)
                                    # nbr_result_ok = nbr_result_ok + nbr_item_in_list

                                if search_list_len > 1:  # To avoid having the progress bar when doing a search on only one item to not waste time
                                    # Update of the progress bar
                                    self.window_instance.progressBar.show()
                                    pourcentage_number_1 = (file_number_search * 100 - 1) // search_list_len
                                    for between_pourcentage_1 in range(step_search, pourcentage_number_1):
                                        time.sleep(0.005)
                                        pourcentage_text_1 = f"Processing of {between_pourcentage_1}% ..."
                                        self.window_instance.statusBar.showMessage(pourcentage_text_1)
                                        self.window_instance.progressBar.setValue(between_pourcentage_1)
                                        step_search = (file_number_search * 100 - 1) // search_list_len

                        results_query_search = list(dict.fromkeys(results_query_search))  # Remove the duplicates
                        results_query_search = [x for x in results_query_search if "0" not in x]  # Remove the results that is "0" (for opca data)

                        nbr = 0  # To get number of results
                        list_result = []
                        list_result_saut = []

                        # print(results_query_search)

                        for nbr, result_query_search in enumerate(results_query_search, 1):
                            # print(result_query_search)
                            serveur_name, management_name = result_query_search  # unpacking

                            if management_name == 'Non présent dans les exports':
                                list_result.append(f"{serveur_name} --> {red_text}{management_name}{text_end}")
                            else:
                                list_result.append(f"{serveur_name} --> {green_text}{management_name}{text_end}")

                            list_result_saut = "<br>".join(list_result)

                        # Display result in text edit
                        self.window_instance.textEdit.setText(list_result_saut)

                        # Display data results in tableview
                        # header table view
                        header = ['Nom de l\'ESXi (vmware) ou du Management Node (opca)', 'vCenter (vmware) ou Management Node (opca)']

                        # Create instance table view
                        table_model = MyTableModel.MyTableModel(results_query_search, header)

                        # Count tab lines
                        # print(table_model.rowCount(None))

                        # Afficher la liste des data à mettre dans le tableau
                        # print(table_model.mylist) # print(data_list)

                        self.window_instance.tableView.setModel(table_model)
                        # set color and style header
                        # stylesheet = "::section{Background-color:rgb(179, 224, 229);border-radius:14px;}"   # Pour ne pas avoir les bordures des cases du header
                        stylesheet = "::section{Background-color:rgb(179, 224, 229)}"  # Couleur bleu ciel pour l'entête du tableau
                        self.window_instance.tableView.horizontalHeader().setStyleSheet(stylesheet)
                        # set font
                        # font = QtGui.QFont("Courier New", 14)
                        # self.tableView.setFont(font)
                        # main_window.tableView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)  # Ajuster la zone tableview aux colonnes (ne fonctionne pas ??!)
                        # set column width to fit contents (set font first!)
                        self.window_instance.tableView.resizeColumnsToContents()
                        # stretch the last column to the view so that the table view fit the layout
                        self.window_instance.tableView.horizontalHeader().setStretchLastSection(True)

                        delegate = AlignDelegate.AlignDelegate(self.window_instance.tableView)
                        # main_window.tableView.setItemDelegateForColumn(2, delegate)  # Pour Centrer le texte de la colonne id 2 (donc la troisième)
                        self.window_instance.tableView.setItemDelegate(delegate)  # for all columns

                        # enable sorting
                        self.window_instance.tableView.setSortingEnabled(True)

                        # main_window.statusBar.showMessage(f"Results : {str(nbr)} | OK : {str(nbr_result_ok)} | KO : {str(nbr_result_ko)}")
                        self.window_instance.statusBar.showMessage(f"Résultats : {str(nbr)}")

                        self.window_instance.progressBar.reset()
                        # self.window_instance.progressBar.hide()
                else:
                    self.window_instance.textEdit.setText(db_connection.message_error_connection_db)
        elif search_choice == 'appli_name':
            results_query_search = []
            nbr_result_ko = 0
            nbr_result_ok = 0
            red_text = "<span style=\" color:#ff0000;\" >"
            text_end = "</span>"
            green_text = "<span style=\" color:#5ea149;\" >"
            logging.debug(f"search_list: {search_list}")

            with DatabaseGestion.DatabaseGestion() as db_connection:  # with allows you to use a context manager that will automatically call the disconnect function when you exit the scope
                if db_connection.error_db_connection is None:
                    if self.is_db_empty():
                        pass
                    else:
                        # If search is empty, search and display all results
                        self.window_instance.textEdit.setText("Recherche en cours...")
                        QtWidgets.QApplication.processEvents()  # Force a refresh of the UI
                        if not search_list:
                            db_connection.sql_query_execute(f"""
                                                                    SELECT IF(c.environment_name is null, \'N/A\', c.environment_name), v.serveur_name
                                                                    FROM serveur_vmware as v 
                                                                    LEFT JOIN serveur_cmdb as c 
                                                                    ON(v.serveur_name = c.serveur_name)""")

                            rows_vmware = db_connection.cursor.fetchall()

                            db_connection.sql_query_execute(f"""
                                                                    SELECT IF(c.environment_name is null, \'N/A\', c.environment_name), o.serveur_name
                                                                    FROM serveur_opca as o 
                                                                    LEFT JOIN serveur_cmdb as c 
                                                                    ON(o.serveur_name = c.serveur_name)""")

                            rows_opca = db_connection.cursor.fetchall()

                            results_query_search.extend(rows_vmware)
                            results_query_search.extend(rows_opca)

                        else:  # if search is not empty
                            search_list_len = len(search_list)
                            step_search = 0
                            self.window_instance.textEdit.setText("Recherche en cours...")
                            QtWidgets.QApplication.processEvents()  # Force a refresh of the UI

                            # For each search string in list
                            for file_number_search, search_string in enumerate(search_list, 1):
                                search_string = str.strip(search_string)  # delete spaces before and after the
                                self.window_instance.textEdit.setText(f"Recherche en cours de {search_string}...")

                                db_connection.sql_query_execute(f"""
                                                                        SELECT IF(c.environment_name is null, \'N/A\', c.environment_name), v.serveur_name
                                                                        FROM serveur_vmware as v 
                                                                        LEFT JOIN serveur_cmdb as c 
                                                                        ON(v.serveur_name = c.serveur_name) 
                                                                        WHERE c.environment_name LIKE \'%{search_string}%\'""")

                                rows_vmware = db_connection.cursor.fetchall()

                                db_connection.sql_query_execute(f"""
                                                                        SELECT IF(c.environment_name is null, \'N/A\', c.environment_name), o.serveur_name
                                                                        FROM serveur_opca as o 
                                                                        LEFT JOIN serveur_cmdb as c 
                                                                        ON(o.serveur_name = c.serveur_name) 
                                                                        WHERE c.environment_name LIKE \'%{search_string}%\'""")

                                rows_opca = db_connection.cursor.fetchall()

                                if not rows_opca and not rows_vmware:
                                    nbr_result_ko += 1
                                    results_query_search.append((search_string, 'Non présent dans les exports'))

                                if rows_vmware:
                                    nbr_item_in_list = len(rows_vmware)
                                    results_query_search.extend(rows_vmware)
                                    nbr_result_ok = nbr_result_ok + nbr_item_in_list

                                if rows_opca:
                                    nbr_item_in_list = len(rows_opca)
                                    results_query_search.extend(rows_opca)
                                    nbr_result_ok = nbr_result_ok + nbr_item_in_list

                                if search_list_len > 1:  # To avoid having the progress bar when doing a search on only one item to not waste time
                                    # Update of the progress bar
                                    self.window_instance.progressBar.show()
                                    pourcentage_number_1 = (file_number_search * 100 - 1) // search_list_len
                                    for between_pourcentage_1 in range(step_search, pourcentage_number_1):
                                        time.sleep(0.005)
                                        pourcentage_text_1 = f"Action en cours de {between_pourcentage_1}% ..."
                                        self.window_instance.statusBar.showMessage(pourcentage_text_1)
                                        self.window_instance.progressBar.setValue(between_pourcentage_1)
                                        step_search = (file_number_search * 100 - 1) // search_list_len

                        nbr = 0  # To get number of results
                        list_result = []
                        list_result_saut = []

                        # print(results_query_search)

                        for nbr, result_query_search in enumerate(results_query_search, 1):
                            # print(result_query_search)
                            environment_name, serveur_name = result_query_search  # unpacking

                            if serveur_name == 'Non présent dans les exports':
                                list_result.append(f"{environment_name} --> {red_text}{serveur_name}{text_end}")
                            else:
                                list_result.append(f"{environment_name} --> {green_text}{serveur_name}{text_end}")

                            list_result_saut = "<br>".join(list_result)

                        # Display result in text edit
                        self.window_instance.textEdit.setText(list_result_saut)

                        # Display data results in tableview
                        # header table view
                        header = ['Application', 'Nom du serveur']

                        # Create instance table view
                        table_model = MyTableModel.MyTableModel(results_query_search, header)

                        # Count tab lines
                        # print(table_model.rowCount(None))

                        # Afficher la liste des data à mettre dans le tableau
                        # print(table_model.mylist) # print(data_list)

                        self.window_instance.tableView.setModel(table_model)
                        # set color and style header
                        # stylesheet = "::section{Background-color:rgb(179, 224, 229);border-radius:14px;}"   # Pour ne pas avoir les bordures des cases du header
                        stylesheet = "::section{Background-color:rgb(179, 224, 229)}"  # Couleur bleu ciel pour l'entête du tableau
                        self.window_instance.tableView.horizontalHeader().setStyleSheet(stylesheet)
                        # set font
                        # font = QtGui.QFont("Courier New", 14)
                        # self.tableView.setFont(font)
                        # main_window.tableView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)  # Ajuster la zone tableview aux colonnes (ne fonctionne pas ??!)
                        # set column width to fit contents (set font first!)
                        self.window_instance.tableView.resizeColumnsToContents()
                        # stretch the last column to the view so that the table view fit the layout
                        self.window_instance.tableView.horizontalHeader().setStretchLastSection(True)

                        delegate = AlignDelegate.AlignDelegate(self.window_instance.tableView)
                        # main_window.tableView.setItemDelegateForColumn(2, delegate)  # Pour Centrer le texte de la colonne id 2 (donc la troisième)
                        self.window_instance.tableView.setItemDelegate(delegate)  # for all columns

                        # enable sorting
                        self.window_instance.tableView.setSortingEnabled(True)

                        self.window_instance.statusBar.showMessage(f"Résultats : {str(nbr)} | OK : {str(nbr_result_ok)} | KO : {str(nbr_result_ko)}")

                        self.window_instance.progressBar.reset()
                        # self.window_instance.progressBar.hide()
                else:
                    self.window_instance.textEdit.setText(db_connection.message_error_connection_db)

    def is_file_authorized(self, file):
        """ If the file is in the list of authorized_files, we copy the file
        :param file: Name of the file with its extension
        :return: A booleen True if the file is part of the authorized list or False if not
        """

        if file in self.window_instance.authorized_files_source_list:  # Lire l'attribut de l'instance qui a déjà été initialisé
            logging.debug(f"is_file_authorized : \"{file}\" is an authorized file.")
            file_authorized = True
        else:
            logging.debug(f"is_file_authorized : \"{file}\" is not an authorized file.")
            file_authorized = False

        return file_authorized

    def list_exports(self, export_type):
        files_authorized_list = []
        files_not_authorized_list = []
        # Check if there are any exports in the folder concerned
        if not os.listdir(fr"{constantes.EXPORTS_DIR}\exports_{export_type}"):
            self.window_instance.textEdit.setText(f"Le répertoire des exports exports_{export_type} est vide.")
        else:
            # Creates a list of files that are in the export folder where each element is of the type 'C:\\path\file.ext'
            files_paths_list = []
            exports_files_folder_path = fr"{constantes.EXPORTS_DIR}\exports_{export_type}"  # Retrieving the path of the export folder
            for root, dirs, files in os.walk(exports_files_folder_path):
                for file in files:
                    files_paths_list.append(os.path.join(root, file))
            number_authorized = number_not_authorized = 0
            for file_path in files_paths_list:
                file = os.path.basename(file_path)
                file_is_authorized = self.is_file_authorized(file)
                if file_is_authorized:
                    number_authorized += 1
                    files_authorized_list.append(file)
                else:
                    number_not_authorized += 1
                    files_not_authorized_list.append(file)

            if files_authorized_list:
                list_result_cr_authorized = "\n".join(files_authorized_list)
                result_search_authorized = f"Nombre de fichiers autorisés trouvés dans le répertoire des exports export_{export_type} : {str(number_authorized)}\n\n{list_result_cr_authorized}"
            else:
                result_search_authorized = "Pas de fichiers autorisés trouvés dans le répertoire des exports."

            if files_not_authorized_list:
                list_result_cr_not_authorized = "\n".join(files_not_authorized_list)
                result_search_not_authorized = f"Nombre de fichiers non-autorisés trouvés dans le répertoire des exports export_{export_type} : {str(number_not_authorized)}\n\n{list_result_cr_not_authorized}"
            else:
                result_search_not_authorized = f"Pas de fichiers non-autorisés trouvés dans le répertoire des exports export_{export_type}."

            self.window_instance.textEdit.setText(f"{result_search_authorized}\n\n{result_search_not_authorized}")
