from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from ui.ui_swap3 import Ui_Swap3
from swapchoose import QDialog_swapchoose

class QDialog_swap3(QtWidgets.QDialog):

	# self-defined signals
	getSwapInfo = pyqtSignal(int)

	def __init__(self, parent=None):
		super(QDialog_swap3, self).__init__(parent)
		self.ui = Ui_Swap3()
		self.ui.setupUi(self)
		self.make_connections()
		self.value = -1

	@pyqtSlot()
	def btnswap_clicked(self):
		dialog = QDialog_swapchoose(self)
		dialog.ui.label.setText("<html><head/><body><p>Your opponent choose to swap.</p></body></html>")
		dialog.exec()
		self.getSwapInfo.emit(0)
		self.close()

	@pyqtSlot()
	def btnnoswap_clicked(self):
		dialog = QDialog_swapchoose(self)
		dialog.ui.label.setText("<html><head/><body><p>Your opponent choose not to swap.</p></body></html>")
		dialog.exec()
		self.getSwapInfo.emit(1)
		self.close()

	@pyqtSlot()
	def btnplaymore_clicked(self):
		dialog = QDialog_swapchoose(self)
		dialog.ui.label.setText("<html><head/><body><p>Your opponent choose to play more.</p></body></html>")
		dialog.exec()
		self.getSwapInfo.emit(2)
		self.close()

	@pyqtSlot()
	def make_connections(self):
		self.ui.pbtn_swap.clicked[bool].connect(self.btnswap_clicked)
		self.ui.pbtn_noswap.clicked[bool].connect(self.btnnoswap_clicked)
		self.ui.pbtn_playmore.clicked[bool].connect(self.btnplaymore_clicked)
		self.getSwapInfo.connect(self.parent().afterSwap)
