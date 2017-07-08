from PyQt5.QtCore import pyqtSignal, QThread
from mcts_ai import mcts_ai
from gomoku_ai import ai_move
from time import sleep, time

class ai_thread_ml(QThread):
	trigger = pyqtSignal()

	def __init__(self, parent, time_limit):
		super(ai_thread_ml, self).__init__(parent)
		self.time_limit = time_limit
		self.trigger.connect(self.parent().afterPlay)

	def run(self):
		timea = time()
		play_pos = ai_move(self.parent().board)
		timeb = time()
		if timeb - timea < self.time_limit:
			sleep(self.time_limit - (timeb - timea))
		self.parent().board.play(play_pos)
		self.trigger.emit()


class ai_thread_mcts(QThread):
	trigger = pyqtSignal()

	def __init__(self, parent):
		super(ai_thread_mcts, self).__init__(parent)
		self.trigger.connect(self.parent().afterPlay)

	def run(self):
		self.parent().board.play(mcts_ai(self.parent().board).ai_move())
		self.trigger.emit()
