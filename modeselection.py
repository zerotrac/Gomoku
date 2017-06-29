from PyQt5 import QtCore, QtGui, QtWidgets
from ui.ui_modeselection import Ui_Modeselection

class Qdialog_modeselection(QtWidgets.QDialog):

	def __init__(self, parent=None):
		super(Qdialog_modeselection, self).__init__(parent)
		self.ui = Ui_Modeselection()
		self.ui.setupUi(self)

		# connections
		self.ui.pbtn_ok.clicked["bool"].connect(self.parent().start_game)

	def s0(self):
		print("hey!")
