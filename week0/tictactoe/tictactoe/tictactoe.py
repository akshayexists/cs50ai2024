"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy

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
    """
    Returns player who has the next turn on a board.
    """
    x_s = board[0].count(X)+board[1].count(X)+board[2].count(X)
    o_s = board[0].count(O)+board[1].count(O)+board[2].count(O)
    if  x_s<=o_s:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    action_options = set()
    i_i = 0
    j_i = 0
    for i in board:
        for j in i:
            if j == None:
                action_options.add((i_i, j_i))
            j_i+=1
        j_i = 0
        i_i += 1
    return action_options

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    new_board = deepcopy(board)
    a, b = action
    #print(a, b)
    if (a < 0 or b < 0) or (a > 2 or b > 2):
        raise Exception
    elif new_board[a][b] != None:
        raise Exception
    else:
        new_board[a][b] = player(board)
    
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for player in [X, O]:
        #check row
        for row in board:
            if row == [player, player, player]:
                return player
        #check diagonal
        if [board[i][i] for i in range(0, 3)] == [player, player, player]:
            return player
        if [board[i][2-i] for i in range(0, 3)] == [player, player, player]:
            return player
        #check column
        for i in range(3):
            if [board[x][i] for x in range(0, 3)] == [player, player, player]:
                return player
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) != None:
        return True 
    for row in board:
        if EMPTY in row:
            return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    winneris = winner(board)
    if winneris == X:
        return 1
    elif winneris == O:
        return -1
    else:
        return 0

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    #import time
    #start = time.time()
    if terminal(board):
        return None
    calls = 0
    if board == initial_state():
        #hardcode a first move for X if O is chosen, cannot have it looking through all 10^90 possible games
        return (0, 0)
    alpha=-2
    beta=2
    def max_value(board, alpha=alpha, beta=beta, calls=calls):
        calls += 1
        bestmove = ()
        if terminal(board):
            #print(time.time()-start)
            return utility(board), bestmove
        if player(board) == "empty":
            return utility(board), (0, 0)
        v=-10
        for action in actions(board):
            #print('calling max_value')
            vnew = min_value(result(board, action))[0]
            '''
            if vnew > beta:
                break
            alpha=max(alpha, v)
            '''
            if vnew > v:
                v = vnew
                bestmove = action
        #print(time.time()-start)
        return v, bestmove
    
    def min_value(board, alpha=alpha, beta=beta, calls=calls):
        calls += 1
        bestmove = ()
        if terminal(board):
            #print(time.time()-start)
            return utility(board), bestmove
        v=10
        for action in actions(board):
            #print('calling min_value')
            vnew = max_value(result(board, action))[0]
            '''
            if vnew < alpha:
                break
            beta=min(beta, v)
            '''
            if vnew < v:
                v = vnew
                bestmove = action
        #print(bestmove)
        #print(time.time()-start)
        return v, bestmove
    
    if player(board) == X:
        return max_value(board)[1]
    else:
        return min_value(board)[1]