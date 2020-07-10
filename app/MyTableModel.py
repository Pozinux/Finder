import operator

from PySide2 import QtGui, QtCore


# Class for tableview

class MyTableModel(QtCore.QAbstractTableModel):
    def __init__(self, mylist, header, parent=None, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.mylist = mylist
        self.header = header

    def rowCount(self, parent=None, *unused1, **unused2):
        return len(self.mylist)

    def columnCount(self, parent=None, *unused1, **unused2):
        return len(self.mylist[0])

    # def flags(self, index):
    #     return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

    def data(self, index, role=None):

        data = self.mylist[index.row()][index.column()]

        if not index.isValid():
            return None

        if role == QtCore.Qt.BackgroundRole and data == "Non présent dans les exports":
            #  if role == QtCore.Qt.BackgroundRole and (data == "VM Name not in RVTools or OPCA exports." or data == "DNS Name or TAGS not in RVTools or OPCA exports."):
            return QtGui.QColor("orange")  # return QBrush(QtCore.Qt.red) # fonctionne aussi

        # if role == QtCore.Qt.BackgroundRole and data == "0":
        #     return QtGui.QColor("orange")  # return QBrush(QtCore.Qt.orange) # fonctionne aussi

        elif role != QtCore.Qt.DisplayRole:
            return None
        return data

    def headerData(self, col, orientation, role=None):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[col]
        return None

    def sort(self, col, order=None):
        """sort table by given column number col"""
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self.mylist = sorted(self.mylist, key=operator.itemgetter(col))
        if order == QtCore.Qt.DescendingOrder:
            self.mylist.reverse()
        self.emit(QtCore.SIGNAL("layoutChanged()"))
