import time
import chess
from IPython.display import display, HTML, clear_output
import random


class Game:
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

    def play_game(self,
                  agent1,
                  agent2,
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

    def run(self,
            agent1,
            agent2,
            iterations,
            uci_start_state=None,
            visual="svg",
            pause=0.001):
        """
        Driver allows for two agent players to play multiple games for a
        provided number of iterations.

        :param agent1: agent function that takes board, return uci move.
        :param agent2: agent function that takes board, return uci move.
        :param iterations: int number of game iterations.
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
        :return: Returns a list of tuples representing scores.
        """
        agent1_name = agent1.name
        agent2_name = agent2.name
        scores_list = list()

        for round_num in range(iterations):
            terminal_state = self.play_game(agent1.agent,
                                            agent2.agent,
                                            uci_start_state,
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

class NaiveAgent:
    """
    Naive Agent class.
    """

    def __init__(self, heuristic="naive"):
        """
        naive agent constructor.
        :param heuristic:
            default is "naive"
            options: "naive" | "improved"
        """
        self.heuristic = heuristic
        base_name = "naive_agent"

        if heuristic == "naive":
            self.name = base_name
            self.eval = self.naive_evaluation
        elif heuristic == "improved":
            self.name = heuristic + "_" + base_name
            self.eval = self.improved_evaluation
        self.agent = self.choice

    def naive_evaluation(self, board, move, color):
        """
        naive evaluation method where score counter seed is set to 0.
        :param board: a python-chess board.
        :return move: str representation of Universal Chess Interface (UCI) move.
        :param color: boolean representing whether the color of the python-chess
                agent is this agent.
        :return: int score value.
        """
        # set seed to 0
        score = 0
        #score += 10 if board.is_capture(move) else 0
        # make the move:
        board.push(move)
        # Now check some other things:
        for (piece, value) in [(chess.PAWN, 1),
                               (chess.BISHOP, 4),
                               (chess.KING, 0),
                               (chess.QUEEN, 10),
                               (chess.KNIGHT, 5),
                               (chess.ROOK, 3)]:
            score += len(board.pieces(piece, color)) * value
            score -= len(board.pieces(piece, not color)) * value
            # can also check things about the pieces position here
        return score

    def improved_evaluation(self, board, move, color):
        """
        improved evaluation method where score counter seed is randomly set.
        :param board: a python-chess board.
        :return move: str representation of Universal Chess Interface (UCI) move.
        :param color: boolean representing whether the color of the python-chess
               agent is this agent.
        :return: int score value.
        """
        # set seed to random val
        score = random.random()
        score += 10 if board.is_capture(move) else 0
        # make the move:
        board.push(move)
        # Now check some other things:
        for (piece, value) in [(chess.PAWN, 1),
                               (chess.BISHOP, 4),
                               (chess.KING, 0),
                               (chess.QUEEN, 10),
                               (chess.KNIGHT, 5),
                               (chess.ROOK, 3)]:
            score += len(board.pieces(piece, color)) * value
            score -= len(board.pieces(piece, not color)) * value
            # can also check things about the pieces position here
        score += 100 if board.is_checkmate() else 0
        return score

    def choice(self, board):
        """
        choice selects the best move using the evaluation function.
        :param board: a python-chess board.
        :return: str representation of Universal Chess Interface (UCI) move.
        """
        moves = list(board.legal_moves)
        for move in moves:
            newboard = board.copy()
            # go through board and return a score
            move.score = self.eval(newboard, move, board.turn)
        moves.sort(key=lambda move: move.score, reverse=True)  # sort on score
        return moves[0].uci()

class MiniMaxAgent:
    """
    Mini-Max Agent class.
    """

    def __init__(self, max_depth=1, heuristic="naive"):
        """
        mini max agent constructor.
        :param max_depth: int maximum state search depth.
        :param heuristic:
           default is "naive"
           options: "naive" | "improved"
        """

        self._max_depth = max_depth
        self.heuristic = heuristic
        base_name = "minimax_agent"

        if heuristic == "naive":
            self.name = heuristic + "_" + base_name
            self.eval = self.naive_evaluation
        elif heuristic == "improved":
            self.name = heuristic + "_" + base_name
            self.eval = self.improved_evaluation
        self.agent = self.choice

    def get_max_depth(self):
        """
        gets assigned max depth.
        :return: int maximum state search depth.
        """
        return self._max_depth

    def maxValue(self, board, currentAgent, depth):
        """
        gets best move for maximizing agent.
        :param board: a python-chess board.
        :param currentAgent: boolean representing whether the color of the
            python-chess agent is the maximizing agent.
        :param depth: current depth in the search.
        :return: int score value.
        """
        bestMove = -9999

        moves = list(board.legal_moves)
        for move in moves:
            newboard = board.copy()
            newboard.push_uci(move.uci())
            result = self.miniMaxDecision(newboard, not currentAgent, depth - 1)
            if result > bestMove:
                bestMove = result
        return bestMove

    def minValue(self, board, currentAgent, depth):
        """
        gets best move for maximizing agent.
        :param board: a python-chess board.
        :param currentAgent: boolean representing whether the color of the
            python-chess agent is the minimizing agent.
        :param depth: current depth in the search.
        :return: int score value.
        """
        bestMove = 9999

        moves = list(board.legal_moves)
        for move in moves:
            newboard = board.copy()
            newboard.push_uci(move.uci())
            result = self.miniMaxDecision(newboard, not currentAgent, depth - 1)
            if result < bestMove:
                bestMove = result
        return bestMove

    def miniMaxDecision(self, board, currentAgent, depth):
        """
        recursively searches state tree to a certain depth for best move.
        :param board: a python-chess board.
        :param currentAgent: boolean representing whether the color of the
            python-chess agent is the current agent.
        :param depth: current depth in the search.
        :return: str representation of Universal Chess Interface (UCI) move.
        """
        if depth == 0:
            return self.eval(board)

        if currentAgent:
            return self.maxValue(board, not currentAgent, depth - 1)
        else:
            return self.minValue(board, not currentAgent, depth - 1)

    def naive_evaluation(self, board):
        """
        naive evaluation method where score counter seed is set to 0.
        :param board: a python-chess board.
        :return: int score value.
        """
        score = 0
        for (piece, value) in [(chess.PAWN, 1),
                               (chess.BISHOP, 4),
                               (chess.KING, 0),
                               (chess.QUEEN, 10),
                               (chess.KNIGHT, 5),
                               (chess.ROOK, 3)]:
            score += len(board.pieces(piece, True)) * value
            score -= len(board.pieces(piece, False)) * value
        return score

    def improved_evaluation(self, board):
        """
        improved evaluation method where score counter seed is randomly set.
        :param board: a python-chess board.
        :return: int score value.
        """
        score = random.random()
        # score += 10 if board.is_capture(move) else 0
        for (piece, value) in [(chess.PAWN, 1),
                               (chess.BISHOP, 4),
                               (chess.KING, 0),
                               (chess.QUEEN, 10),
                               (chess.KNIGHT, 5),
                               (chess.ROOK, 3)]:
            score += len(board.pieces(piece, True)) * value
            score -= len(board.pieces(piece, False)) * value
            # can also check things about the pieces position here
        return score

    def choice(self, board):
        """
        choice selects the best move using the evaluation function.
        :param board: a python-chess board.
        :return: str representation of Universal Chess Interface (UCI) move.
        """
        start_depth = self.get_max_depth()
        moves = list(board.legal_moves)
        for move in moves:
            newboard = board.copy()
            newboard.push_uci(move.uci())
            move.score = self.miniMaxDecision(newboard, False, start_depth)
        moves.sort(key=lambda move: move.score, reverse=True)  # sort on score
        return moves[0].uci()

##TODO alphabeta
    # def minimax_eval(board):
    #     # moves = list(board.legal_moves)
    #     # for move in moves:
    #     #     newboard = board.copy()
    #     #     # go through board and return a score
    #     #     move.score = staticAnalysis(newboard, move, board.turn)
    #     # moves.sort(key=lambda move: move.score, reverse=True) # sort on score
    #     # return moves[0].uci()
    #     score = random.random()
    #     for (piece, value) in [(chess.PAWN, 1),
    #                            (chess.BISHOP, 4),
    #                            (chess.KING, 0),
    #                            (chess.QUEEN, 10),
    #                            (chess.KNIGHT, 5),
    #                            (chess.ROOK, 3)]:
    #         score += len(board.pieces(piece, True)) * value
    #         score -= len(board.pieces(piece, False)) * value
    #         # can also check things about the pieces position here
    #     return score

##TODO alphabeta
    # def evaluateMoves(board):
    #     score = 0
    #     for (piece, value) in [(chess.PAWN, 1),
    #                            (chess.BISHOP, 4),
    #                            (chess.KING, 0),
    #                            (chess.QUEEN, 10),
    #                            (chess.KNIGHT, 5),
    #                            (chess.ROOK, 3)]:
    #         score += len(board.pieces(piece, True)) * value
    #         score -= len(board.pieces(piece, False)) * value
    #         # can also check things about the pieces position here
    #     score += 100 if board.is_checkmate() else 0
    #     return score

##TODO alphabeta
    # def maxValue(board, currentAgent, depth, alpha, beta):
    #     bestMove = -9999
    #
    #     moves = list(board.legal_moves)
    #     for move in moves:
    #         newboard = board.copy()
    #         newboard.push_uci(move.uci())
    #         bestMove = max(bestMove, miniMaxDecision(newboard, not currentAgent,
    #                                                  depth - 1, alpha, beta))
    #         if bestMove >= beta:
    #             return bestMove
    #         alpha = max(alpha, bestMove)
    #     return bestMove

##TODO alphabeta
    # def minValue(board, currentAgent, depth, alpha, beta):
    #     bestMove = 9999
    #     moves = list(board.legal_moves)
    #
    #     for move in moves:
    #         newboard = board.copy()
    #         newboard.push_uci(move.uci())
    #         bestMove = min(bestMove, miniMaxDecision(newboard, not currentAgent,
    #                                                  depth - 1, alpha, beta))
    #         if bestMove <= alpha:
    #             return bestMove
    #         beta = min(beta, bestMove)
    #     return bestMove

##TODO alphabeta
    # def miniMaxDecision(board, currentAgent, depth, alpha, beta):
    #     if depth == 0:
    #         return evaluateMoves(board)
    #
    #     if currentAgent:
    #         return maxValue(board, currentAgent, depth, alpha, beta)
    #     else:
    #         return minValue(board, currentAgent, depth, alpha, beta)

##TODO alphabeta
    # def mini_max_agent(board):
    #     moves = list(board.legal_moves)
    #     for move in moves:
    #         newboard = board.copy()
    #         newboard.push_uci(move.uci())
    #         move.score = miniMaxDecision(newboard, False , 3, -10000,10000)
    #     moves.sort(key=lambda move: move.score, reverse=True) # sort on score
    #     return moves[0].uci()

##TODO piecesquare table
# pawntable = [
#  0,  0,  0,  0,  0,  0,  0,  0,
# 50, 50, 50, 50, 50, 50, 50, 50,
# 10, 10, 20, 30, 30, 20, 10, 10,
#  5,  5, 10, 25, 25, 10,  5,  5,
#  0,  0,  0, 20, 20,  0,  0,  0,
#  5, -5,-10,  0,  0,-10, -5,  5,
#  5, 10, 10,-20,-20, 10, 10,  5,
#  0,  0,  0,  0,  0,  0,  0,  0]
#
# knightstable = [
# -50,-40,-30,-30,-30,-30,-40,-50,
# -40,-20,  0,  0,  0,  0,-20,-40,
# -30,  0, 10, 15, 15, 10,  0,-30,
# -30,  5, 15, 20, 20, 15,  5,-30,
# -30,  0, 15, 20, 20, 15,  0,-30,
# -30,  5, 10, 15, 15, 10,  5,-30,
# -40,-20,  0,  5,  5,  0,-20,-40,
# -50,-40,-30,-30,-30,-30,-40,-50]
#
# bishopstable = [
# -20,-10,-10,-10,-10,-10,-10,-20,
# -10,  0,  0,  0,  0,  0,  0,-10,
# -10,  0,  5, 10, 10,  5,  0,-10,
# -10,  5,  5, 10, 10,  5,  5,-10,
# -10,  0, 10, 10, 10, 10,  0,-10,
# -10, 10, 10, 10, 10, 10, 10,-10,
# -10,  5,  0,  0,  0,  0,  5,-10,
# -20,-10,-10,-10,-10,-10,-10,-20]
#
# rookstable = [
#   0,  0,  0,  0,  0,  0,  0,  0,
#   5, 10, 10, 10, 10, 10, 10,  5,
#  -5,  0,  0,  0,  0,  0,  0, -5,
#  -5,  0,  0,  0,  0,  0,  0, -5,
#  -5,  0,  0,  0,  0,  0,  0, -5,
#  -5,  0,  0,  0,  0,  0,  0, -5,
#  -5,  0,  0,  0,  0,  0,  0, -5,
#   0,  0,  0,  5,  5,  0,  0,  0]
#
# queenstable = [
# -20,-10,-10, -5, -5,-10,-10,-20,
# -10,  0,  0,  0,  0,  0,  0,-10,
# -10,  0,  5,  5,  5,  5,  0,-10,
#  -5,  0,  5,  5,  5,  5,  0, -5,
#   0,  0,  5,  5,  5,  5,  0, -5,
# -10,  5,  5,  5,  5,  5,  0,-10,
# -10,  0,  5,  0,  0,  0,  0,-10,
# -20,-10,-10, -5, -5,-10,-10,-20]
#
# kingstable = [
# -30,-40,-40,-50,-50,-40,-40,-30,
# -30,-40,-40,-50,-50,-40,-40,-30,
# -30,-40,-40,-50,-50,-40,-40,-30,
# -30,-40,-40,-50,-50,-40,-40,-30,
# -20,-30,-30,-40,-40,-30,-30,-20,
# -10,-20,-20,-20,-20,-20,-20,-10,
#  20, 20,  0,  0,  0,  0, 20, 20,
#  20, 30, 10,  0,  0, 10, 30, 20]




##TODO minimax with piece square
# def evaluateMoves(board):
#     if board.is_checkmate():
#         if board.turn:
#             return -9999
#         else:
#             return 9999
#     if board.is_stalemate():
#         return 0
#     if board.is_insufficient_material():
#         return 0
#
#     wp = len(board.pieces(chess.PAWN, chess.WHITE))
#     bp = len(board.pieces(chess.PAWN, chess.BLACK))
#     wn = len(board.pieces(chess.KNIGHT, chess.WHITE))
#     bn = len(board.pieces(chess.KNIGHT, chess.BLACK))
#     wb = len(board.pieces(chess.BISHOP, chess.WHITE))
#     bb = len(board.pieces(chess.BISHOP, chess.BLACK))
#     wr = len(board.pieces(chess.ROOK, chess.WHITE))
#     br = len(board.pieces(chess.ROOK, chess.BLACK))
#     wq = len(board.pieces(chess.QUEEN, chess.WHITE))
#     bq = len(board.pieces(chess.QUEEN, chess.BLACK))
#
#     material = 100 * (wp - bp) + 320 * (wn - bn) + 330 * (wb - bb) + 500 * (
#                 wr - br) + 900 * (wq - bq)
#
#     pawnsq = sum([pawntable[i] for i in board.pieces(chess.PAWN, chess.WHITE)])
#     pawnsq = pawnsq + sum([-pawntable[chess.square_mirror(i)]
#                            for i in board.pieces(chess.PAWN, chess.BLACK)])
#     knightsq = sum(
#         [knightstable[i] for i in board.pieces(chess.KNIGHT, chess.WHITE)])
#     knightsq = knightsq + sum([-knightstable[chess.square_mirror(i)]
#                                for i in
#                                board.pieces(chess.KNIGHT, chess.BLACK)])
#     bishopsq = sum(
#         [bishopstable[i] for i in board.pieces(chess.BISHOP, chess.WHITE)])
#     bishopsq = bishopsq + sum([-bishopstable[chess.square_mirror(i)]
#                                for i in
#                                board.pieces(chess.BISHOP, chess.BLACK)])
#     rooksq = sum([rookstable[i] for i in board.pieces(chess.ROOK, chess.WHITE)])
#     rooksq = rooksq + sum([-rookstable[chess.square_mirror(i)]
#                            for i in board.pieces(chess.ROOK, chess.BLACK)])
#     queensq = sum(
#         [queenstable[i] for i in board.pieces(chess.QUEEN, chess.WHITE)])
#     queensq = queensq + sum([-queenstable[chess.square_mirror(i)]
#                              for i in board.pieces(chess.QUEEN, chess.BLACK)])
#     kingsq = sum([kingstable[i] for i in board.pieces(chess.KING, chess.WHITE)])
#     kingsq = kingsq + sum([-kingstable[chess.square_mirror(i)]
#                            for i in board.pieces(chess.KING, chess.BLACK)])
#
#     eval = material + pawnsq + knightsq + bishopsq + rooksq + queensq + kingsq
#     return eval
#     # if board.turn:
#     #     return eval
#     # else:
#     #     return -eval

##TODO minimax with piece square
# def maxValue(board, currentAgent, depth,alpha,beta):
#     bestMove = -9999
#
#     moves = list(board.legal_moves)
#     for move in moves:
#         newboard = board.copy()
#         newboard.push_uci(move.uci())
#         bestMove = max(bestMove,miniMaxDecision(newboard, not currentAgent , depth -1,alpha,beta))
#         if bestMove >=beta :
#           return bestMove
#         alpha = max(alpha, bestMove)
#     return bestMove

##TODO minimax with piece square
# def minValue(board, currentAgent, depth,alpha,beta):
#     bestMove = 9999
#     moves = list(board.legal_moves)
#
#     for move in moves:
#         newboard = board.copy()
#         newboard.push_uci(move.uci())
#         bestMove = min(bestMove,miniMaxDecision(newboard, not currentAgent, depth -1,alpha,beta))
#         if bestMove <= alpha:
#           return bestMove
#         beta = min(beta, bestMove)
#     return bestMove

##TODO minimax with piece square
# def miniMaxDecision(board, currentAgent, depth,alpha,beta):
#     if depth == 0 :
#         return evaluateMoves(board)
#
#     if currentAgent:
#         return maxValue(board, currentAgent, depth, alpha, beta)
#     else:
#         return minValue(board, currentAgent, depth, alpha, beta)

##TODO minimax with piece square
# def mini_max_agent(board):
#     moves = list(board.legal_moves)
#     for move in moves:
#         newboard = board.copy()
#         newboard.push_uci(move.uci())
#         move.score = miniMaxDecision(newboard, False , 2, -10000,10000)
#     moves.sort(key=lambda move: move.score, reverse=True) # sort on score
#     return moves[0].uci()







##TODO minimax alpha beta pruning with piece square
# def evaluateMoves(board):
#     if board.is_checkmate():
#         if board.turn:
#             return -9999
#         else:
#             return 9999
#     if board.is_stalemate():
#         return 0
#     if board.is_insufficient_material():
#         return 0
#
#     wp = len(board.pieces(chess.PAWN, chess.WHITE))
#     bp = len(board.pieces(chess.PAWN, chess.BLACK))
#     wn = len(board.pieces(chess.KNIGHT, chess.WHITE))
#     bn = len(board.pieces(chess.KNIGHT, chess.BLACK))
#     wb = len(board.pieces(chess.BISHOP, chess.WHITE))
#     bb = len(board.pieces(chess.BISHOP, chess.BLACK))
#     wr = len(board.pieces(chess.ROOK, chess.WHITE))
#     br = len(board.pieces(chess.ROOK, chess.BLACK))
#     wq = len(board.pieces(chess.QUEEN, chess.WHITE))
#     bq = len(board.pieces(chess.QUEEN, chess.BLACK))
#
#     material = 100 * (wp - bp) + 320 * (wn - bn) + 330 * (wb - bb) + 500 * (
#                 wr - br) + 900 * (wq - bq)
#
#     pawnsq = sum([pawntable[i] for i in board.pieces(chess.PAWN, chess.WHITE)])
#     pawnsq = pawnsq + sum([-pawntable[chess.square_mirror(i)]
#                            for i in board.pieces(chess.PAWN, chess.BLACK)])
#     knightsq = sum(
#         [knightstable[i] for i in board.pieces(chess.KNIGHT, chess.WHITE)])
#     knightsq = knightsq + sum([-knightstable[chess.square_mirror(i)]
#                                for i in
#                                board.pieces(chess.KNIGHT, chess.BLACK)])
#     bishopsq = sum(
#         [bishopstable[i] for i in board.pieces(chess.BISHOP, chess.WHITE)])
#     bishopsq = bishopsq + sum([-bishopstable[chess.square_mirror(i)]
#                                for i in
#                                board.pieces(chess.BISHOP, chess.BLACK)])
#     rooksq = sum([rookstable[i] for i in board.pieces(chess.ROOK, chess.WHITE)])
#     rooksq = rooksq + sum([-rookstable[chess.square_mirror(i)]
#                            for i in board.pieces(chess.ROOK, chess.BLACK)])
#     queensq = sum(
#         [queenstable[i] for i in board.pieces(chess.QUEEN, chess.WHITE)])
#     queensq = queensq + sum([-queenstable[chess.square_mirror(i)]
#                              for i in board.pieces(chess.QUEEN, chess.BLACK)])
#     kingsq = sum([kingstable[i] for i in board.pieces(chess.KING, chess.WHITE)])
#     kingsq = kingsq + sum([-kingstable[chess.square_mirror(i)]
#                            for i in board.pieces(chess.KING, chess.BLACK)])
#
#     eval = material + pawnsq + knightsq + bishopsq + rooksq + queensq + kingsq
#     return eval
#     # if board.turn:
#     #     return eval
#     # else:
#     #     return -eval

##TODO minimax alpha beta pruning with piece square
# def maxValue(board, currentAgent, depth,alpha,beta):
#     bestMove = -9999
#
#     moves = list(board.legal_moves)
#     for move in moves:
#         newboard = board.copy()
#         newboard.push_uci(move.uci())
#         bestMove = max(bestMove,miniMaxDecision(newboard, not currentAgent , depth -1,alpha,beta))
#         if bestMove >=beta :
#           return bestMove
#         alpha = max(alpha, bestMove)
#     return bestMove

##TODO minimax alpha beta pruning with piece square
# def minValue(board, currentAgent, depth,alpha,beta):
#     bestMove = 9999
#     moves = list(board.legal_moves)
#
#     for move in moves:
#         newboard = board.copy()
#         newboard.push_uci(move.uci())
#         bestMove = min(bestMove,miniMaxDecision(newboard, not currentAgent, depth -1,alpha,beta))
#         if bestMove <= alpha:
#           return bestMove
#         beta = min(beta, bestMove)
#     return bestMove

##TODO minimax alpha beta pruning with piece square
# def miniMaxDecision(board, currentAgent, depth,alpha,beta):
#     if depth == 0 :
#         return evaluateMoves(board)
#
#     if currentAgent:
#         return maxValue(board, currentAgent, depth, alpha, beta)
#     else:
#         return minValue(board, currentAgent, depth, alpha, beta)

##TODO minimax alpha beta pruning with piece square
# def mini_max_agent(board):
#     moves = list(board.legal_moves)
#     for move in moves:
#         newboard = board.copy()
#         newboard.push_uci(move.uci())
#         move.score = miniMaxDecision(newboard, False , 2, -10000,10000)
#     moves.sort(key=lambda move: move.score, reverse=True) # sort on score
#     return moves[0].uci()
