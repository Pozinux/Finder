import os
import logging

# A décommenter pour voir les log dans tous les fichiers du projet ou "contantes.py" a été importé.
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - In %(filename)s - Line %(lineno)s - %(message)s')

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(CUR_DIR, "config")
CONFIG_AUTHORIZED_FILES_INI = os.path.join(CONFIG_DIR, "config_authorized_files.ini")
CONFIG_DB_INI = os.path.join(CONFIG_DIR, "config_db.ini")
EXPORTS_DIR = os.path.join(CUR_DIR, "exports")
EXPORTS_VMWARE_DIR = os.path.join(EXPORTS_DIR, "exports_vmware")
EXPORTS_OPCA_DIR = os.path.join(EXPORTS_DIR, "exports_opca")
EXPORTS_CMDB_DIR = os.path.join(EXPORTS_DIR, "exports_cmdb")

logging.debug(f"__name__ -> {__name__}")
logging.debug(f"CUR_DIR -> {CUR_DIR}")
logging.debug(f"CONFIG_DIR -> {CONFIG_DIR}")
logging.debug(f"CONFIG_AUTHORIZED_FILES_INI -> {CONFIG_AUTHORIZED_FILES_INI}")
logging.debug(f"CONFIG_DB_INI -> {CONFIG_DB_INI}")
logging.debug(f"EXPORTS_DIR -> {EXPORTS_DIR}")
logging.debug(f"EXPORTS_VMWARE_DIR -> {EXPORTS_VMWARE_DIR}")
logging.debug(f"EXPORTS_OPCA_DIR -> {EXPORTS_OPCA_DIR}")
logging.debug(f"EXPORTS_CMDB_DIR -> {EXPORTS_CMDB_DIR}")