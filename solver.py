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


    def win_in_two(self, state, color):
        """
        Returns BLACK or WHITE if any five in a row is detected for the color
        EMPTY otherwise.
        """
        for r in self.board.rows:
            result = self.board.has_five_in_list(r)
            if result != EMPTY:
                return result
        for c in self.board.cols:
            result = self.board.has_five_in_list(c)
            if result != EMPTY:
                return result
        for d in self.board.diags:
            result = self.board.has_five_in_list(d)
            if result != EMPTY:
                return result
        return EMPTY



    def win_in_two_in_list(self, list):
        """
        1 1 0 1 1
        Returns BLACK or WHITE if any five in a rows exist in the list.
        EMPTY otherwise.
        """

        prev = BORDER
        prev2 = BORDER
        counter = 1
        for stone in list:
            if self.get_color(stone) == prev:
                counter += 1
            else:
                counter = 1
                prev = self.get_color(stone)
            if counter == 5 and prev != EMPTY:
                return prev
        return EMPTY

        '''
        prev = BORDER
        counter = 1
        color = EMPTY
        emptyCounter = 0
        for stone in list:
            thisColor = self.get_color(stone)
            if thisColor != EMPTY:
                color = thisColor
            else:
                emptyCounter += 1
            if thisColor == prev or thisColor == EMPTY:
                counter += 1
            else:
                counter = 1
                prev = thisColor
            if counter == 5 and prev != EMPTY and emptyCounter < 3:
                return prev

        return EMPTY
        '''



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
                    best.insert(0, m2)
                    found = True
                    break
            if found:
                continue


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