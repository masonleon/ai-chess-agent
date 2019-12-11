import chess
import chess.pgn
import chess.engine
import sys
import json

# This engine test uses the configuration file engines.json and can easily be
# modified to use any UCI compatible chess engine.
#
# This engine test can be configured to use multiple PGN puzzle files.
# To work properly, the games of the pgn file consists of:
#	1. The setup position of the chess board in the form of an FEN structure.
#	2. One move entered by either black or white which is the puzzle solution move
#      based on the FEN position

def convert_piece_move(puzzle_move): 

	pos   = puzzle_move.find('-')
	part1 = puzzle_move[0:pos]
	part1 = part1[-2:]
	part2 = puzzle_move[pos+1:pos+3]

	return part1 + part2

def convert_capture_move(puzzle_move):

	pos   = puzzle_move.find('x')
	part1 = puzzle_move[0:pos]
	part1 = part1[-2:]
	part2 = puzzle_move[pos+1:pos+3]

	return part1 + part2

def puzzle_test(allpuzzles, engine, thinking_time):
	puzzle_sum = 0
	number_of_puzzles = 0

	print ("thinking_time = {0} seconds".format(thinking_time))
	file=open("misses.pgn", "w")
	
	for puzzle_batch in allpuzzles:
		puzzle_pgn = open(puzzle_batch["pgn_file"])
		print(puzzle_batch["pgn_file"])
		test_game = chess.pgn.read_game(puzzle_pgn)

		while test_game != None:
			round_str = test_game.headers["Round"]
			
			if (round_str[-1] >= "0") and (round_str[-1] <= "9"):
				number_of_puzzles += 1
			elif round_str[-1] == "a":
				number_of_puzzles += 1

			board = test_game.board()
			
			# get pgn move
			node = test_game
			next_node = node.variation(0)
	
			next_move = ""

			pattern = node.board().lan(next_node.move)
			pos = pattern.find('-')
			if pos > 0:
				next_move = convert_piece_move(pattern)
			else:
				pos = pattern.find('x')
				if pos > 0:
					next_move = convert_capture_move(pattern)
				else:
					next_move = pattern #example castling

			result = engine.play(board, chess.engine.Limit(time=thinking_time))

			next_move_str = "{0}".format(next_move)
			engine_move_str = "{0}".format(result.move)

			# promotiom piece ignpred
			if len(engine_move_str) == 5:
				if "rnbq".find(engine_move_str[4]):
					engine_move_str = engine_move_str[0:4] 

			if next_move_str == engine_move_str:
				puzzle_sum += 1
			else:
				print(test_game, file=open("misses.pgn", "a"), end ="\n\n")

			percentage = "{:.2%}".format(puzzle_sum / number_of_puzzles)

			if number_of_puzzles == 1:
				print("\n\n")
		 
			boardStr = "{0}".format(board.fen)
			pos1 = boardStr.find('(')+2
			pos2 = boardStr.find(')')-1
			boardStr = boardStr[pos1:pos2]

			print("FEN: {0}".format(boardStr))
			print("puzzle move :{0} engine move :{1} Score {2}/{3} = {4}\n".format(next_move_str, engine_move_str, puzzle_sum, number_of_puzzles, percentage))
	
			#next game		
			test_game = chess.pgn.read_game(puzzle_pgn)					
		# next puzzle file

if __name__ == '__main__':

	if len(sys.argv) > 1:
		thinking_time = int(sys.argv[1])
		print("thinking_time: {0} seconds".format(thinking_time))
	else:
		thinking_time = 60
		print("thinking_time: {0} seconds".format(thinking_time))

	with open('engines.json', 'r') as fp:
		data = json.load(fp)

	allengines = data["tester"][0]["chess_engines"]
	allpuzzles = data["test_files"]

	for testEngine in allengines:
		engine = chess.engine.SimpleEngine.popen_uci(testEngine["path"])
		
		print("\n\nTesting engine: {0} {1}\n".format(testEngine["engineName"], testEngine["version"]))
		puzzle_test(allpuzzles, engine, thinking_time)
		
		engine.quit()
