from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from ui.ui_modeselection import Ui_Modeselection

class Qdialog_modeselection(QtWidgets.QDialog):

	# self-defined signals
	game_parameters = pyqtSignal(int, float, int, int, float, int, bool, bool)

	def __init__(self, parent=None):
		super(Qdialog_modeselection, self).__init__(parent)
		self.ui = Ui_Modeselection()
		self.ui.setupUi(self)
		self.make_connections()

	@pyqtSlot(int)
	def modify_spinbox_black(self, player_id):
		if player_id == 0:
			self.ui.spinbox_black.setEnabled(False)
		else:
			self.ui.spinbox_black.setEnabled(True)

	@pyqtSlot(int)
	def modify_spinbox_white(self, player_id):
		if player_id == 0:
			self.ui.spinbox_white.setEnabled(False)
		else:
			self.ui.spinbox_white.setEnabled(True)

	@pyqtSlot()
	def start_game(self):
		self.game_parameters.emit(\
			self.ui.combobox_black.currentIndex(), self.ui.spinbox_black.value(), 0, \
			self.ui.combobox_white.currentIndex(), self.ui.spinbox_white.value(), 0, \
			self.ui.checkbox_retract.isChecked(), self.ui.checkbox_swap2.isChecked())

	def make_connections(self):
		self.ui.pbtn_ok.clicked[bool].connect(self.start_game)
		self.game_parameters.connect(self.parent().start_game)
		self.ui.combobox_black.currentIndexChanged[int].connect(self.modify_spinbox_black)
		self.ui.combobox_white.currentIndexChanged[int].connect(self.modify_spinbox_white)

