import enum
import time
import chess
from IPython.display import display, HTML, clear_output
import random
import chess.engine
import requests


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
                  board_state=None,
                  visual="svg",
                  pause=0.001):
        """
        Plays a single game with two agent players.

        :param agent1: agent function that takes board, return uci move.
        :param agent2: agent function that takes board, return uci move.
        :param board_state: str representing the board state in FEN standard.
                example FEN: 'r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4'
               default is None.
               available options: None | '<properly formatted FEN>
        :param visual: indicates if visual html animation of board active.
               default is "svg".
               available options: "svg" | "simple" | None
        :param pause: time in between turns, can be used to speed up visual html
               animation.
               default is 0.001.
        :return: tuple (game_has_winner, msg, board)
        """

        use_svg = (visual == "svg")

        if board_state is None:
            board = chess.Board()
        else:
            board = chess.Board(board_state)

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
            board_state=None,
            visual="svg",
            pause=0.001):
        """
        Driver allows for two agent players to play multiple games for a
        provided number of iterations.

        :param agent1: agent function that takes board, return uci move.
        :param agent2: agent function that takes board, return uci move.
        :param iterations: int number of game iterations.
        :param board_state: str representing the board state in FEN standard.
                example FEN: 'r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4'
               default is None.
               available options: None | '<properly formatted FEN>
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

        depth = None

        if "minimax" in agent1_name:
            depth = agent1.get_max_depth()

        for round_num in range(iterations):
            terminal_state = self.play_game(agent1.agent,
                                            agent2.agent,
                                            board_state,
                                            visual,
                                            pause)

            game_hase_winner = terminal_state[0]
            msg = terminal_state[1]
            moves_played = len(terminal_state[2].move_stack)
            remaining_w_pieces = self.count_pieces(terminal_state[2])[0]
            remaining_b_pieces = self.count_pieces(terminal_state[2])[1]
            remaining_tot_pieces = remaining_w_pieces + remaining_b_pieces

            result_list = (round_num + 1,
                           iterations,
                           depth,
                           agent1_name,
                           agent2_name,
                           game_hase_winner,
                           msg,
                           moves_played,
                           remaining_w_pieces,
                           remaining_b_pieces,
                           remaining_tot_pieces)

            scores_list.append(result_list)

        return scores_list

    def play_game_engine(self,
                        agent1,
                        engine_agent,
                        uci_start_state=None,
                        visual="svg",
                        pause=0.001
                        ):
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

        # engine_result_data = list()

        try:
            while not board.is_game_over(claim_draw=True):

                if board.turn == chess.WHITE:

                    uci = agent1(board)

                else:

                    result = engine_agent.play(board, chess.engine.Limit(time=0.1))
                    uci = result.move.uci()
                    # engine_result_data.append(result)

                board.push_uci(uci)
                name = self.who(board.turn)
                board_stop = self.display_board(board, use_svg)
                html = "<b>Move %s %s, Play '%s':</b><br/>%s" % (len(board.move_stack), name, uci, board_stop)
                if visual is not None:
                    if visual == "svg":
                        clear_output(wait=True)
                    display(HTML(html))
                    if visual == "svg":
                        time.sleep(pause)
            engine_agent.quit()
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

        # if engine_agent:
        #     engine_agent.quit()
        return (game_has_winner, msg, board)

    def run_engine(self,
                    agent1,
                    engine_path,
                    iterations,
                    uci_start_state=None,
                    visual="svg",
                    pause=0.001
                    ):
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
        # print("game started at FEN: " + uci_start_state)
        agent1_name = agent1.name
        engine_name = "stockfish"
        # engine_name = "chess.engine.SimpleEngine.popen_uci(\"./stockfish\")"

        # engine_data_dict = dict()

        scores_list = list()

        depth = None

        if "minimax" in agent1_name:
            depth = agent1.get_max_depth()

        for round_num in range(iterations):
            # print("started round: " + str(round_num))

            engine_agent = chess.engine.SimpleEngine.popen_uci(engine_path)

            # print("created stockfish: " + str(engine_agent))


            terminal_state = self.play_game_engine(agent1.agent,
                                                    engine_agent,
                                                    uci_start_state,
                                                    visual,
                                                    pause
                                                    )

            game_hase_winner = terminal_state[0]
            msg = terminal_state[1]
            moves_played = len(terminal_state[2].move_stack)
            remaining_w_pieces = self.count_pieces(terminal_state[2])[0]
            remaining_b_pieces = self.count_pieces(terminal_state[2])[1]
            remaining_tot_pieces = remaining_w_pieces + remaining_b_pieces

            # print(terminal_state[2].halfmo)

            # key = "round:" + str(round_num + 1) + "_of:" + str(iterations) + "_depth:" + str(depth) + "_agent:" + agent1_name + "_engine:" + engine_name

            # engine_data_dict[key] = engine_data

            result_list = (round_num + 1,
                           iterations,
                           depth,
                           agent1_name,
                           engine_name,
                           game_hase_winner,
                           msg,
                           moves_played,
                           remaining_w_pieces,
                           remaining_b_pieces,
                           remaining_tot_pieces)

            scores_list.append(result_list)

        # return scores_list, engine_data_dict
        return scores_list

pawntable = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10, -20, -20, 10, 10, 5,
    5, -5, -10, 0, 0, -10, -5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, 5, 10, 25, 25, 10, 5, 5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
    0, 0, 0, 0, 0, 0, 0, 0]

knightstable = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50]

bishopstable = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 5, 0, 0, 0, 0, 5, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20]

rookstable = [
    0, 0, 0, 5, 5, 0, 0, 0,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    5, 10, 10, 10, 10, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0]

queenstable = [
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 5, 5, 5, 5, 5, 0, -10,
    0, 0, 5, 5, 5, 5, 0, -5,
    -5, 0, 5, 5, 5, 5, 0, -5,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20]

kingstable = [
    20, 30, 10, 0, 0, 10, 30, 20,
    20, 20, 0, 0, 0, 0, 20, 20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30]

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
            if board.is_capture(m):
                captures.append(m)

        if len(captures) is 0:
            move = random.choice(moves)
        else:
            move = random.choice(captures)
        return move.uci()

class BaseAgent:
    """
    Base Agent class.
    """

    def __init__(self, heuristic="naive"):
        """
        naive agent constructor.
        :param heuristic:
            default is "naive"
            options: "naive" | "improved"
        """
        self.heuristic = heuristic
        base_name = "_agent"

        if heuristic == "naive":
            self.name = heuristic + base_name
            self.eval = self.naive_evaluation
        elif heuristic == "improved":
            self.name = heuristic + base_name
            self.eval = self.improved_evaluation
        elif heuristic == "advanced":
            self.name = heuristic + base_name
            self.eval = self.advanced_evaluation
        self.agent = self.choice

    def count_pieces(self, board):
        """
        Tallies the white and black players pieces.
        :param board: a python-chess board.
        :return: arr[int, int] representation of number of pieces on board where
                arr[0] is white and arr[1] is black.
        """
        score = 0
        for piece in [chess.PAWN,
                               chess.BISHOP,
                               chess.KING,
                               chess.QUEEN,
                               chess.KNIGHT,
                               chess.ROOK]:
            score += len(board.pieces(piece, True))
            score += len(board.pieces(piece, False))

        return score

    def naive_evaluation(self, board, move, color):
        """
        naive evaluation method where score counter seed is set to 0.
        :param board: a python-chess board.
        :param move: str representation of Universal Chess Interface (UCI) move.
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
        for (piece, value) in [(chess.PAWN,   100),
                               (chess.BISHOP, 330),
                               (chess.KING,     0),
                               (chess.QUEEN,  900),
                               (chess.KNIGHT, 320),
                               (chess.ROOK,   500)]:
            score += len(board.pieces(piece, color)) * value
            score -= len(board.pieces(piece, not color)) * value
            # can also check things about the pieces position here
        return score

    def improved_evaluation(self, board, move, color):
        """
        improved evaluation method where score counter seed is randomly set.
        :param board: a python-chess board.
        :param move: str representation of Universal Chess Interface (UCI) move.
        :param color: boolean representing whether the color of the python-chess
               agent is this agent.
        :return: int score value.
        """
        # set seed to random val
        score = random.random()
        score += 50 if board.is_capture(move) else 0
        score -= 500 if board.is_into_check(move) else 0
        # make the move:
        board.push(move)
        if board.is_checkmate():
            return 9999
        if self.count_pieces(board) <=7:
            eval = 0
            query = "http://tablebase.lichess.ovh/standard?fen="
            fen = board.fen()
            request = query + fen.replace(" ", "_")
            r = requests.get(request)
            if r.status_code == 429:
                time.sleep(1)
                request = query + fen.replace(" ", "_")
                r = requests.get(request)
            wdl = r.json()["wdl"]
            if wdl is not None:
                # wdl < 0 if the side to move is losing. This move is preferable
                # since the opponent's side is losing
                if wdl < 0:
                    eval += 50
                if wdl >= 0:
                    eval -= 50
            return eval
        # Now check some other things:
        for (piece, value) in [(chess.PAWN,   100),
                               (chess.BISHOP, 330),
                               (chess.KING,     0),
                               (chess.QUEEN,  900),
                               (chess.KNIGHT, 320),
                               (chess.ROOK,   500)]:
            score += len(board.pieces(piece, color)) * value
            score -= len(board.pieces(piece, not color)) * value

        # check if the move puts other agent into check
        score += 900 if board.is_check() else 0
        return score

    def advanced_evaluation(self, board, move, color):
        """
        advanced evaluation method uses piece-square tables.
        :param board: a python-chess board.
        :param move: str representation of Universal Chess Interface (UCI) move.
        :param color: boolean representing whether the color of the python-chess
               agent is this agent.
        :return: int score value.
        """
        board.push(move)
        if board.is_checkmate():
            return 9999
        # low score if stalemate game
        if board.is_stalemate():
            return 0
        # low score if insufficient material to complete or win the game
        if board.is_insufficient_material():
            return 0
        if self.count_pieces(board) <= 7:
            eval = 0
            query = "http://tablebase.lichess.ovh/standard?fen="
            fen = board.fen()
            request = query + fen.replace(" ", "_")
            r = requests.get(request)
            if r.status_code == 429:
                time.sleep(1)
                request = query + fen.replace(" ", "_")
                r = requests.get(request)
            wdl = r.json()["wdl"]
            if wdl is not None:
                # wdl < 0 if the side to move is losing. This move is preferable
                # since the opponent's side is losing
                if wdl < 0:
                    eval += 50
                if wdl >= 0:
                    eval -= 50
            return eval

        wp = len(board.pieces(chess.PAWN,   chess.WHITE))
        bp = len(board.pieces(chess.PAWN,   chess.BLACK))
        wn = len(board.pieces(chess.KNIGHT, chess.WHITE))
        bn = len(board.pieces(chess.KNIGHT, chess.BLACK))
        wb = len(board.pieces(chess.BISHOP, chess.WHITE))
        bb = len(board.pieces(chess.BISHOP, chess.BLACK))
        wr = len(board.pieces(chess.ROOK,   chess.WHITE))
        br = len(board.pieces(chess.ROOK,   chess.BLACK))
        wq = len(board.pieces(chess.QUEEN,  chess.WHITE))
        bq = len(board.pieces(chess.QUEEN,  chess.BLACK))

        material = 100 * (wp - bp) + \
                   320 * (wn - bn) + \
                   330 * (wb - bb) + \
                   500 * (wr - br) + \
                   900 * (wq - bq)

        pawnsq = sum([pawntable[i] for i in board.pieces(chess.PAWN, chess.WHITE)])
        pawnsq = pawnsq + sum([-pawntable[chess.square_mirror(i)] for i in board.pieces(chess.PAWN, chess.BLACK)])

        knightsq = sum([knightstable[i] for i in board.pieces(chess.KNIGHT, chess.WHITE)])
        knightsq = knightsq + sum([-knightstable[chess.square_mirror(i)] for i in board.pieces(chess.KNIGHT, chess.BLACK)])

        bishopsq = sum([bishopstable[i] for i in board.pieces(chess.BISHOP, chess.WHITE)])
        bishopsq = bishopsq + sum([-bishopstable[chess.square_mirror(i)] for i in board.pieces(chess.BISHOP, chess.BLACK)])

        rooksq = sum([rookstable[i] for i in board.pieces(chess.ROOK, chess.WHITE)])
        rooksq = rooksq + sum([-rookstable[chess.square_mirror(i)] for i in board.pieces(chess.ROOK, chess.BLACK)])

        queensq = sum([queenstable[i] for i in board.pieces(chess.QUEEN, chess.WHITE)])
        queensq = queensq + sum([-queenstable[chess.square_mirror(i)] for i in board.pieces(chess.QUEEN, chess.BLACK)])

        kingsq = sum([kingstable[i] for i in board.pieces(chess.KING, chess.WHITE)])
        kingsq = kingsq + sum([-kingstable[chess.square_mirror(i)] for i in board.pieces(chess.KING, chess.BLACK)])

        eval = material + pawnsq + knightsq + bishopsq + rooksq + queensq + kingsq
        if board.turn:
            return -eval
        else:
            return eval

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

    def __init__(self, max_depth=1, heuristic="naive", type="minimax"):
        """
        mini max agent constructor.
        :param max_depth: int maximum state search depth.
        :param heuristic:
           default is "naive"
           options: "naive" | "improved"
        """
        self._max_depth = max_depth
        self.heuristic = heuristic
        self.type = type

        base_name = "_minimax_agent"

        if type == "minimax":
            self.name = base_name
            if heuristic == "naive":
                self.name = heuristic + self.name
                self.eval = self.naive_evaluation
            elif heuristic == "improved":
                self.name = heuristic + self.name
                self.eval = self.improved_evaluation
            elif heuristic == "advanced":
                self.name = heuristic + self.name
                self.eval = self.advanced_evaluation
            self.agent = self.minimax_choice

        elif type == "alpha-beta":
            self.name = type + base_name

            if heuristic == "naive":
                self.name = heuristic + "_" + self.name
                self.eval = self.naive_evaluation
            elif heuristic == "improved":
                self.name = heuristic + "_" + self.name
                self.eval = self.improved_evaluation
            elif heuristic == "advanced":
                self.name = heuristic + "_" + self.name
                self.eval = self.advanced_evaluation
            self.agent = self.alphabeta_choice

    def count_pieces(self, board):
        """
        Tallies the white and black players pieces.
        :param board: a python-chess board.
        :return: arr[int, int] representation of number of pieces on board where
                arr[0] is white and arr[1] is black.
        """
        score = 0
        for piece in [chess.PAWN,
                               chess.BISHOP,
                               chess.KING,
                               chess.QUEEN,
                               chess.KNIGHT,
                               chess.ROOK]:
            score += len(board.pieces(piece, True))
            score += len(board.pieces(piece, False))

        return score

    def naive_evaluation(self, board):
        """
        naive evaluation method where score counter seed is set to 0.
        :param board: a python-chess board.
        :return: int score value.
        """
        score = 0
        if self.count_pieces(board) <= 7:
            eval = 0
            query = "http://tablebase.lichess.ovh/standard?fen="
            fen = board.fen()
            request = query + fen.replace(" ", "_")
            r = requests.get(request)
            if r.status_code == 429:
                time.sleep(1)
                request = query + fen.replace(" ", "_")
                r = requests.get(request)
            wdl = r.json()["wdl"]
            if wdl is not None:
                # wdl < 0 if the side to move is losing. This move is preferable
                # since the opponent's side is losing
                if wdl < 0:
                    eval += 50
                if wdl >= 0:
                    eval -= 50
            return eval

        for (piece, value) in [(chess.PAWN, 100),
                               (chess.BISHOP, 330),
                               (chess.KING, 0),
                               (chess.QUEEN, 900),
                               (chess.KNIGHT, 320),
                               (chess.ROOK, 500)]:
            score += len(board.pieces(piece, True)) * value
            score -= len(board.pieces(piece, False)) * value
        return score

    def improved_evaluation(self, board):
        """
        improved evaluation method where score counter seed is randomly set.
        :param board: a python-chess board.
        :return: int score value.
        """
        if board.is_checkmate():
            if board.turn:
                # very low score if agent is checkmated by opponent
                return -9999
            else:
                # very high score if move is a checkmate
                return 9999
        if self.count_pieces(board) <=7:
            eval = 0
            query = "http://tablebase.lichess.ovh/standard?fen="
            fen = board.fen()
            request = query + fen.replace(" ", "_")
            r = requests.get(request)
            if r.status_code == 429:
                time.sleep(1)
                request = query + fen.replace(" ", "_")
                r = requests.get(request)
            wdl = r.json()["wdl"]
            if wdl is not None:
                # wdl < 0 if the side to move is losing. This move is preferable
                # since the opponent's side is losing
                if wdl < 0:
                    eval += 50
                if wdl >= 0:
                    eval -= 50
            return eval
        score = random.random()
        # TODO
        # score += 50 if board.is_capture() else 0
        for (piece, value) in [(chess.PAWN, 100),
                               (chess.BISHOP, 330),
                               (chess.KING, 0),
                               (chess.QUEEN, 900),
                               (chess.KNIGHT, 320),
                               (chess.ROOK, 500)]:
            score += len(board.pieces(piece, True)) * value
            score -= len(board.pieces(piece, False)) * value

        # check if the move puts other agent into check
        if board.is_check():
            if board.turn:
                score -= 900
            else:
                score += 900
        return score

    def advanced_evaluation(self, board):
        """
        advanced evaluation method uses piece-square tables.
        :param board: a python-chess board.
        :return move: str representation of Universal Chess Interface (UCI) move.
        :param color: boolean representing whether the color of the python-chess
               agent is this agent.
        :return: int score value.
        """
        if board.is_checkmate():
            if board.turn:
                # very low score if agent is checkmated by opponent
                return -9999
            else:
                # very high score if move is a checkmate
                return 9999
        # low score if stalemate game
        if board.is_stalemate():
            return 0
        # low score if insufficient material to complete or win the game
        if board.is_insufficient_material():
            return 0
        # When the number of pieces on the board is less than 7, the agent probes the syzygy
        # endgame table base to get the wdl(win/draw/loss) details. This heavily reduces the
        # computation overload on the agent
        if self.count_pieces(board) <=7:
            # print("piece count: ",self.count_pieces(board))
            eval =0
            query = "http://tablebase.lichess.ovh/standard?fen="
            fen = board.fen()
            print("White thinking about FEN: " + str(fen))
            request = query + fen.replace(" ", "_")
            r = requests.get(request)
            if r.status_code == 429:
                time.sleep(1)
                request = query + fen.replace(" ", "_")
                r = requests.get(request)
            wdl = r.json()["wdl"]
            print("response received")
            if wdl is not None:
                if wdl < 0:
                    eval += 50
                if wdl >= 0:
                    eval -= 50
            return eval

        wp = len(board.pieces(chess.PAWN,   chess.WHITE))
        bp = len(board.pieces(chess.PAWN,   chess.BLACK))
        wn = len(board.pieces(chess.KNIGHT, chess.WHITE))
        bn = len(board.pieces(chess.KNIGHT, chess.BLACK))
        wb = len(board.pieces(chess.BISHOP, chess.WHITE))
        bb = len(board.pieces(chess.BISHOP, chess.BLACK))
        wr = len(board.pieces(chess.ROOK,   chess.WHITE))
        br = len(board.pieces(chess.ROOK,   chess.BLACK))
        wq = len(board.pieces(chess.QUEEN,  chess.WHITE))
        bq = len(board.pieces(chess.QUEEN,  chess.BLACK))

        material = 100 * (wp - bp) + \
                   320 * (wn - bn) + \
                   330 * (wb - bb) + \
                   500 * (wr - br) + \
                   900 * (wq - bq)

        pawnsq = sum([pawntable[i] for i in board.pieces(chess.PAWN, chess.WHITE)])
        pawnsq = pawnsq + sum([-pawntable[chess.square_mirror(i)] for i in board.pieces(chess.PAWN, chess.BLACK)])

        knightsq = sum([knightstable[i] for i in board.pieces(chess.KNIGHT, chess.WHITE)])
        knightsq = knightsq + sum([-knightstable[chess.square_mirror(i)] for i in board.pieces(chess.KNIGHT, chess.BLACK)])

        bishopsq = sum([bishopstable[i] for i in board.pieces(chess.BISHOP, chess.WHITE)])
        bishopsq = bishopsq + sum([-bishopstable[chess.square_mirror(i)] for i in board.pieces(chess.BISHOP, chess.BLACK)])

        rooksq = sum([rookstable[i] for i in board.pieces(chess.ROOK, chess.WHITE)])
        rooksq = rooksq + sum([-rookstable[chess.square_mirror(i)] for i in board.pieces(chess.ROOK, chess.BLACK)])

        queensq = sum([queenstable[i] for i in board.pieces(chess.QUEEN, chess.WHITE)])
        queensq = queensq + sum([-queenstable[chess.square_mirror(i)] for i in board.pieces(chess.QUEEN, chess.BLACK)])

        kingsq = sum([kingstable[i] for i in board.pieces(chess.KING, chess.WHITE)])
        kingsq = kingsq + sum([-kingstable[chess.square_mirror(i)] for i in board.pieces(chess.KING, chess.BLACK)])

        eval = material + pawnsq + knightsq + bishopsq + rooksq + queensq + kingsq
        return eval

    def get_max_depth(self):
        """
        gets assigned max depth.
        :return: int maximum state search depth.
        """
        return self._max_depth

    def minimax_max_value(self, board, currentAgent, depth):
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
            result = self.minimax_decision(newboard, not currentAgent, depth - 1)
            if result > bestMove:
                bestMove = result
        return bestMove

    def minimax_min_value(self, board, currentAgent, depth):
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
            result = self.minimax_decision(newboard, not currentAgent, depth - 1)
            if result < bestMove:
                bestMove = result
        return bestMove

    def minimax_decision(self, board, currentAgent, depth):
        """
        recursively searches state tree to a certain depth for best move.
        :param board: a python-chess board.
        :param currentAgent: boolean representing whether the color of the
            python-chess agent is the current agent.
        :param depth: current depth in the search.
        :return: str representation of Universal Chess Interface (UCI) move.
        """
        if depth == 0:
            print("made a move")
            return self.eval(board)

        if currentAgent:
            return self.minimax_max_value(board, currentAgent, depth)
        else:
            return self.minimax_min_value(board, currentAgent, depth)

    def minimax_choice(self, board):
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
            move.score = self.minimax_decision(newboard, False, start_depth)
        moves.sort(key=lambda move: move.score, reverse=True)  # sort on score
        return moves[0].uci()

    def alphabeta_max_value(self, board, currentAgent, depth, alpha, beta):
        """
        gets best move for minimizing alphabeta agent.
        :param board: a python-chess board.
        :param currentAgent: boolean representing whether the color of the
            python-chess agent is the minimizing agent.
        :param depth: current depth in the search.
        :return: int best score value.
        """
        bestMove = -9999

        moves = list(board.legal_moves)
        for m in moves:
            newboard = board.copy()
            newboard.push_uci(m.uci())

            alpha = self.alpha
            beta = self.beta

            bestMove = max(bestMove, self.alphabeta_decision(newboard, not currentAgent, depth - 1, alpha, beta))
            if bestMove >= beta:
                return bestMove
            self.alpha = max(alpha, bestMove)
        return bestMove

    def alphabeta_min_value(self, board, currentAgent, depth, alpha, beta):
        """
        gets best move for maximizing alphabeta agent.
        :param board: a python-chess board.
        :param currentAgent: boolean representing whether the color of the
            python-chess agent is the minimizing agent.
        :param depth: current depth in the search.
        :return: int best score value.
        """
        bestMove = 9999

        moves = list(board.legal_moves)
        for m in moves:
            newboard = board.copy()
            newboard.push_uci(m.uci())

            alpha = self.alpha
            beta = self.beta

            bestMove = min(bestMove, self.alphabeta_decision(newboard, not currentAgent, depth - 1, alpha, beta))
            if bestMove <= alpha:
                return bestMove
            self.beta = min(self.beta, bestMove)
        return bestMove

    def alphabeta_decision(self, board, currentAgent, depth, alpha, beta):
        """
        recursively searches minimax state tree to a certain depth for best move
        eliminating unnecessary costly explorations by using alpha-beta pruning.
        :param board: a python-chess board.
        :param currentAgent: boolean representing whether the color of the
            python-chess agent is the current agent.
        :param depth: current depth in the search.
        :param alpha: int representing the minimum alpha value.
        :param beta: int representing the maximum beta value.
        :return: str representation of Universal Chess Interface (UCI) move.
        """
        if depth == 0:
            return self.eval(board)

        if currentAgent:
            return self.alphabeta_max_value(board, currentAgent, depth, alpha, beta)
        else:
            return self.alphabeta_min_value(board, currentAgent, depth, alpha, beta)

    def alphabeta_choice(self, board):
        start_depth = self.get_max_depth()
        moves = list(board.legal_moves)
        for move in moves:
            self.alpha = -10000
            self.beta = 10000
            newboard = board.copy()
            newboard.push_uci(move.uci())
            move.score = self.alphabeta_decision(newboard, False, start_depth, self.alpha, self.beta)
        moves.sort(key=lambda move: move.score, reverse=True) # sort on score
        return moves[0].uci()



# def main():
#     # game rounds per match-up
#     NUM_ITERATIONS = 1
#     # result stats per game for pandas dataframee
#     COLUMNS = ['round_num', 'iterations', 'depth', 'white agent', 'black agent', 'white_victory', 'winner',
#                'moves_played', 'remain_w_pieces', 'remaining_b_pieces', 'remaining_tot_pieces']
#     # turn off svg animation to improve performance
#     GRAPHICS = None
#     # stockfish engine executable path
#     STOCKFISH_PATH = "./../stockfish_engine/test/stockfish"
#
#     game = Game()
#
#     white = MiniMaxAgent(max_depth=1, heuristic="advanced", type="alpha-beta")
#     black = STOCKFISH_PATH
#
#     results, dict = game.run_engine(white, black, NUM_ITERATIONS, visual=None)
#
#     print(results)
#
#     print(dict)
#
# if __name__ == "__main__":
#     main()