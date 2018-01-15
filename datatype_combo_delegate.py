from PyQt4.QtCore import pyqtSlot, Qt
from PyQt4.QtGui import QItemDelegate, QComboBox, QApplication, QStyle


# https://stackoverflow.com/questions/41207485/how-to-create-combo-box-qitemdelegate
class DatatypeComboDelegate(QItemDelegate):
    """
    A delegate that places a fully functioning QComboBox in every
    cell of the column to which it's applied
    """

    def __init__(self, parent=None):
        super(DatatypeComboDelegate, self).__init__(parent)
        self._items = []

    def setItems(self, items):
        self._items = items

    def createEditor(self, widget, option, index):
        editor = QComboBox(widget)
        editor.addItems(self._items)
        return editor

    def setEditorData(self, editor, index):
        editor.blockSignals(True)
        value = index.model().data(index, Qt.DisplayRole)
        if value:
            editor.setCurrentIndex(self.get_row_index(value))
        editor.blockSignals(False)

    def get_row_index(self, value):
        i = 0
        for item in self._items:
            if item == value:
                return i
            else:
                i = i + 1
        return 0

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText(), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def paint(self, painter, option, index):
        # print str(index.row()) + " / " + str(len(self.items))
        # text = self.items[index.row()]
        text = self._items[1]
        option.text = text
        QApplication.style().drawControl(QStyle.CE_ItemViewItem, option, painter)

    @pyqtSlot()
    def currentIndexChanged(self):
        self.commitData.emit(self.sender())
