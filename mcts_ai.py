from board import Board
from feature import get_features
import numpy as np
import time, math, random
import keras
from mcts_thread import score_store, ai_thread_default_policy
from PyQt5.QtCore import QMutex, QThread, pyqtSignal

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

	def kth(self, result, sz, k=3):
		k_argmax = np.zeros((k, 2), int)
		for x, y in k_argmax:
			x = -1
			y = -1
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

	def judgea_3(self, cnt_mid, cnt_left, block_left, cnt_right, block_right):
		return (cnt_mid == 3 and block_left + block_right == 0 and cnt_left + cnt_right == 0) or \
			   (cnt_mid == 2 and block_left + block_right == 0 and cnt_left + cnt_right == 1) or \
			   (cnt_mid == 1 and block_left + block_right == 0 and ((cnt_left == 2 and cnt_right == 0) or (cnt_right == 2 and cnt_left == 0)))

	def judgea_4(self, cnt_mid, cnt_left, block_left, cnt_right, block_right):
		return (cnt_mid == 4 and block_left + block_right == 0 and cnt_left + cnt_right == 0)

	def judgea_5(self, cnt_mid, cnt_left, block_left, cnt_right, block_right):
		return (cnt_mid == 5)

	def judgeb_4(self, cnt_mid, cnt_left, block_left, cnt_right, block_right):
		return (cnt_mid == 4 and (block_left == 0 or block_right == 0) and cnt_left + cnt_right == 0) or \
			   (cnt_mid == 3 and (cnt_left == 1 or cnt_right == 1)) or \
			   (cnt_mid == 2 and (cnt_left == 2 or cnt_right == 2)) or \
			   (cnt_mid == 1 and (cnt_left == 3 or cnt_right == 3))

	def check_win(self, board, optional_move, other_player):
		a_3 = 0 # huo san
		a_4 = 0 # huo si
		a_5 = 0 # huo wu
		b_4 = 0 # chong si

		for dir in easyBoard.directions:
			cnt1 = 0
			cnt2 = 0
			block_type_1 = -100 # 0=no chess 1=opp chess
			curx, cury = optional_move
			dx, dy = dir
			for i in range(5):
				curx += dx
				cury += dy
				if not board.in_board((curx, cury)) or board.data[curx][cury] == other_player:
					if block_type_1 == -100 or cnt2 != 0:
						block_type_1 = 1
					break
				elif board.data[curx][cury] == 0:
					if block_type_1 == 0:
						break
					block_type_1 = 0
				else:
					if block_type_1 == -100:
						cnt1 += 1
					else:
						cnt2 += 1

			cnt3 = 0
			cnt4 = 0
			block_type_2 = -100
			curx, cury = optional_move
			for i in range(5):
				curx -= dx
				cury -= dy
				if not board.in_board((curx, cury)) or board.data[curx][cury] == other_player:
					if block_type_2 == -100 or cnt4 != 0:
						block_type_2 = 1
					break
				elif board.data[curx][cury] == 0:
					if block_type_2 == 0:
						break
					block_type_2 = 0
				else:
					if block_type_2 == -100:
						cnt3 += 1
					else:
						cnt4 += 1
			#if dir[0] == 1 and dir[1] == 0:
			#	print("dir =", cnt1, cnt2, cnt3, cnt4, block_type_1, block_type_2)

			if self.judgea_3(cnt1 + cnt3 + 1, cnt2, block_type_1, cnt4, block_type_2):
				a_3 += 1
			elif self.judgea_4(cnt1 + cnt3 + 1, cnt2, block_type_1, cnt4, block_type_2):
				a_4 += 1
			elif self.judgea_5(cnt1 + cnt3 + 1, cnt2, block_type_1, cnt4, block_type_2):
				a_5 += 1
			elif self.judgeb_4(cnt1 + cnt3 + 1, cnt2, block_type_1, cnt4, block_type_2):
				b_4 += 1

		#print("pos =", optional_move, a_3, a_4, a_5, b_4)
		if a_5 > 0:
			return 3
		elif a_4 > 0 or b_4 > 1:
			return 2
		elif a_3 > 1 or a_3 + b_4 > 1:
			return 1
		else:
			return 0

	def expand(self, board: easyBoard):
		sz = board.board_size

		if self.is_root:
			features = get_features(board)
			result = policy_network.predict(np.array([features])).reshape(15, 15) * (board.data == 0)
			k_select = 5
			k_argmax = self.kth(result, sz, k=k_select)
			#print(k_argmax)

			value_me = []
			value_op = []
			vme_max = -1
			vop_max = -1
			for k_pos in k_argmax:
				if k_pos[0] == -1 and k_pos[1] == -1:
					continue
				vme = self.check_win(board, k_pos, 3 - board.current_player)
				vop = self.check_win(board, k_pos, board.current_player)
				value_me.append(vme)
				value_op.append(vop)
				if vme > vme_max:
					vme_max = vme
				if vop > vop_max:
					vop_max = vop

			if vme_max >= vop_max:
				for i in range(k_select):
					if k_argmax[i][0] == -1 and k_argmax[i][1] == -1:
						continue
					if value_me[i] == vme_max:
						self.childs.append(mcts_node(False, self, tuple(k_argmax[i])))
						if len(self.childs) == 3:
							break
			else:
				for i in range(k_select):
					if k_argmax[i][0] == -1 and k_argmax[i][1] == -1:
						continue
					if value_op[i] == vop_max:
						self.childs.append(mcts_node(False, self, tuple(k_argmax[i])))
						if len(self.childs) == 3:
							break
			#print(k_argmax)
			#for k_pos in k_argmax:
			#	self.childs.append(mcts_node(False, self, tuple(k_pos)))
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

class mcts_ai(QThread):
	trigger = pyqtSignal()

	def __init__(self, board, parent=None, time_limit=5.0, C=1.2):
		super(mcts_ai, self).__init__(parent)
		self.C = C
		self.root = mcts_node(True)
		self.board = easyBoard(board)
		self.expect_winner = board.current_player
		self.time_limit = time_limit
		self.trigger.connect(self.parent().afterPlay)

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

		new_ai_threads = []
		for i in range(game_turn):
			new_ai_thread = ai_thread_default_policy(easyBoard(self.board), self.expect_winner, mutex, score)
			new_ai_thread.start()
			new_ai_threads.append(new_ai_thread)
		for i in range(game_turn):
			new_ai_threads[i].wait()

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

	def ai_move(self, time_limit=5.0):
		if not self.board.history:
			return 7, 7
		jsy = 0
		start_time = time.time()
		while time.time() - start_time <= time_limit:
			self.uct_search()
			jsy += 1

		optimal = self.root.best_child(0, True)
		#print("jsy =", jsy)
		#print("optimal =", optimal.pos)
		#self.root.print()
		#print(self.board.data)
		return optimal.pos

	def run(self):
		self.parent().board.play(self.ai_move(self.time_limit))
		self.trigger.emit()
