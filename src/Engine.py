import chess
import time,random

from src.Constants import C,E

from src.Gameplay import Move,Line





class Engine:
	def __init__(self , coach):
		self.coach = coach

		self.player_scheme = E.INIT_SCHEME
		self.board = None


	def evaluate(self , method=None):
		if self.board.is_game_over() and self.board.outcome.termination in (
			chess.Termination.STALEMATE,
			chess.Termination.INSUFFICIENT_MATERIAL,
			chess.Termination.FIFTY_MOVES,
			chess.Termination.THREEFOLD_REPETITION
		):
			return 0

		score = 0
		if method is None:
			for f in range(8):
				for r in range(8):
					man = self.board.piece_at(chess.parse_square(C.FILES[f+1] + str(r+1)))

					if man is not None:
						mat = self.score_material(man.symbol(),f+1,r+1)
						pos = self.score_position(man.symbol(),f+1,r+1)
						score += mat + pos

		elif method.upper() == "STOCKFISH":
			pass

		return score


	# TODO: STOP SEARCHING AT CHECKMATE, FOR BLACK AND WHITE, !!! BEFORE FULL DEPTH IS REACHED !!!
	# Needs better escape logic
	def search(self , depth , method=None , history=None):
		if depth == 0:
			print("eval:",history,self.evaluate(method))
			return history , self.evaluate(method)

		line = history or Line(self.board)

		linescores = []
		searching  = True
		for i,move in enumerate(self.board.legal_moves):
			if searching:
				print()
				print(depth,move)

				line.append(move)
				self.board.push(move)
				if self.board.is_game_over() and self.board.outcome().termination is chess.Termination.CHECKMATE:
					movescore = line.copy() , float("inf") * (1 - 2*bool(self.board.turn))
					searching = False
				else:
					movescore = self.search(depth-1 , method , line.copy())

				self.board.pop()

				print(line)
				print(depth,i,move,line,movescore)

				linescores.append(movescore)

				print(linescores)

				line.pop()

		# Returns every legal move and its evaluation, in descending order by evaluation, as if white.
		#   i.e., a positive evaluation at any depth favours white and negative favours black. This is so that I don't have
		#   to keep switching between "max()" and "min()".
		print(linescores)
		return max(linescores , key=lambda l:l[1])


	def play(self , depth=3):
		self.board = chess.Board(fen=self.coach.export_FEN())

		print(self.search(depth))

		print("ENGINE DONE!")

		# scheme = self.player_scheme[self.coach.board.ply == "b"]
		# move   = {
		# 	"RANDOM"        : self.play_random(),
		# 	"MATERIALISTIC" : self.play_materialistic(),
		# 	"POSITIONAL"    : self.play_positional(),
		# 	"BASIC"         : self.play_basic(),
		# }[scheme]
		#
		# self.coach.force_move(move)


	def play_random(self):
		return


	def play_materialistic(self):
		return


	def play_positional(self):
		return


	def play_basic(self):
		# Translate for python-chess ...


		# ... Detranslate back for coach.
		move = Move(self.board)
		move.origin = None
		move.agent  = None
		move.target = None
		return move

