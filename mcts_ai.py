from board import Board
import numpy as np
import time
import math
import random

class easyBoard:
	board_size = 15

	def __init__(self, board: Board):
		self.data = board.data.copy()
		self.history = board.history.copy()
		self.current_player = board.current_player
		self.winner = board.winner

	def in_board(self, pos):
		return 0 <= pos[0] < self.board_size and 0 <= pos[1] < self.board_size

	def is_empty(self, pos):
		if not self.in_board(pos):
			return False
		if self.data[tuple(pos)] == 0:
			return True
		return False

	def check_winner(self):
		last_move = self.history[-1]
		directions = np.array([(1, -1), (1, 0), (1, 1), (0, 1)])
		for dir in directions:
			count = 1
			for i in range(1, self.board_size):
				if not self.in_board(last_move + i * dir) or self.data[tuple(last_move + i * dir)] != self.current_player:
					break
				count += 1
			for i in range(-1, -self.board_size, -1):
				if not self.in_board(last_move + i * dir) or self.data[tuple(last_move + i * dir)] != self.current_player:
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
	draw_value = 0.3
	lose_value = 0.0

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

	def expand(self, board: easyBoard):
		sz = board.board_size
		available = np.zeros((sz, sz), int)
		dirs = []
		for i in range(-2, 3):
			for j in range(-2, 3):
				dirs.append((i, j))
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
				div = 1.0 - div
			value = div + C * math.sqrt(1.96 * math.log(self.n_value) / child.n_value)
			if value > best:
				best = value
				bestarg = child
		return bestarg

class mcts_ai:

	def __init__(self, C, board: Board):
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
				self.board.play(expect_node.childs[expect_node.which_child])
				result = expect_node.child[expect_node.which_child]
				expect_node.which_child += 1
				return result
			else:
				expect_node = expect_node.best_child(self.C, cur_player_black)
				self.board.play(expect_node.pos)
			cur_player_black = not cur_player_black
		return expect_node

	def decide_winner(self):
		if self.board.winner == self.expect_winner:
			return mcts_node.win_value
		elif self.board.winner == -1:
			return mcts_node.draw_value
		else:
			return mcts_node.lose_value

	def random_game(self):
		cnt = 0
		locations = []
		sz = self.board.board_size
		for i in range(sz):
			for j in range(sz):
				if self.board[i][j] == 0:
					locations.append((i, j))
		random.shuffle(locations)
		while self.board.winner == 0:
			cnt += 1
			self.board.play(locations[cnt - 1])
		result = self.decide_winner()
		for i in range(cnt):
			self.board.undo()
		return result

	def uct_search(self):
		expect_node = self.tree_policy(self.root)
		result = self.random_game() if self.board.winner == 0 else self.decide_winner()
		back


	def ai_move(self, time_limit = 3.0):
		start_time = time.time()
		while time.time() - start_time <= time_limit:
			self.uct_search()

