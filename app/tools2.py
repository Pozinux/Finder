import logging
import os

import constantes


# Fichier créé avec des fonctions qui ne nécessitent pas d'affichage UI.
# Par exemple get_export_files_folder_path est utilisée dans l'init du Creator de l'UI. Les fonctions dans Tools ont besoin de l'UI par contre. Donc je passe une instance de l'UI.


def create_files_paths_list(export_type):
    """ Created a list of files that are in the export folder
    :return: List of files where each element is of the type 'C:\\path\file.ext'
    """
    files_paths_list = []
    exports_files_folder_path = f"{constantes.EXPORTS_DIR}\exports_{export_type}"  # Retrieving the path of the export folder
    for root, dirs, files in os.walk(exports_files_folder_path):
        for file in files:
            files_paths_list.append(os.path.join(root, file))
    return files_paths_list
