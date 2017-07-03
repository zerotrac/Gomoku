from PyQt5.QtCore import pyqtSignal, QThread
#from gomoku_ai import ai_move
from mcts_ai import mcts_ai
from time import sleep

'''
class ai_thread_ml(QThread):
	trigger = pyqtSignal()

	def __init__(self, parent):
		super(ai_thread_ml, self).__init__(parent)
		self.trigger.connect(self.parent().afterPlay)

	def run(self):
		sleep(0.1)
		self.parent().board.play(ai_move(self.parent().board))
		self.trigger.emit()
'''
class ai_thread_mcts(QThread):
	trigger = pyqtSignal()

	def __init__(self, parent):
		super(ai_thread_mcts, self).__init__(parent)
		self.trigger.connect(self.parent().afterPlay)

	def run(self):
		self.parent().board.play(mcts_ai(self.parent().board).ai_move())
		self.trigger.emit()
