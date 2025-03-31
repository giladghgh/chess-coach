import operator

import chess,time,random
import pygame.display

from src.Constants import C,E

from src.Gameplay import Move,Line





class Engine:
	def __init__(self , coach):
		self.coach = coach

		self.stockfish = None

		# Mechanics
		self.schema = E.INIT_SCHEMA
		self.model	= chess.Board(fen=C.INIT_FEN)

		### for convenience
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


	def load_stockfish(self):
		from stockfish import Stockfish

		self.stockfish = Stockfish(
			path="data\\stockfish\\stockfish-windows-x86-64-avx2.exe",
			depth=15,
			parameters={
				"Minimum Thinking Time":0,
				"Min Split Depth":10,
			}
		)

		self.coach.analysis.counters["SCORE_STOCKFISH"].value = self.stockfish.get_evaluation()["value"]/100


	def unload_stockfish(self):
		self.stockfish = None


	def evaluate(self):
		value = 0

		for colour in chess.COLORS:
			score = 0
			for piece in chess.PIECES:
				creed = chess.piece_symbol(piece).upper()

				for square in self.model.pieces(piece,colour):
					if colour == chess.WHITE:
						f = chess.square_file(square)
						r = 7 - chess.square_rank(square)
					else:
						f = 7 - chess.square_file(square)
						r = chess.square_rank(square)

					mat = E.SCOREBOARD_MATERIAL[creed]
					pos = E.SCOREBOARD_POSITION[creed][r][f] / 100

					score += mat + pos

			if self.model.is_check() and self.model.turn == colour:
				score += 5

			### perspective
			value += score * (1,-1)[colour == self.model.turn]

		return round(value,4)


	def play(self):
		self.model.set_fen(self.coach.board.this_move.fen)

		# Calculate
		move = {
			"RANDOM"    : self.play_random,
			"HAL90"     : self.play_hal90,
			"STOCKFISH" : self.play_stockfish,
		}[self.schema[self.coach.board.ply == "b"]]()

		# Go
		self.coach.force_move(move)


	def play_random(self):
		best = random.choice( list(self.model.legal_moves) )

		return self.UCI_to_move(best)


	def play_stockfish(self):
		if not self.stockfish:
			self.load_stockfish()

		if self.stockfish:
			self.stockfish.set_fen_position(self.model.fen())
			best = self.stockfish.get_best_move()
		else:
			print("random!")
			best = random.choice( list(self.model.legal_moves) )

		return self.STR_to_move(best)


	def play_hal90(self):
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

		return self.UCI_to_move( best )


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


	def STR_to_move(self , string):
		move = Move(
			self.coach.board,
			self.coach.board.this_move.fen
		)

		move.forced = True
		move.origin = self.coach.board.tile( C.FILES.index(string[0]) , int(string[1]) )
		move.target = self.coach.board.tile( C.FILES.index(string[2]) , int(string[3]) )

		return move


	@property
	def depth(self):
		return int((
			E.BOT_DEPTH_WHITE,
			E.BOT_DEPTH_BLACK
		)[self.coach.board.ply == "b"])
