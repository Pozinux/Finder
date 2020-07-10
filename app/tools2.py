import logging
import os


# Fichier créé avec des fonctions qui ne nécessitent pas d'affichage UI.
# Par exemple get_export_files_folder_path est utilisée dans l'init du Creator de l'UI. Les fonctions dans Tools ont besoin de l'UI par contre. Donc je passe une instance de l'UI.


def get_exports_files_folder_path(export_type):
    #current_folder = os.path.dirname(__file__)
    current_forlder_one_step_back = os.path.normpath(os.getcwd() + os.sep + os.pardir)
    exports_files_folder_path = current_forlder_one_step_back + r"\exports\exports_" + export_type + "\\"
    logging.debug(f"exports_files_folder_path: {exports_files_folder_path}")
    return exports_files_folder_path


def create_files_paths_list(export_type):
    """ Created a list of files that are in the export folder
    :return: List of files where each element is of the type 'C:\\path\file.ext'
    """
    files_paths_list = []
    exports_files_folder_path = get_exports_files_folder_path(export_type)  # Retrieving the path of the export folder
    for root, dirs, files in os.walk(exports_files_folder_path):
        for file in files:
            files_paths_list.append(os.path.join(root, file))
    return files_paths_list
