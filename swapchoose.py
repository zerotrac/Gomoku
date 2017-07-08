from PyQt5 import QtCore, QtGui, QtWidgets
from ui.ui_swapchoose import Ui_Swapchoose

class QDialog_swapchoose(QtWidgets.QDialog):

	def __init__(self, parent=None):
		super(QDialog_swapchoose, self).__init__(parent)
		self.ui = Ui_Swapchoose()
		self.ui.setupUi(self)
