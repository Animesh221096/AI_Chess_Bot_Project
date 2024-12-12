import pygame
import numpy as np

from const import *
from Eval_Values import *
# from game import Game

import chess

file = open("depth_logs.txt", "w")

class Chess_AI:

    def __init__(self) -> None:
        self.AI_Board_ref = chess.Board()

        self.AI_Move_List = []

        self.pieces_base_value = {"O" : np.array([ 85, 320, 330, 500, 900]), # Opening
                                  "M" : np.array([ 90, 320, 330, 510, 900]), # Midgame
                                  "E" : np.array([100, 320, 330, 520, 900])} # Endgame
        
        self.game_stage = "O"

        self.captured_piece = 0

        self.pawntable = PAWN_TABLE[self.game_stage]

        self.knightstable = KNIGHT_TABLE[self.game_stage]
        
        self.bishopstable = BISHOP_TABLE[self.game_stage]
        
        self.rookstable = ROOK_TABLE[self.game_stage]
        
        self.queenstable = QUEENS_TABLE[self.game_stage]
        
        self.kingstable = KING_TABLE[self.game_stage]

    def eval_function(self):
        if self.AI_Board_ref.is_checkmate():
            if self.AI_Board_ref.turn:
                return -9999
            else:
                return 9999
        if self.AI_Board_ref.is_stalemate():
                return 0
        if self.AI_Board_ref.is_insufficient_material():
                return 0
        wp = len(self.AI_Board_ref.pieces(chess.PAWN, chess.WHITE))
        bp = len(self.AI_Board_ref.pieces(chess.PAWN, chess.BLACK))
        wn = len(self.AI_Board_ref.pieces(chess.KNIGHT, chess.WHITE))
        bn = len(self.AI_Board_ref.pieces(chess.KNIGHT, chess.BLACK))
        wb = len(self.AI_Board_ref.pieces(chess.BISHOP, chess.WHITE))
        bb = len(self.AI_Board_ref.pieces(chess.BISHOP, chess.BLACK))
        wr = len(self.AI_Board_ref.pieces(chess.ROOK, chess.WHITE))
        br = len(self.AI_Board_ref.pieces(chess.ROOK, chess.BLACK))
        wq = len(self.AI_Board_ref.pieces(chess.QUEEN, chess.WHITE))
        bq = len(self.AI_Board_ref.pieces(chess.QUEEN, chess.BLACK))
        
        # material = 100 * (wp - bp) + 320 * (wn - bn) + 330 * (wb - bb) + 500 * (wr - br) + 900 * (wq - bq)

        material = sum(self.pieces_base_value[self.game_stage] * [(wp - bp),  (wn - bn), (wb - bb), (wr - br), (wq - bq)])


        pawnsq = sum([self.pawntable[i] for i in self.AI_Board_ref.pieces(chess.PAWN, chess.WHITE)])
        pawnsq = pawnsq + sum([-self.pawntable[chess.square_mirror(i)]
                            for i in self.AI_Board_ref.pieces(chess.PAWN, chess.BLACK)])
        
        knightsq = sum([self.knightstable[i] for i in self.AI_Board_ref.pieces(chess.KNIGHT, chess.WHITE)])
        knightsq = knightsq + sum([-self.knightstable[chess.square_mirror(i)]
                                for i in self.AI_Board_ref.pieces(chess.KNIGHT, chess.BLACK)])
        
        bishopsq = sum([self.bishopstable[i] for i in self.AI_Board_ref.pieces(chess.BISHOP, chess.WHITE)])
        bishopsq = bishopsq + sum([-self.bishopstable[chess.square_mirror(i)]
                                for i in self.AI_Board_ref.pieces(chess.BISHOP, chess.BLACK)])
        
        rooksq = sum([self.rookstable[i] for i in self.AI_Board_ref.pieces(chess.ROOK, chess.WHITE)])
        rooksq = rooksq + sum([-self.rookstable[chess.square_mirror(i)]
                            for i in self.AI_Board_ref.pieces(chess.ROOK, chess.BLACK)])
        
        queensq = sum([self.queenstable[i] for i in self.AI_Board_ref.pieces(chess.QUEEN, chess.WHITE)])
        queensq = queensq + sum([-self.queenstable[chess.square_mirror(i)]
                                for i in self.AI_Board_ref.pieces(chess.QUEEN, chess.BLACK)])
        
        kingsq = sum([self.kingstable[i] for i in self.AI_Board_ref.pieces(chess.KING, chess.WHITE)])
        kingsq = kingsq + sum([-self.kingstable[chess.square_mirror(i)]
                            for i in self.AI_Board_ref.pieces(chess.KING, chess.BLACK)])
        
        eval = material + pawnsq + knightsq + bishopsq + rooksq + queensq + kingsq
        
        if self.AI_Board_ref.turn:
            return eval
        else:
            return -eval


    def select_move(self, depth):
        bestMove = chess.Move.null()
        bestValue = -99999
        alpha = -100000
        beta = 100000
        for move in self.AI_Board_ref.legal_moves:
            self.AI_Board_ref.push(move)
            boardValue = -self.alphabeta(-beta, -alpha,
                                          depth - 1)
            if boardValue > bestValue:
                bestValue = boardValue
                bestMove = move
            if (boardValue > alpha):
                alpha = boardValue
            self.AI_Board_ref.pop()
        return bestMove 

        
    def alphabeta(self, alpha, beta, depthleft):
        bestscore = -9999
        if (depthleft == 0):
            file.write("\n---- ---- ---- ----\n")
            return self.quiesce(alpha, beta, 0)
        for move in self.AI_Board_ref.legal_moves:
            self.AI_Board_ref.push(move)
            score = -self.alphabeta(-beta, -alpha,
                                     depthleft - 1)
            self.AI_Board_ref.pop()
            if (score >= beta):
                return score
            if (score > bestscore):
                bestscore = score
            if (score > alpha):
                alpha = score  
        return bestscore


    def quiesce(self, alpha, beta, dep):

        stand_pat = self.eval_function()

        if (stand_pat >= beta):
            file.write(f"{dep}\n")
            return beta
        if (alpha < stand_pat):
            alpha = stand_pat

        for move in self.AI_Board_ref.legal_moves:
            if self.AI_Board_ref.is_capture(move):
                self.AI_Board_ref.push(move)
                score = -self.quiesce(-beta, -alpha, dep+1)
                self.AI_Board_ref.pop()
                if (score >= beta):
                    return beta
                if (score > alpha):
                    alpha = score

        return alpha


    def AI_Move(self, display_board, depth):
        mov = self.select_move(depth)

        if self.AI_Board_ref.is_capture(mov):
            self.captured_piece += 1

        is_mid = 0

        is_mid += (self.captured_piece >= 4) + (int(self.AI_Board_ref.fen()[-1]) >= 8) + (self.AI_Board_ref.fen().split()[-4] == "-")

        if is_mid >= 2:
            self.game_stage = "M"


        wn = len(self.AI_Board_ref.pieces(chess.KNIGHT, chess.WHITE))
        bn = len(self.AI_Board_ref.pieces(chess.KNIGHT, chess.BLACK))
        wb = len(self.AI_Board_ref.pieces(chess.BISHOP, chess.WHITE))
        bb = len(self.AI_Board_ref.pieces(chess.BISHOP, chess.BLACK))
        wr = len(self.AI_Board_ref.pieces(chess.ROOK, chess.WHITE))
        br = len(self.AI_Board_ref.pieces(chess.ROOK, chess.BLACK))
        wq = len(self.AI_Board_ref.pieces(chess.QUEEN, chess.WHITE))
        bq = len(self.AI_Board_ref.pieces(chess.QUEEN, chess.BLACK))

        is_end = 0

        is_end += ((wn + bn + wb + bb) < 4) + ((wr + br) < 2) + ((wq + bq) == 0) + ((self.captured_piece > 10))

        if (is_end >=3 ):
            self.game_stage = "E"


        self.AI_Board_ref.push(mov)


        print("\n( ~~~~ ~~~~ ~~~~ ~~~~\n>")
        self.AI_Move_List.append(mov)

        move_str = str(mov)
        print("---- ---- ---- ----")
        initial_row = 8 - int(move_str[1])
        final_row = 8 - int(move_str[3])
        print("initial_row", initial_row, "final_row", final_row)
        initial_col = ord(move_str[0]) - 97
        final_col = ord(move_str[2]) - 97
        print("initial_col", initial_col, "final_col", final_col)
        print("---- ---- ---- ----")

        print("AI made the move")
        print(self.AI_Board_ref)

        if initial_col == 0 and final_col == 1 and initial_row == 3 and final_row == 3:
            print("|||| |||| ||||| ||||")
            print(self.AI_Board_ref.fen())
            print(self.AI_Board_ref.is_checkmate())
            print("|||| |||| ||||| ||||")            

        print("<\n~~~~ ~~~~ ~~~~ ~~~~ ) \n\n")

        return [initial_row, initial_col, final_row, final_col, self.AI_Board_ref.is_checkmate(), self.AI_Board_ref.is_stalemate()]

    def Update(self, move):
        initial_row = 8 - move.initial.row
        initial_col = move.initial.col
        final_row = 8 - move.final.row
        final_col = move.final.col

        initial_col_char = chr(ord('`')+initial_col+1)
        final_col_char = chr(ord('`')+final_col+1)

        uci_move = initial_col_char + str(initial_row) + final_col_char + str(final_row)
        # print("AI Move Update : ", uci_move)

        Standard_move = chess.Move.from_uci(uci_move)
        # print(self.AI_Board_ref.san(Standard_move))

        self.AI_Board_ref.push(Standard_move)
        # print(self.AI_Board_ref)

        self.AI_Move_List.append(Standard_move)

    # def 