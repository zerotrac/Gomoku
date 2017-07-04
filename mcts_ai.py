from board import Board
from feature import get_features
import numpy as np
import time, math, random
import keras
from mcts_thread import score_store, ai_thread_default_policy
from PyQt5.QtCore import QMutex

policy_network = keras.models.load_model("policy.h5")
policy_network._make_predict_function()

class easyBoard:
	board_size = 15
	directions = np.array([(1, -1), (1, 0), (1, 1), (0, 1)])

	def __init__(self, board):
		self.data = board.data.copy()
		self.history = board.history.copy()
		self.current_player = board.current_player
		self.winner = board.winner

	@property
	def shape(self):
		return self.data.shape

	def at(self, pos):
		assert(self.in_board(pos))
		return self.data[tuple(pos)]

	def in_board(self, pos):
		return 0 <= pos[0] < self.board_size and 0 <= pos[1] < self.board_size

	def is_empty(self, pos):
		if not self.in_board(pos):
			return False
		if self.data[tuple(pos)] == 0:
			return True
		return False

	def check_winner(self):
		last_move = np.array(self.history[-1])
		for dir in self.directions:
			count = 1
			curx, cury = last_move
			dx, dy = dir
			for i in range(4):
				curx += dx
				cury += dy
				if not self.in_board((curx, cury)) or self.data[curx][cury] != self.current_player:
					break
				count += 1

			curx, cury = last_move
			for i in range(4):
				curx -= dx
				cury -= dy
				if not self.in_board((curx, cury)) or self.data[curx][cury] != self.current_player:
					break
				count += 1

			if count == 5:
				self.winner = self.current_player
		if len(self.history) == self.board_size * self.board_size:
			self.winner = -1
		return self.winner

	def play(self, pos):
		self.data[pos] = self.current_player
		self.history.append(pos)
		self.winner = self.check_winner()
		self.current_player = 2 if self.current_player == 1 else 1

	def undo(self):
		last_move = self.history.pop()
		self.data[last_move[0]][last_move[1]] = 0
		self.winner = 0
		self.current_player = 2 if self.current_player == 1 else 1

class mcts_node:
	win_value = 1.0
	draw_value = 0.0
	lose_value = -1.0

	def __init__(self, is_root, parent=None, pos=(0, 0)):
		self.is_root = is_root
		self.parent = parent
		self.pos = pos
		self.q_value = 0.0
		self.n_value = 0.0
		self.childs = []
		self.which_child = 0

	def can_expand(self):
		return not len(self.childs) or self.which_child < len(self.childs)

	def kth(self, result, sz, k=4):
		k_argmax = np.zeros((k, 2), int)
		k_value = np.zeros(k, float)
		for i in range(sz):
			for j in range(sz):
				for kk in range(k):
					if result[i][j] > k_value[kk]:
						for push in range(k - 1, kk, -1):
							k_argmax[push] = k_argmax[push - 1]
							k_value[push] = k_value[push - 1]
						k_argmax[kk] = i, j
						k_value[kk] = result[i][j]
						break
		return k_argmax

	def expand(self, board: easyBoard):
		sz = board.board_size

		if self.is_root:
			features = get_features(board)
			result = policy_network.predict(np.array([features])).reshape(15, 15) * (board.data == 0)
			k_argmax = self.kth(result, sz)
			print(k_argmax)
			for k_pos in k_argmax:
				self.childs.append(mcts_node(False, self, tuple(k_pos)))
		else:
			available = np.zeros((sz, sz), int)
			dirs = np.array([(-2, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1), (2, 0)])
			locations = []
			for i in range(sz):
				for j in range(sz):
					if board.data[i][j] != 0:
						for dir in dirs:
							ask = (i, j) + dir
							if board.is_empty(ask):
								available[tuple(ask)] = 1
			for i in range(sz):
				for j in range(sz):
					if available[i][j] == 1:
						locations.append((i, j))
			random.shuffle(locations)
			for location in locations:
				self.childs.append(mcts_node(False, self, location))

	def best_child(self, C, cur_player_black):
		best = -1.0
		bestarg = None
		for child in self.childs:
			div = child.q_value / child.n_value
			if not cur_player_black:
				div = -div
			value = div + C * math.sqrt(2 * math.log(self.n_value) / child.n_value)
			if value > best:
				best = value
				bestarg = child
		return bestarg

	def print(self):
		# debug
		for child in self.childs:
			print(child.q_value, child.n_value, child.pos, child.is_root)

class mcts_ai:
	def __init__(self, board: Board, C=1.2):
		self.C = C
		self.root = mcts_node(True)
		self.board = easyBoard(board)
		self.expect_winner = board.current_player

	def tree_policy(self, node):
		expect_node = node
		cur_player_black = True
		while self.board.winner == 0:
			if expect_node.can_expand():
				if not expect_node.childs:
					expect_node.expand(self.board)
				self.board.play(expect_node.childs[expect_node.which_child].pos)
				result = expect_node.childs[expect_node.which_child]
				expect_node.which_child += 1
				return result
			else:
				expect_node = expect_node.best_child(self.C, cur_player_black)
				self.board.play(expect_node.pos)
			cur_player_black = not cur_player_black
		return expect_node

	def decide_winner(self):
		if self.board.winner == self.expect_winner:
			return mcts_node.win_value, 1.0
		elif self.board.winner == -1:
			return mcts_node.draw_value, 1.0
		else:
			return mcts_node.lose_value, 1.0

	def default_policy(self):
		game_turn = 8
		score = score_store(game_turn)
		mutex = QMutex()
		for i in range(8):
			ai_thread_default_policy(easyBoard(self.board), self.expect_winner, mutex, score).start()
		while not score.finished:
			pass
		print(score.q_value, score.n_value*1.0)
		return score.q_value, score.n_value * 1.0
		'''
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
		for i in range(cnt):
			self.board.undo()
		return result
		'''

	def back_up(self, node, result):
		node.q_value += result[0]
		node.n_value += result[1]
		if not node.is_root:
			self.board.undo()
			self.back_up(node.parent, result)

	def uct_search(self):
		expect_node = self.tree_policy(self.root)
		result = self.default_policy() if self.board.winner == 0 else self.decide_winner()
		self.back_up(expect_node, result)

	def ai_move(self, time_limit=3.0):
		if not self.board.history:
			return 7, 7
		jsy = 0
		start_time = time.time()
		while time.time() - start_time <= time_limit:
			self.uct_search()
			jsy += 1

		optimal = self.root.best_child(0, True)
		print("jsy =", jsy)
		print("optimal =", optimal.pos)
		self.root.print()
		print(self.board.data)
		return optimal.pos
