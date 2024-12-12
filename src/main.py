import pygame
import sys

from const import *
from game import Game
from square import Square
from move import Move

from chess_AI import Chess_AI

class Main:

    def __init__(self, ai_vs_ai = False, ai_player = "black", table="simple"):

        print(table)

        TABLE = table

        pygame.init()
        self.screen = pygame.display.set_mode( (WIDTH, HEIGHT) )
        pygame.display.set_caption('Chess')
        self.game = Game()

        self.AI_Player = ai_player
        self.AI_Bot = Chess_AI()
        self.AI_vs_AI = ai_vs_ai

        self.Move_lists = []

    def mainloop(self):
        
        screen = self.screen
        game = self.game
        board = self.game.board
        dragger = self.game.dragger

        while True:
            # show methods
            game.show_bg(screen)
            game.show_last_move(screen)
            game.show_moves(screen)
            game.show_pieces(screen)
            game.show_hover(screen)

            if self.AI_vs_AI:
                initial_row, initial_col, released_row, released_col, is_checkmate, is_stalemate = self.AI_Bot.AI_Move(board, DEPTH)

                initial = Square(initial_row, initial_col)
                final = Square(released_row, released_col)
                move = Move(initial, final)

                Moved_peice = board.squares[initial_row][initial_col].piece

                if Moved_peice.name == 'king':
                    board.calc_moves(Moved_peice, initial_row, initial_col)

                board.move(board.squares[initial_row][initial_col].piece, move)

                self.Move_lists.append(move)

                game.show_bg(screen)
                game.show_pieces(screen)

                if is_checkmate:
                    print(f"{Moved_peice.color} Won")
                    break

                if is_stalemate:
                    print(f"Statemate")
                    break

                game.next_turn()

            if dragger.dragging:
                dragger.update_blit(screen)

            for event in pygame.event.get():

                # key press
                if event.type == pygame.KEYDOWN:
                    
                    # changing themes
                    if event.key == pygame.K_t:
                        game.change_theme()

                     # changing themes
                    if event.key == pygame.K_r:
                        game.reset()
                        game = self.game
                        board = self.game.board
                        dragger = self.game.dragger

                # quit application
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()   


                elif game.next_player != self.AI_Player:
                # click
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        dragger.update_mouse(event.pos)

                        clicked_row = dragger.mouseY // SQSIZE
                        clicked_col = dragger.mouseX // SQSIZE

                        # if clicked square has a piece ?
                        if board.squares[clicked_row][clicked_col].has_piece():
                            piece = board.squares[clicked_row][clicked_col].piece
                            # valid piece (color) ?
                            if piece.color == game.next_player:
                                board.calc_moves(piece, clicked_row, clicked_col, bool=True)
                                dragger.save_initial(event.pos)
                                dragger.drag_piece(piece)
                                # show methods 
                                game.show_bg(screen)
                                game.show_last_move(screen)
                                game.show_moves(screen)
                                game.show_pieces(screen)
                    
                    # mouse motion
                    elif event.type == pygame.MOUSEMOTION:
                        motion_row = event.pos[1] // SQSIZE
                        motion_col = event.pos[0] // SQSIZE

                        game.set_hover(motion_row, motion_col)

                        if dragger.dragging:
                            dragger.update_mouse(event.pos)
                            # show methods
                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_moves(screen)
                            game.show_pieces(screen)
                            game.show_hover(screen)
                            dragger.update_blit(screen)
                    
                    # click release
                    elif event.type == pygame.MOUSEBUTTONUP:
                        
                        if dragger.dragging:
                            dragger.update_mouse(event.pos)

                            released_row = dragger.mouseY // SQSIZE
                            released_col = dragger.mouseX // SQSIZE

                            # create possible move
                            initial = Square(dragger.initial_row, dragger.initial_col)
                            final = Square(released_row, released_col)
                            move = Move(initial, final)

                            # valid move ?
                            if board.valid_move(dragger.piece, move):
                                # normal capture
                                captured = board.squares[released_row][released_col].has_piece()
                                board.move(dragger.piece, move)
                                self.AI_Bot.Update(move)

                                board.set_true_en_passant(dragger.piece)                            

                                # sounds
                                game.play_sound(captured)
                                # show methods
                                game.show_bg(screen)
                                game.show_last_move(screen)
                                game.show_pieces(screen)
                                # next turn
                                game.next_turn()
                        
                        dragger.undrag_piece()
            
                elif game.next_player == self.AI_Player:
                    initial_row, initial_col, released_row, released_col, is_checkmate, is_stalemate = self.AI_Bot.AI_Move(board, DEPTH)

                    initial = Square(initial_row, initial_col)
                    final = Square(released_row, released_col)
                    move = Move(initial, final)

                    Moved_peice = board.squares[initial_row][initial_col].piece

                    if Moved_peice.name == 'king':
                        board.calc_moves(Moved_peice, initial_row, initial_col)

                    board.move(board.squares[initial_row][initial_col].piece, move)

                    if is_checkmate:
                        print(f"{Moved_peice.color} (AI) Won")
                        break

                    if is_stalemate:
                        print(f"Statemate")
                        break

                    game.next_turn()

            pygame.display.update()

print(len(sys.argv))

if len(sys.argv) == 4:
    aI_vs_AI = False
    if sys.argv[1].lower() == "true":
        aI_vs_AI = True
    elif sys.argv[1].lower() == "false":
        aI_vs_AI = False
    else:
        print("Please provide correct 1st arguments")
        exit(1)

    if ((sys.argv[2] != "black") and (sys.argv[2] != "white")):
        print("Please provide correct 2nd arguments")
        exit(1)

    if ((sys.argv[3] != "simple") and (sys.argv[3] != "PeSTO")):
        print("Please provide correct 3rd arguments")
        exit(1)
    
    main = Main(ai_vs_ai=aI_vs_AI, ai_player=sys.argv[2], table=sys.argv[3])
    main.mainloop()


elif len(sys.argv) == 1:
    main = Main()
    main.mainloop()

else:
    print("Please provide correct arguments")
