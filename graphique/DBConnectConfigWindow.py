# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:/Bull/Dev/Finder/Finder/graphique\DBConnectConfigWindow.ui',
# licensing of 'C:/Bull/Dev/Finder/Finder/graphique\DBConnectConfigWindow.ui' applies.
#
# Created: Mon Jul 13 16:39:34 2020
#      by: pyside2-uic  running on PySide2 5.12.3
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_DBConnectConfigWindow(object):
    def setupUi(self, DBConnectConfigWindow):
        DBConnectConfigWindow.setObjectName("DBConnectConfigWindow")
        DBConnectConfigWindow.resize(264, 266)
        self.gridLayout = QtWidgets.QGridLayout(DBConnectConfigWindow)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(DBConnectConfigWindow)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)
        self.lineEdit = QtWidgets.QLineEdit(DBConnectConfigWindow)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 1, 0, 1, 2)
        self.label_2 = QtWidgets.QLabel(DBConnectConfigWindow)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 2)
        self.lineEdit_2 = QtWidgets.QLineEdit(DBConnectConfigWindow)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridLayout.addWidget(self.lineEdit_2, 3, 0, 1, 2)
        self.label_3 = QtWidgets.QLabel(DBConnectConfigWindow)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 4, 0, 1, 2)
        self.lineEdit_3 = QtWidgets.QLineEdit(DBConnectConfigWindow)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.gridLayout.addWidget(self.lineEdit_3, 5, 0, 1, 2)
        self.label_4 = QtWidgets.QLabel(DBConnectConfigWindow)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 6, 0, 1, 2)
        self.lineEdit_4 = QtWidgets.QLineEdit(DBConnectConfigWindow)
        self.lineEdit_4.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_4.setReadOnly(False)
        self.lineEdit_4.setClearButtonEnabled(False)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.gridLayout.addWidget(self.lineEdit_4, 7, 0, 1, 2)
        self.pushButton = QtWidgets.QPushButton(DBConnectConfigWindow)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 8, 0, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(DBConnectConfigWindow)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 8, 1, 1, 1)

        self.retranslateUi(DBConnectConfigWindow)
        QtCore.QMetaObject.connectSlotsByName(DBConnectConfigWindow)

    def retranslateUi(self, DBConnectConfigWindow):
        DBConnectConfigWindow.setWindowTitle(QtWidgets.QApplication.translate("DBConnectConfigWindow", "Database connection configuration", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("DBConnectConfigWindow", "Database server name:", None, -1))
        self.lineEdit.setPlaceholderText(QtWidgets.QApplication.translate("DBConnectConfigWindow", "Host ?", None, -1))
        self.label_2.setText(QtWidgets.QApplication.translate("DBConnectConfigWindow", "Database name :", None, -1))
        self.lineEdit_2.setPlaceholderText(QtWidgets.QApplication.translate("DBConnectConfigWindow", "Database ?", None, -1))
        self.label_3.setText(QtWidgets.QApplication.translate("DBConnectConfigWindow", "Database user name:", None, -1))
        self.lineEdit_3.setPlaceholderText(QtWidgets.QApplication.translate("DBConnectConfigWindow", "User ?", None, -1))
        self.label_4.setText(QtWidgets.QApplication.translate("DBConnectConfigWindow", "Database password:", None, -1))
        self.lineEdit_4.setPlaceholderText(QtWidgets.QApplication.translate("DBConnectConfigWindow", "Password ?", None, -1))
        self.pushButton.setText(QtWidgets.QApplication.translate("DBConnectConfigWindow", "Cancel", None, -1))
        self.pushButton_2.setText(QtWidgets.QApplication.translate("DBConnectConfigWindow", "Ok", None, -1))

