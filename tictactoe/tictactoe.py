"""
Tic Tac Toe Player
"""

import math
import copy
X = "X"
O = "O"
EMPTY = None


def initial_state():
	"""
	Returns starting state of the board.
	"""
	return [[EMPTY, EMPTY, EMPTY],
			[EMPTY, EMPTY, EMPTY],
			[EMPTY, EMPTY, EMPTY]]


def player(board):
	X_count = 0
	O_count = 0
	for i in range(3): # Count the number of Xs and Os
		for j in range(3):
			if board[i][j] == X:
				X_count += 1
			elif board[i][j] == O:
				O_count += 1
	if X_count == O_count: # If X and Os are equal, then it is X's turn
		return X
	return O



def actions(board):
	action_set = set()
	for i in range(3):
		for j in range(3):
			if not board[i][j]:
				action_set.add((i, j))
	return action_set



def result(board, action):
	if board[action[0]][action[1]]:
		raise Exception("You cannot make that action!")
	board_copy = copy.deepcopy(board)
	board_copy[action[0]][action[1]] = player(board)
	return board_copy



def winner(board):
	for i in range(3):
		column = [board[x][i] for x in range(3)]
		if EMPTY not in board[i]: # Skip row if there is an empty square
			if all([x == board[i][0] for x in board[i]]):
				return board[i][0]
		if EMPTY not in column: # Skip row if there is an empty square
			if all([x == column[0] for x in column]):
				return column[0]

	# Check for diagonal matches
	for i in [0, 2]:
		diagonal = [board[abs(x)][abs(i-x)] for x in range(3)]
		if EMPTY not in diagonal: # Skip row if there is an empty square
			if all([x == diagonal[0] for x in diagonal]):
				return diagonal[0]
	return None


def terminal(board):
	# Check for horizontal matches
	for i in range(3):
		column = [board[x][i] for x in range(3)]
		if EMPTY not in board[i]: # Skip row if there is an empty square
			if all([x == board[i][0] for x in board[i]]):
				return True
		if EMPTY not in column: # Skip row if there is an empty square
			if all([x == column[0] for x in column]):
				return True

	# Check for diagonal matches
	for i in [0, 2]:
		diagonal = [board[abs(x)][abs(i-x)] for x in range(3)]
		if EMPTY in diagonal: # Skip row if there is an empty square
			continue
		if all([x == diagonal[0] for x in diagonal]):
			return True

	# Check whether the board is full
	for i in range(3):
		for j in range(3):
			if not board[i][j]:
				return False

	return True


def utility(board):
	# Check for horizontal matches
	for i in range(3):
		column = [board[x][i] for x in range(3)]
		if EMPTY not in board[i]: # Skip row if there is an empty square
			if all([x == board[i][0] for x in board[i]]):
				if board[i][0] == X:
					return 1
				return -1

		if EMPTY not in column: # Skip row if there is an empty square
			if all([x == column[0] for x in column]):
				if column[0] == X:
					return 1
				return -1

	# Check for diagonal matches
	for i in [0, 2]:
		diagonal = [board[abs(x)][abs(i-x)] for x in range(3)]
		if EMPTY in diagonal: # Skip row if there is an empty square
			continue
		if all([x == diagonal[0] for x in diagonal]):
			if diagonal[0] == X:
				return 1
			return -1

	# Check whether the board is full
	for i in range(3):
		for j in range(3):
			if not board[i][j]:
				return False

	return 0


def minimax(board):
	if terminal(board):
		return None
	optimum_actions = set()
	neutral_actions = set()
	for action in actions(board):
		if player(board) == X:
			min_result = min_value(result(board,action))
			if min_result == 1:
				optimum_actions.add(action)
			elif min_result == 0:
				neutral_actions.add(action)
		else:
			max_result = max_value(result(board,action))
			if max_result == -1:
				optimum_actions.add(action)
			elif max_result == 0:
				neutral_actions.add(action)

	if not len(optimum_actions):
		return neutral_actions.pop()
	return optimum_actions.pop()

def min_value(board):
	if terminal(board):
		return utility(board)
	val = 2
	for action in actions(board):
		val = min(val, max_value(result(board, action)))
		if val == -1: # Do alpha beta pruning
			return val
	return val


def max_value(board):
	if terminal(board):
		return utility(board)
	val = -2
	for action in actions(board):
		val = max(val, min_value(result(board, action)))
		if val == 1: # Do alpha beta pruning
			return val
	return val

