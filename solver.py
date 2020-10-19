from transposition_table_simple import TranspositionTable
import time
from board_util import (
    GoBoardUtil,
    BLACK,
    WHITE,
    EMPTY,
    BORDER,
    where1d
)


INFINITY = 1000000

class Solver:
    def __init__(self, board):
        self.board = board
        self.timelimit = 1
        self.startTime = -1


    def solve(self):
        tt = TranspositionTable()
        board = self.board.copy()
        self.startTime = time.time()
        return self.minimaxOR(board, tt)



    def get_code(self, state):
        indices = range(0, (state.size * state.size))
        code = ""
        for i in where1d(state.board != BORDER):
            code += str(state.board[i])
        return code



    def sortedBest(self, state, color):
        opponent = GoBoardUtil.opponent(color)
        empty = state.get_empty_points()
        best = []
        threats = []
        winning = False
        for m in empty:
            #Winning moves
            newState = state.copy()
            newState.play_move(m, color)
            result = newState.detect_five_in_a_row()
            if result == color:
                winning = True
                best.insert(0, m)
                continue

            #Block winning moves and double threats
            newState = state.copy()
            newState.play_move(m, opponent)
            result = newState.detect_five_in_a_row()
            if result == opponent:
                threats.append(m)
                best.insert(0, m)
                continue

            '''
            #Check win in two moves
            newState = state.copy()
            newState.play_move(m, color)
            found = False
            for m2 in newState.get_empty_points():
                newState2 = newState.copy()
                newState2.play_move(m2, color)
                result = newState2.detect_five_in_a_row()
                if result == color:
                    best.insert(0, m)
                    found = True
                    break
            if found:
                continue
            '''

            best.append(m)

        return len(threats) > 1 and not winning, best



    def minimaxOR(self, state, tt):
        current = time.time()
        if current - self.startTime > self.timelimit:
            return None

        output = tt.lookup(self.get_code(state))
        if output != None:
            return output

        result = state.detect_five_in_a_row()
        if result == BLACK:
            if self.board.current_player == WHITE:
                tt.store(self.get_code(state), [None, -1])
                return [None, -1]
            else:
                tt.store(self.get_code(state), [None, 1])
                return [None, 1]
        elif result == WHITE:
            if self.board.current_player == WHITE:
                tt.store(self.get_code(state), [None, 1])
                return [None, 1]
            else:
                tt.store(self.get_code(state), [None, -1])
                return [None, -1]

        elif state.get_empty_points().size == 0:
            tt.store(self.get_code(state), [None, 0])
            return [None, 0]

        bestMove = None
        bestVal = -INFINITY
        doomed, bestArr = self.sortedBest(state, state.current_player)
        if doomed:
            tt.store(self.get_code(state), [bestArr[0], -1])
            return [bestArr[0], -1]
 

        for m in bestArr:
            newState = state.copy()
            newState.play_move(m, newState.current_player)
            best = self.minimaxAND(newState, tt)
            if best == None:
                return None
            if best[1] > bestVal:
                bestMove = m
                bestVal = best[1]
            if best[1] == 1:
                break

        tt.store(self.get_code(state), [bestMove, bestVal])
        return [bestMove, bestVal]



    def minimaxAND(self, state, tt):
        current = time.time()
        if current - self.startTime > self.timelimit:
            return None

        output = tt.lookup(self.get_code(state))
        if output != None:
            return output

        result = state.detect_five_in_a_row()
        if result == BLACK:
            if self.board.current_player == WHITE:
                tt.store(self.get_code(state), [None, -1])
                return [None, -1]
            else:
                tt.store(self.get_code(state), [None, 1])
                return [None, 1]
        elif result == WHITE:
            if self.board.current_player == WHITE:
                tt.store(self.get_code(state), [None, 1])
                return [None, 1]
            else:
                tt.store(self.get_code(state), [None, -1])
                return [None, -1]

        elif state.get_empty_points().size == 0:
            tt.store(self.get_code(state), [None, 0])
            return [None, 0]

        bestMove = None
        bestVal = INFINITY
        doomed, bestArr = self.sortedBest(state, state.current_player)
        if doomed:
            tt.store(self.get_code(state), [bestArr[0], 1])
            return [bestArr[0], 1]

        for m in bestArr:
            newState = state.copy()
            newState.play_move(m, newState.current_player)
            best = self.minimaxOR(newState, tt)
            if best == None:
                return None
            if best[1] < bestVal:
                bestMove = m
                bestVal = best[1]
            if best[1] == -1:
                break
                
        tt.store(self.get_code(state), [bestMove, bestVal])
        return [bestMove, bestVal]