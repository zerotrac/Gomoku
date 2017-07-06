from PyQt5.QtCore import QThread, QObject
from PyQt5.QtCore import QMutexLocker
import random

class score_store(QObject):

	def __init__(self, game_turn):
		super(score_store, self).__init__()
		self.q_value = 0.0
		self.n_value = 0
		self.game_turn = game_turn
		self.finished = False

	def update_value(self, q_delta):
		self.q_value += q_delta
		self.n_value += 1


class ai_thread_default_policy(QThread):
	win_value = 1.0
	draw_value = 0.0
	lose_value = -1.0

	def __init__(self, board, expect_winner, mutex, parent=None):
		super(ai_thread_default_policy, self).__init__(parent)
		self.board = board
		self.expect_winner = expect_winner
		self.mutex = mutex

	def decide_winner(self):
		if self.board.winner == self.expect_winner:
			return self.win_value
		elif self.board.winner == -1:
			return self.draw_value
		else:
			return self.lose_value

	def run(self):
		cnt = 0
		locations = []
		sz = self.board.board_size
		for i in range(sz):
			for j in range(sz):
				if self.board.data[i][j] == 0:
					locations.append((i, j))
		random.shuffle(locations)
		while self.board.winner == 0:
			self.board.play(locations[cnt])
			cnt += 1
		result = self.decide_winner()
		with QMutexLocker(self.mutex):
			self.parent().update_value(result)
