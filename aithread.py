from PyQt5.QtCore import pyqtSignal, QThread
from gomoku_ai import ai_move
from time import sleep

class ai_thread(QThread):
	trigger = pyqtSignal()

	def __init__(self, parent):
		super(ai_thread, self).__init__(parent)
		self.trigger.connect(self.parent().afterPlay)

	def run(self):
		sleep(0.1)
		self.parent().board.play(ai_move(self.parent().board))
		self.trigger.emit()
