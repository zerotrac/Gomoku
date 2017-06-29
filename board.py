import numpy as np

class Board(object):
	board_size = 15

	def __init__(self, off_id=0, off_delay=1.0, def_id=0, def_delay=1.0, can_retract=False, can_swap2=False):
		self.data = np.zeros((self.board_size, self.board_size), int)
		self.history = []
		self.current_player = 1
		self.winner = 0
		self.in_game = False

		'''
		off=offensive position, the player who plays black
		def=defensive position, the player who plays white
		'''
		self.off_id, self.off_delay, self.off_score = off_id, off_delay, 0
		self.def_id, self.def_delay, self.def_score = def_id, def_delay, 0
		self.can_retract = can_retract
		self.can_swap2 = can_swap2


	@property
	def turn(self):
		return len(self.history)

	@property
	def shape(self):
		return self.data.shape

	def in_board(self, pos):
		return 0 <= pos[0] < self.board_size and 0 <= pos[1] < self.board_size

	def at(self, pos):
		assert(self.in_board(pos))
		return self.data[tuple(pos)]

	def is_start(self):
		return self.in_game

	def start(self):
		self.in_game = True

	def play(self, pos):
		assert self.in_board(pos)
		if self.data[pos] or self.winner:
			return
		self.data[pos] = self.current_player
		self.history.append(pos)
		winner = self.check_winner()
		self.current_player = 2 if self.current_player == 1 else 1

	def undo(self):
		assert self.history
		last_move = self.history.pop()
		self.data[last_move[0]][last_move[1]] = 0
		self.winner = 0
		self.current_player = 2 if self.current_player == 1 else 1

	def check_winner(self):
		assert self.history
		last_move = self.history[-1]
		directions = np.array([(1, -1), (1, 0), (1, 1), (0, 1)])
		for dir in directions:
			count = 1
			for i in range(1, self.board_size):
				if not self.in_board(last_move + i * dir) or \
					self.data[tuple(last_move + i * dir)] != self.current_player:
					break
				count += 1
			for i in range(-1, -self.board_size, -1):
				if not self.in_board(last_move + i * dir) or \
					self.data[tuple(last_move + i * dir)] != self.current_player:
					break
				count += 1
			if count == 5:
				self.winner = self.current_player
		if len(self.history) == self.board_size * self.board_size:
			self.winner = -1
		return self.winner
