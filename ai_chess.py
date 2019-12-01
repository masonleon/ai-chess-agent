import time
import chess
from IPython.display import display, HTML, clear_output
import numpy as np
import pandas as pd
import timeit
import random


class Game:

    def display_board(self, board, use_svg):
        """
        Displays the chess board
        """
        if use_svg:
            return board._repr_svg_()
        else:
            return "<pre>" + str(board) + "</pre>"


    def who(self, agent):
        """
        Checks if player agent is white or black
        """
        return "White" if agent == chess.WHITE else "Black"


    def get_move(self, prompt):
        """
        Obtains available moves
        """
        uci = input(prompt)
        if uci and uci[0] == "q":
            raise KeyboardInterrupt()
        try:
            chess.Move.from_uci(uci)
        except:
            uci = None
        return uci


    def count_pieces(self, board):
        """
        Tallies the white and black players pieces
        """
        num_pieces = [0, 0]

        num_pieces[0] += len(board.pieces(chess.PAWN, chess.WHITE))
        num_pieces[0] += len(board.pieces(chess.BISHOP, chess.WHITE))
        num_pieces[0] += len(board.pieces(chess.KING, chess.WHITE))
        num_pieces[0] += len(board.pieces(chess.QUEEN, chess.WHITE))
        num_pieces[0] += len(board.pieces(chess.KNIGHT, chess.WHITE))
        num_pieces[0] += len(board.pieces(chess.ROOK, chess.WHITE))

        num_pieces[1] += len(board.pieces(chess.PAWN, chess.BLACK))
        num_pieces[1] += len(board.pieces(chess.BISHOP, chess.BLACK))
        num_pieces[1] += len(board.pieces(chess.KING, chess.BLACK))
        num_pieces[1] += len(board.pieces(chess.QUEEN, chess.BLACK))
        num_pieces[1] += len(board.pieces(chess.KNIGHT, chess.BLACK))
        num_pieces[1] += len(board.pieces(chess.ROOK, chess.BLACK))

        return num_pieces


    def play_game(self, agent1, agent2, start_state="", visual="svg", pause=0.1):
        """
        Plays a single game with two agent players
        """
        """
        agentN1, agent2: functions that takes board, return uci move
        visual: "simple" | "svg" | None
        """
        use_svg = (visual == "svg")

        if start_state is "":
            board = chess.Board()
        else:
            board = chess.Board(start_state)

        try:
            while not board.is_game_over(claim_draw=True):
                if board.turn == chess.WHITE:
                    uci = agent1(board)
                else:
                    uci = agent2(board)
                name = self.who(board.turn)
                board.push_uci(uci)
                board_stop = self.display_board(board, use_svg)
                html = "<b>Move %s %s, Play '%s':</b><br/>%s" % (
                    len(board.move_stack), name, uci, board_stop)
                if visual is not None:
                    if visual == "svg":
                        clear_output(wait=True)
                    display(HTML(html))
                    if visual == "svg":
                        time.sleep(pause)
        except KeyboardInterrupt:
            msg = "Game interrupted!"
            return (False, msg, board)
        game_has_winner = False
        if board.is_checkmate():
            msg = "checkmate: " + self.who(not board.turn) + " wins!"
            game_has_winner = not board.turn
        elif board.is_stalemate():
            msg = "draw: stalemate"
        elif board.is_fivefold_repetition():
            msg = "draw: 5-fold repetition"
        elif board.is_insufficient_material():
            msg = "draw: insufficient material"
        elif board.can_claim_draw():
            msg = "draw: claim"
        if visual is not None:
            print(msg)

        return (game_has_winner, msg, board)


    def run(self, agent1, agent2, iterations, agent1_name, agent2_name, start_state="", visual="svg", pause=0.001):
        """
        "Driver" allows for two agent players to play multiple games for a provided
        number of iterations. Returns a list of scores
        """
        scores_list = list()

        for round_num in range(iterations):
            terminal_state = self.play_game(agent1,
                                            agent2,
                                            start_state,
                                            visual,
                                            pause)

            game_hase_winner = terminal_state[0]
            msg = terminal_state[1]
            moves_played = len(terminal_state[2].move_stack)
            remaining_w_pieces = self.count_pieces(terminal_state[2])[0]
            remaining_b_pieces = self.count_pieces(terminal_state[2])[1]

            result_list = (round_num + 1,
                           iterations,
                           agent1_name,
                           agent2_name,
                           game_hase_winner,
                           msg,
                           moves_played,
                           remaining_w_pieces,
                           remaining_b_pieces)

            scores_list.append(result_list)

        return scores_list


class Agents:

    def random_agent(self, board):
        move = random.choice(list(board.legal_moves))
        return move.uci()

    def naive_agent(self, board, naive_eval):
        moves = list(board.legal_moves)
        for move in moves:
            newboard = board.copy()
            # go through board and return a score
            move.score = naive_eval(newboard, move, board.turn)
        moves.sort(key=lambda move: move.score, reverse=True)  # sort on score
        return moves[0].uci()

    def eval(self, board, move, my_color):
        score = 0
        ## Check some things about this move:
        # score += 10 if board.is_capture(move) else 0
        # To actually make the move:
        board.push(move)
        # Now check some other things:
        for (piece, value) in [(chess.PAWN, 1),
                               (chess.BISHOP, 4),
                               (chess.KING, 0),
                               (chess.QUEEN, 10),
                               (chess.KNIGHT, 5),
                               (chess.ROOK, 3)]:
            score += len(board.pieces(piece, my_color)) * value
            score -= len(board.pieces(piece, not my_color)) * value
            # can also check things about the pieces position here
        return score




# class RandomAgent:
#     """
#     Random Agent player
#     """
#     def run(self):
#
#         g = Game()
#
#         return g.run(random_agent, random_agent, 1, "r1", "r2", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w HAha - 0 1")


# class Eval:






# df = pd.DataFrame(data=res,
#                   columns=['round_num',
#                            'iterations',
#                            'agent1_name',
#                            'agent2_name',
#                            'game_has_winner',
#                            'winner',
#                            'moves_played',
#                            'remain_w_pieces',
#                            'remaining_b_pieces'])
#
# df.sort_values(by=['moves_played'], inplace=False,
#                                     ascending=True)

# df = pd.DataFrame(
#     columns=['round_num',
#              'iterations',
#              'agent1_name',
#              'agent2_name',
#              'game_has_winner',
#              'winner',
#              'moves_played',
#              'remain_w_pieces',
#              'remaining_b_pieces'])
#


