import os
import re
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import pyqtSlot, QDir
from ui.ui_board import Ui_Board
from aithread import ai_thread_ml
from mcts_ai import mcts_ai
from board import Board
import random
from modeselection import Qdialog_modeselection
from nextturn import QDialog_nextturn
from swap3 import QDialog_swap3
from swap5 import QDialog_swap5
from swapchoose import QDialog_swapchoose

class Ui(QtWidgets.QWidget):
	boardPos = (28, 28)
	gridSize = (33, 33)
	chessSize = (25, 25)
	starSize = (5, 5)
	blackTarget = (625, 135)
	whiteTarget = (625, 385)
	chessTargetSize = (20, 20)
	player_name = ["human", "naiveAI", "mctsAI"]

	def __init__(self, parent=None):
		super(Ui, self).__init__(parent)
		self.ui = Ui_Board()
		self.ui.setupUi(self)
		self.setFixedSize(650, 520)
		self.ui.choosePanel.hide()

		self.ui.btn_shiftleft10.clicked[bool].connect(self.shift_left_10)
		self.ui.btn_shiftleft1.clicked[bool].connect(self.shift_left_1)
		self.ui.btn_shiftright1.clicked[bool].connect(self.shift_right_1)
		self.ui.btn_shiftright10.clicked[bool].connect(self.shift_right_10)

		self.board = Board()
		self.ai = 0
		self.cursor_x = -1
		self.cursor_y = -1
		self.game_preparation()

	def game_preparation(self):
		self.board = Board()
		self.ui.btnUndo.hide()
		self.ui.label_off.hide()
		self.ui.label_off_name.hide()
		self.ui.label_off_score.hide()
		self.ui.label_def.hide()
		self.ui.label_def_name.hide()
		self.ui.label_def_score.hide()
		self.ui.btn_shiftleft10.hide()
		self.ui.btn_shiftleft1.hide()
		self.ui.btn_shiftright1.hide()
		self.ui.btn_shiftright10.hide()
		self.ui.line_whichstep.hide()

	def paintEvent(self, QPaintEvent):
		painter = QtGui.QPainter(self)
		painter.setBrush(QtCore.Qt.black)
		for i in range(self.boardPos[0], self.boardPos[0] + self.gridSize[0] * 14 + 1, self.gridSize[0]):
			painter.drawLine(i, self.boardPos[1], i, self.boardPos[1] + self.gridSize[1] * 14)
		for i in range(self.boardPos[1], self.boardPos[1] + self.gridSize[1] * 14 + 1, self.gridSize[1]):
			painter.drawLine(self.boardPos[0], i, self.boardPos[0] + self.gridSize[0] * 14, i)
		for i in [(3, 3), (3, 11), (11, 3), (11, 11), (7, 7)]:
			self.drawStar(painter, i)
		if self.ui.line_whichstep.isHidden():
			for i, _ in enumerate(self.board.history):
				self.drawChessPiece(painter, self.board.history[i], QtCore.Qt.white if i % 2 else QtCore.Qt.black)
		else:
			step = int(self.ui.line_whichstep.text())
			for i, _ in enumerate(self.board.history):
				if i < step:
					self.drawChessPiece(painter, self.board.history[i], QtCore.Qt.white if i % 2 else QtCore.Qt.black)
		self.drawCursorPosition(painter, (self.cursor_x, self.cursor_y))
		if self.board.history:
			if self.ui.line_whichstep.isHidden():
				self.drawLastPlayPosition(painter, self.board.history[len(self.board.history) - 1])
			else:
				step = int(self.ui.line_whichstep.text())
				if step > 0:
					self.drawLastPlayPosition(painter, self.board.history[step - 1])
		if self.board.is_start() or not self.ui.line_whichstep.isHidden():
			if self.board.current_player == 1 or not self.ui.line_whichstep.isHidden():
				self.drawChessPieceTarget(painter, self.blackTarget, QtCore.Qt.black)
			if self.board.current_player == 2 or not self.ui.line_whichstep.isHidden():
				self.drawChessPieceTarget(painter, self.whiteTarget, QtCore.Qt.white)
		return super().paintEvent(QPaintEvent)

	def drawLastPlayPosition(self, painter, center):
		painter.setPen(QtCore.Qt.red)
		painter.translate(center[0] * self.gridSize[0] + self.boardPos[0], center[1] * self.gridSize[1] + self.boardPos[1])
		seg = self.gridSize[0] / 8
		thres = 1
		painter.drawLine(0, -seg, 0, -thres)
		painter.drawLine(0, seg, 0, thres)
		painter.drawLine(-seg, 0, -thres, 0)
		painter.drawLine(seg, 0, thres, 0)
		painter.resetTransform()

	def drawCursorPosition(self, painter, center):
		if not self.board.in_board(center):
			return
		painter.setPen(QtCore.Qt.black)
		painter.translate(center[0] * self.gridSize[0] + self.boardPos[0], center[1] * self.gridSize[1] + self.boardPos[1])
		seg = self.gridSize[0] / 4
		painter.drawLine(-seg * 2, -seg * 2, -seg, -seg * 2)
		painter.drawLine(-seg * 2, -seg * 2, -seg * 2, -seg)
		painter.drawLine(seg * 2, -seg * 2, seg, -seg * 2)
		painter.drawLine(seg * 2, -seg * 2, seg * 2, -seg)
		painter.drawLine(-seg * 2, seg * 2, -seg, seg * 2)
		painter.drawLine(-seg * 2, seg * 2, -seg * 2, seg)
		painter.drawLine(seg * 2, seg * 2, seg, seg * 2)
		painter.drawLine(seg * 2, seg * 2, seg * 2, seg)
		painter.resetTransform()

	def drawChessPiece(self, painter, center, color):
		painter.setPen(QtCore.Qt.black)
		painter.setBrush(color)
		painter.translate(center[0] * self.gridSize[0] + self.boardPos[0], center[1] * self.gridSize[1] + self.boardPos[1])
		rect = QtCore.QRectF(-self.chessSize[0] / 2, -self.chessSize[0] / 2, self.chessSize[0], self.chessSize[0])
		painter.drawChord(rect, 0, 5760)
		painter.resetTransform()

	def drawChessPieceTarget(self, painter, center, color):
		painter.setPen(QtCore.Qt.black)
		painter.setBrush(color)
		painter.translate(center[0], center[1])
		rng = self.chessTargetSize[0]
		rect = QtCore.QRectF(-rng / 2, -rng / 2, rng, rng)
		painter.drawChord(rect, 0, 5760)
		painter.resetTransform()

	def drawStar(self, painter, center):
		painter.setBrush(QtCore.Qt.black)
		painter.translate(center[0] * self.gridSize[0] + self.boardPos[0], center[1] * self.gridSize[1] + self.boardPos[1])
		rect = QtCore.QRectF(-self.starSize[0] / 2, -self.starSize[0] / 2, self.starSize[0], self.starSize[0])
		painter.drawChord(rect, 0, 5760)
		painter.resetTransform()

	def mouseMoveEvent(self, QMouseEvent):
		if self.board.winner:
			return super().mouseMoveEvent(QMouseEvent)
		self.cursor_x = int(round((QMouseEvent.x() - self.boardPos[0]) / self.gridSize[0]))
		self.cursor_y = int(round((QMouseEvent.y() - self.boardPos[1]) / self.gridSize[1]))
		self.update()
		return super().mouseMoveEvent(QMouseEvent)

	def mousePressEvent(self, QMouseEvent):
		if self.board.winner:
			return super().mousePressEvent(QMouseEvent)
		chess_x = int(round((QMouseEvent.x() - self.boardPos[0]) / self.gridSize[0]))
		chess_y = int(round((QMouseEvent.y() - self.boardPos[1]) / self.gridSize[1]))
		pos = (chess_x, chess_y)
		if self.board.is_start() and self.board.current_player_type == 0 and self.board.in_board(pos) and self.board.at(pos) == 0:
			self.board.play(pos)
			self.afterPlay()
		self.update()
		return super().mousePressEvent(QMouseEvent)

	winning_message = {
		-1: "Draw!",
		1: "Black wins!",
		2: "White wins!"
	}

	def ai_turn(self):
		#self.board.play(ai_move(self.board))
		#self.afterPlay()
		if self.board.current_player_type == 1:
			ai_thread_ml(self, self.board.get_current_delay()).start()
		else:
			mcts_ai(self.board, self, self.board.get_current_delay()).start()

	@pyqtSlot()
	def afterPlay(self):
		if self.board.winner:
			self.setWindowTitle(self.winning_message[self.board.winner])
			if self.board.winner == 1:
				self.board.off_score += 1
			else:
				self.board.def_score += 1
			self.update()
			QDialog_nextturn(self).exec()
			# sleep(2)
			'''
			fileName = "save/" + strftime("%Y%m%d_%H%M%S", localtime())
			fileName += "_" + self.player_name[self.board.off_id] + "_" + self.player_name[
				self.board.def_id] + "_" + str(self.board.winner) + ".txt"
			print(fileName)
			opt = open(fileName, "w")
			print(len(self.board.history), file=opt)
			for posx, posy in self.board.history:
				print(posx, posy, file=opt)
			opt.close()
			self.start_game(self.board.def_id, self.board.def_delay, self.board.def_score, self.board.off_id,
							self.board.off_delay, self.board.off_score, self.board.can_retract, self.board.can_swap2)
			'''
			return
		if self.board.swapped == -1 and len(self.board.history) == 3:
			QDialog_swap3(self).exec()
		elif self.board.swapped == 2 and len(self.board.history) == 5:
			QDialog_swap5(self).exec()
		elif self.board.current_player_type > 0:
			self.ai_turn()
		else:
		#else:
			'''
			if self.ui.chkSwap2.checkState() == QtCore.Qt.Checked:
				if self.board.turn == 3:
					self.setWindowTitle("Swap 1")
				elif self.board.turn == 5:
					self.setWindowTitle("Swap 2")
			'''
		self.update()

	@pyqtSlot(int)
	def afterSwap(self, swapped):
		self.board.swap_start(swapped)
		self.ui.label_off_name.setText(self.player_name[self.board.off_id])
		self.ui.label_off_score.setText(str(self.board.off_score))
		self.ui.label_def_name.setText(self.player_name[self.board.def_id])
		self.ui.label_def_score.setText(str(self.board.def_score))
		self.update()
		if self.board.current_player_type > 0:
			self.ai_turn()

	def on_btnStart_clicked(self, checked=True):
		if checked:
			return
		Qdialog_modeselection(self).exec()

	def on_btnLoad_clicked(self, checked=True):
		if checked:
			return
		path = QFileDialog.getOpenFileName(self, "Load Game", QDir.currentPath()+"/save")[0]
		if not path:
			return
		self.start_game(0, 0, 0, 0, 0, 0, False, False)
		self.board.in_game = False

		self.ui.label_off_score.hide()
		self.ui.label_def_score.hide()
		self.ui.btn_shiftleft10.show()
		self.ui.btn_shiftleft1.show()
		self.ui.btn_shiftright1.show()
		self.ui.btn_shiftright10.show()
		self.ui.line_whichstep.show()

		names = re.findall("_([^_]+)", re.findall("/([^/]+)", path)[-1])
		self.ui.label_off_name.setText(names[1])
		self.ui.label_def_name.setText(names[2])

		iptFile = open(path, "r")
		elem_count = int(iptFile.readline().strip())
		for i in range(elem_count):
			rd = iptFile.readline().strip().split()
			self.board.history.append((int(rd[0]), int(rd[1])))
		iptFile.close()
		self.ui.line_whichstep.setText(str(len(self.board.history)))
		self.update()
		#print(self.board.history)

	def on_btnAi_clicked(self, checked=True):
		if checked:
			return
		self.board = Board()
		self.ai = random.randint(1, 2)
		self.setWindowTitle(QtCore.QCoreApplication.translate("Board", "Gomoku"))
		self.afterPlay()
		self.update()

	def on_btnUndo_clicked(self, checked=True):
		if checked:
			return
		if self.board.turn == 0 or (self.ai == 1 and self.board.turn == 1):
			return
		self.board.undo()
		if self.ai == self.board.current_player:
			self.board.undo() # Undo two moves if play against AI
		self.update()

	@pyqtSlot(int, float, int, int, float, int, bool, bool)
	def start_game(self, off_id, off_delay, off_score, def_id, def_delay, def_score, can_retract, can_swap2):
		self.game_preparation()
		self.board = Board(off_id, off_delay, off_score, def_id, def_delay, def_score, can_retract, can_swap2)
		self.board.start()
		self.setWindowTitle("Gomoku")
		self.ui.btnUndo.show()
		self.ui.btnUndo.setEnabled(can_retract)
		if off_id > 0 or def_id > 0:
			self.ui.btnUndo.setEnabled(False)
		self.ui.label_off.show()
		self.ui.label_off_name.show()
		self.ui.label_off_name.setText(self.player_name[off_id])
		self.ui.label_off_score.show()
		self.ui.label_off_score.setText(str(off_score))
		self.ui.label_def.show()
		self.ui.label_def_name.show()
		self.ui.label_def_name.setText(self.player_name[def_id])
		self.ui.label_def_score.show()
		self.ui.label_def_score.setText(str(def_score))
		self.update()
		if self.board.current_player_type > 0:
			self.ai_turn()

	@pyqtSlot()
	def shift_left_1(self):
		step = int(self.ui.line_whichstep.text())
		step -= 1
		if step < 0:
			step = 0
		self.ui.line_whichstep.setText(str(step))
		self.update()

	@pyqtSlot()
	def shift_left_10(self):
		step = int(self.ui.line_whichstep.text())
		step -= 10
		if step < 0:
			step = 0
		self.ui.line_whichstep.setText(str(step))
		self.update()

	@pyqtSlot()
	def shift_right_1(self):
		step = int(self.ui.line_whichstep.text())
		step += 1
		if step > len(self.board.history):
			step = len(self.board.history)
		self.ui.line_whichstep.setText(str(step))
		self.update()

	@pyqtSlot()
	def shift_right_10(self):
		step = int(self.ui.line_whichstep.text())
		step += 10
		if step > len(self.board.history):
			step = len(self.board.history)
		self.ui.line_whichstep.setText(str(step))
		self.update()

def gui_start():
	import sys
	app = QtWidgets.QApplication(sys.argv)
	app.setStyle(QtWidgets.QStyleFactory.create("Fusion"))
	window = Ui()
	window.show()
	sys.exit(app.exec_())
