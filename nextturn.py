from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QDir
from ui.ui_nextturn import Ui_Nextturn
from time import localtime, strftime

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
		if board.swapped == 0:
			self.parent().start_game(board.off_id, board.off_delay, board.off_score, board.def_id, board.def_delay, board.def_score, board.can_retract, board.can_swap2)
		else:
			self.parent().start_game(board.def_id, board.def_delay, board.def_score, board.off_id, board.off_delay, board.off_score, board.can_retract, board.can_swap2)

	@pyqtSlot()
	def btncancel_clicked(self):
		self.parent().game_preparation()

	@pyqtSlot()
	def btnsave_clicked(self):
		fileName = "/save/" + strftime("%Y%m%d_%H%M%S", localtime())
		fileName += "_" + self.parent().player_name[self.parent().board.off_id] + "_" + self.parent().player_name[self.parent().board.def_id] + "_" + str(self.parent().board.winner) + ".txt"
		path = QFileDialog.getSaveFileName(self, "Save Game", QDir.currentPath()+fileName)[0]
		if path:
			opt = open(path, "w")
			print(len(self.parent().board.history), file=opt)
			for posx, posy in self.parent().board.history:
				print(posx, posy, file=opt)
			opt.close()

	def make_connections(self):
		self.ui.pbtn_ok.clicked[bool].connect(self.btnok_clicked)
		self.ui.pbtn_cancel.clicked[bool].connect(self.btncancel_clicked)
		self.ui.pbtn_save.clicked[bool].connect(self.btnsave_clicked)