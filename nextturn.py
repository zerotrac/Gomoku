from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from ui.ui_nextturn import Ui_Nextturn

class QDialog_nextturn(QtWidgets.QDialog):

	# self-defined signals
	game_continue = pyqtSignal()
	game_return = pyqtSignal()

	def __init__(self, parent=None):
		super(QDialog_nextturn, self).__init__(parent)
		self.ui = Ui_Nextturn()
		self.ui.setupUi(self)
		self.make_connections()

	@pyqtSlot()
	def btnok_clicked(self):
		board = self.parent().board
		self.parent().start_game(board.def_id, board.def_delay, board.def_score, board.off_id, board.off_delay, board.off_score, board.can_retract, board.can_swap2)

	@pyqtSlot()
	def btncancel_clicked(self):
		self.parent().game_preparation()

	def make_connections(self):
		self.ui.pbtn_ok.clicked[bool].connect(self.btnok_clicked)
		self.ui.pbtn_cancel.clicked[bool].connect(self.btncancel_clicked)