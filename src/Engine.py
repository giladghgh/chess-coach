import operator

import chess,time,random

from src.Constants import C,E

from src.Gameplay import Move,Line





class Engine:
	def __init__(self , coach):
		self.coach = coach

		# Mechanics
		self.scheme = E.INIT_SCHEME
		self.model	= chess.Board(fen=C.INIT_FEN)

		### convenience
		chess.COLORS = (
			chess.WHITE,
			chess.BLACK
		)
		chess.PIECES = (
			chess.PAWN,
			chess.KNIGHT,
			chess.BISHOP,
			chess.ROOK,
			chess.QUEEN,
			chess.KING
		)

	def evaluate(self):
		value = 0

		for colour in chess.COLORS:
			score = 0
			for piece in chess.PIECES:
				creed = chess.piece_symbol(piece).upper()

				for square in self.model.pieces(piece,colour):
					if colour == chess.WHITE:
						f = chess.square_file(square)
						r = 7-chess.square_rank(square)
					else:
						f = 7-chess.square_file(square)
						r = chess.square_rank(square)

					mat = E.SCOREBOARD_MATERIAL[creed]
					pos = E.SCOREBOARD_POSITION[creed][r][f] / 100

					score += mat + pos

			if self.model.is_check() and self.model.turn == colour:
				score += 5

			### gain some perspective:
			value += score * (1,-1)[colour == self.model.turn]

		return round( value , 4 )


	def play(self):
		self.model.set_fen(self.coach.board.this_move.fen)

		# Theory
		uci = {
			"RANDOM" : self.play_random,
			"SIMPLE" : self.play_simple,
			"HAL90"  : self.play_random,
		}[self.scheme[self.coach.board.ply == "b"]]()

		# Praxis
		self.coach.force_move(
			self.UCI_to_move(uci)
		)


	def play_random(self):
		return random.choice( list(self.model.legal_moves) )


	def play_simple(self):
		movescores = {}
		for move in self.model.legal_moves:
			self.model.push(move)

			move.eval = self.evaluate()
			branch = self.search(self.depth-1,Line(move))
			movescores[move] = branch

			self.model.pop()


		###########################################
		# for step,line in movescores.items():
		# 	print(step,end="")
		# 	for branch in line:
		# 		print("\t\t",branch)
		###########################################


		best , main = max( movescores.items() , key=lambda m:m[1].eval )

		# print()
		# print("best:",type(best),best)
		# print("main:",type(main),main)

		return best


	def search(self , depth , history):
		if not depth:
			return history

		lines = Line()
		for move in self.model.legal_moves:
			self.model.push(move)

			move.eval = self.evaluate()
			lines.append(
				self.search(
					depth-1,
					history + [move]
				)
			)

			self.model.pop()

		return lines


	def UCI_to_move(self , uci):
		move = Move(
			self.coach.board,
			self.coach.board.this_move.fen
		)

		move.forced = True
		move.origin = self.coach.board.tile(
			1 + chess.square_file(uci.from_square),
			1 + chess.square_rank(uci.from_square)
		)
		move.target = self.coach.board.tile(
			1 + chess.square_file(uci.to_square),
			1 + chess.square_rank(uci.to_square)
		)

		return move


	@property
	def depth(self):
		return int((
			E.BOT_DEPTH_WHITE,
			E.BOT_DEPTH_BLACK
		)[self.coach.board.ply == "b"])
