import time
import random

import chess
import chess.engine
from IPython.display import display, HTML, clear_output

class StockfishGame:
    """
    Game driver helper functions.
    """

    def display_board(self, board, use_svg):
        """
        Displays the chess board.
        :param board: a python-chess board.
        :param use_svg: boolean if visual html animation of board active.
        :return: str representation of html formatted board for display.
        """

        if use_svg:
            return board._repr_svg_()
        else:
            return "<pre>" + str(board) + "</pre>"

    def who(self, agent):
        """
        Checks if player agent is white or black.
        :param agent: a python-chess player.
        :return: str representation of agent's color.
        """

        return "White" if agent == chess.WHITE else "Black"

    def get_move(self, prompt):
        """
        Obtains available moves.
        :param prompt: keyboard interrupt prompt to halt active game.
        :return: str representation of Universal Chess Interface (UCI) move.
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
        Tallies the white and black players pieces.
        :param board: a python-chess board.
        :return: arr[int, int] representation of number of pieces on board where
                arr[0] is white and arr[1] is black.
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

    def test_engine_play(self,
                        agent1,
                        engine,
                        uci_start_state=None,
                        visual="svg",
                        pause=0.001):
        """
        Plays a single game with two agent players.

        :param agent1: agent function that takes board, return uci move.
        :param agent2: agent function that takes board, return uci move.
        :param uci_start_state: str representing an Universal Chess Interface (UCI) board state.
                example UCI: 'r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4'
               default is None.
               available options: None | '<properly formatted UCI>
        :param visual: indicates if visual html animation of board active.
               default is "svg".
               available options: "svg" | "simple" | None
        :param pause: time in between turns, can be used to speed up visual html
               animation.
               default is 0.001.
        :return: tuple (game_has_winner, msg, board)
        """

        use_svg = (visual == "svg")

        if uci_start_state is None:
            board = chess.Board()
        else:
            board = chess.Board(uci_start_state)


        try:
            while not board.is_game_over(claim_draw=True):

                if board.turn == chess.WHITE:
                    uci = agent1(board)

                else:
                    result = engine.play(board, chess.engine.Limit(time=0.1))
                    uci = result.move.uci()
                    # board.push(result.move)

                board.push_uci(uci)
                # analysis = engine.analysis(board)
                # turn = [result, analysis]
                #
                # out.append(turn)

                name = self.who(board.turn)


                # if board.turn == chess.WHITE:
                #     uci = agent1(board)
                # else:
                #     uci = agent2(board)
                # name = self.who(board.turn)


                board_stop = self.display_board(board, use_svg)
                # html = "<b>Move %s %s, Play '%s':</b><br/>%s" % (len(board.move_stack), name, uci, board_stop)
                html = "<b>Move %s %s, Play '%s':</b><br/>%s" % (len(board.move_stack), name, uci, board_stop)
                if visual is not None:
                    if visual == "svg":
                        clear_output(wait=True)
                    display(HTML(html))
                    if visual == "svg":
                        time.sleep(pause)
            engine.quit()
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

    # async def test_async_engine_play(self):
    #     transport, engine = await chess.engine.popen_uci("./stockfish")
    #     # chess.engine.SimpleEngine.popen_uci("./stockfish")
    #
    #     board = chess.Board()
    #     while not board.is_game_over():
    #         result = await engine.play(board, chess.engine.Limit(time=0.1))
    #         board.push(result.move)
    #
    #     await engine.quit()
    #
    # asyncio.set_event_loop_policy(chess.engine.EventLoopPolicy())
    # asyncio.run(main())

class RandomAgent:
    """
    Random Agent class.
    """

    def __init__(self, heuristic="naive"):
        """
        random agent constructor.
        :param heuristic:
            default is "naive"
            options: "naive" | "improved"
        """
        self.heuristic = heuristic
        base_name = "random_agent"

        if heuristic == "naive":
            self.name = base_name
            self.agent = self.naive_choice
        elif heuristic == "improved":
            self.name = heuristic + "_" + base_name
            self.agent = self.improved_choice

    def naive_choice(self, board):
        """
        randomly selects a legal move.
        :param board: a python-chess board.
        :return move: str representation of Universal Chess Interface (UCI) move.
        """
        move = random.choice(list(board.legal_moves))
        return move.uci()

    def improved_choice(self, board):
        """
        randomly selects a capture move if exists otherwise randomly selects a
        legal move.
        :param board: a python-chess board.
        :return move: str representation of Universal Chess Interface (UCI) move.
        """
        moves = list(board.legal_moves)
        captures = list()

        for m in moves:
            newboard = board.copy()
            if newboard.is_capture(m) is True:
                captures.append(m)

        if len(captures) is 0:
            move = random.choice(moves)
        else:
            move = random.choice(captures)
        return move.uci()
    # def play_game(self,
    #               agent1,
    #               agent2,
    #               uci_start_state=None,
    #               visual="svg",
    #               pause=0.001):
    #     """
    #     Plays a single game with two agent players.
    #
    #     :param agent1: agent function that takes board, return uci move.
    #     :param agent2: agent function that takes board, return uci move.
    #     :param uci_start_state: str representing an Universal Chess Interface (UCI) board state.
    #             example UCI: 'r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4'
    #            default is None.
    #            available options: None | '<properly formatted UCI>
    #     :param visual: indicates if visual html animation of board active.
    #            default is "svg".
    #            available options: "svg" | "simple" | None
    #     :param pause: time in between turns, can be used to speed up visual html
    #            animation.
    #            default is 0.001.
    #     :return: tuple (game_has_winner, msg, board)
    #     """
    #
    #     use_svg = (visual == "svg")
    #
    #     if uci_start_state is None:
    #         board = chess.Board()
    #     else:
    #         board = chess.Board(uci_start_state)
    #
    #     try:
    #         while not board.is_game_over(claim_draw=True):
    #             if board.turn == chess.WHITE:
    #                 uci = agent1(board)
    #             else:
    #                 uci = agent2(board)
    #             name = self.who(board.turn)
    #             board.push_uci(uci)
    #             board_stop = self.display_board(board, use_svg)
    #             html = "<b>Move %s %s, Play '%s':</b><br/>%s" % (
    #                 len(board.move_stack), name, uci, board_stop)
    #             if visual is not None:
    #                 if visual == "svg":
    #                     clear_output(wait=True)
    #                 display(HTML(html))
    #                 if visual == "svg":
    #                     time.sleep(pause)
    #     except KeyboardInterrupt:
    #         msg = "Game interrupted!"
    #         return (False, msg, board)
    #     game_has_winner = False
    #     if board.is_checkmate():
    #         msg = "checkmate: " + self.who(not board.turn) + " wins!"
    #         game_has_winner = not board.turn
    #     elif board.is_stalemate():
    #         msg = "draw: stalemate"
    #     elif board.is_fivefold_repetition():
    #         msg = "draw: 5-fold repetition"
    #     elif board.is_insufficient_material():
    #         msg = "draw: insufficient material"
    #     elif board.can_claim_draw():
    #         msg = "draw: claim"
    #     if visual is not None:
    #         print(msg)
    #
    #     return (game_has_winner, msg, board)

    # def run(self,
    #         agent1,
    #         agent2,
    #         iterations,
    #         uci_start_state=None,
    #         visual="svg",
    #         pause=0.001):
    #     """
    #     Driver allows for two agent players to play multiple games for a
    #     provided number of iterations.
    #
    #     :param agent1: agent function that takes board, return uci move.
    #     :param agent2: agent function that takes board, return uci move.
    #     :param iterations: int number of game iterations.
    #     :param uci_start_state: str representing an Universal Chess Interface (UCI) board state.
    #             example UCI: 'r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4'
    #            default is None.
    #            available options: None | '<properly formatted UCI>
    #     :param visual: indicates if visual html animation of board active.
    #            default is "svg".
    #            available options: "svg" | "simple" | None
    #     :param pause: time in between turns, can be used to speed up visual html
    #            animation.
    #            default is 0.001.
    #     :return: Returns a list of tuples representing scores.
    #     """
    #     agent1_name = agent1.name
    #     agent2_name = agent2.name
    #     scores_list = list()
    #
    #     depth = None
    #
    #     if "minimax" in agent1_name:
    #         depth = agent1.get_max_depth()
    #
    #     for round_num in range(iterations):
    #         terminal_state = self.play_game(agent1.agent,
    #                                         agent2.agent,
    #                                         uci_start_state,
    #                                         visual,
    #                                         pause)
    #
    #         game_hase_winner = terminal_state[0]
    #         msg = terminal_state[1]
    #         moves_played = len(terminal_state[2].move_stack)
    #         remaining_w_pieces = self.count_pieces(terminal_state[2])[0]
    #         remaining_b_pieces = self.count_pieces(terminal_state[2])[1]
    #
    #         result_list = (round_num + 1,
    #                        iterations,
    #                        depth,
    #                        agent1_name,
    #                        agent2_name,
    #                        game_hase_winner,
    #                        msg,
    #                        moves_played,
    #                        remaining_w_pieces,
    #                        remaining_b_pieces)
    #
    #         scores_list.append(result_list)
    #
    #     return scores_list