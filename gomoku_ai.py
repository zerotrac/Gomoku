import keras
import numpy
from board import Board
from feature import get_features
from keras.utils import to_categorical
policy_network = keras.models.load_model("policy.h5")
policy_network._make_predict_function()
#reinforces = [keras.models.load_model("reinforce1.h5"), keras.models.load_model("reinforce2.h5"), keras.models.load_model("reinforce3.h5"), keras.models.load_model("reinforce4.h5")]
reinforces = []
value = None

gauss_noise = lambda scale, shape: numpy.random.normal(0, scale, shape)

def ai_move(board: Board, feature = None, policy:str = "max", version:str = "policy"):
	if board.turn == 1:
		return naive_ai(board)
	if feature is None:
		feature = get_features(board)
	score = lambda x:naive_score(x, board.current_player)
	if version == "policy":
		result = policy_network.predict(numpy.array([feature])).reshape(15, 15)
	elif version == "reinforce1":
		result = reinforces[0].predict(numpy.array([feature])).reshape(15, 15)
	elif version == "reinforce2":
		result = reinforces[1].predict(numpy.array([feature])).reshape(15, 15)
	elif version == "reinforce3":
		result = reinforces[2].predict(numpy.array([feature])).reshape(15, 15)
	elif version == "reinforce4":
		result = reinforces[3].predict(numpy.array([feature])).reshape(15, 15)
	if policy != "sample":
		result += numpy.apply_along_axis(score, 2, feature)# + gauss_noise(0.05, board.shape)
	result = result * (board.data == 0)
	result /= result.sum()
	if policy == "max":
		choice = numpy.unravel_index(result.argmax(), board.shape)
	elif policy == "sample":
		choice = numpy.unravel_index(numpy.random.choice(225, p=result.flatten()), board.shape)
	return choice

def ai_move2(board: Board, feature = None):
	global value
	if not value:
		value = keras.models.load_model("value.h5")
	if board.turn == 1:
		return naive_ai(board)
	if feature is None:
		feature = get_features(board)
	score = lambda x:naive_score(x, board.current_player)
	result = (policy_network.predict([numpy.array([feature]), numpy.array(to_categorical(board.current_player - 1, 2))]).reshape(15, 15) + \
		numpy.apply_along_axis(score, 2, feature)) * \
		(board.data == 0)
	candidates = [numpy.unravel_index(x, result.shape) for x in result.flatten().argsort()[-3:]]
	best_cadidate = (0, (0, 0))
	for candidate in candidates:
		if result[candidate] == 0:
			break
		board.play(candidate)
		prob = value.predict([numpy.array([get_features(board)]), numpy.array(to_categorical(board.current_player - 1, 2))])[0][0] + \
			naive_score(feature[candidate], 3 - board.current_player)
		best_cadidate = max(best_cadidate, (prob, candidate))
		board.undo()
	return best_cadidate[1]

def random_move(board: Board):
	mask = (board.data == 0)
	return numpy.unravel_index(numpy.random.choice(225, p=mask.flatten()/mask.sum()), board.shape)

def naive_score(x: numpy.array, player: int):
	enemy = 3 - player
	if not x[0]:
		return 0
	if numpy.argmax(x[player * 9 - 6:player * 9]) == 4:
		return 4
	elif numpy.argmax(x[enemy * 9 - 6:enemy * 9]) == 4:
		return 3
	elif numpy.argmax(x[player * 9 - 6:player * 9]) == 3 and numpy.argmax(x[player * 9:player * 9 + 3]) == 2:
		return 2
	elif numpy.argmax(x[enemy * 9 - 6:enemy * 9]) == 3 and numpy.argmax(x[enemy * 9:enemy * 9 + 3]) == 2:
		return 1
	else:
		return numpy.argmax(x[3:9]) * 10e-4

def naive_ai(board: Board, feature = None):
	if feature is None:
		feature = get_features(board)
	score = lambda x:naive_score(x, board.current_player)
	result = numpy.apply_along_axis(score, 2, feature) + gauss_noise(10e-6, board.shape)
	mask = (board.data == 0)
	return numpy.unravel_index((result * mask).argmax(), board.shape)

def board_value(board: Board, feature = None):
	return value.predict(numpy.array([get_features(board)]))
