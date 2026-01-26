import time,sys

from src.bots.HAL9 import *
from src.bots.Stockfish import *
from src.bots.Random import *





class Engine:
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

	def __init__(self , coach):
		self.coach = coach

		# Mechanics
		self.schema = E.INIT_SCHEMA

		self.model = chess.Board(fen=C.INIT_FEN)


	def play(self):
		bot = self.schema[self.coach.board.ply == "b"]

		bot.update()

		self.coach.force_move( bot.play() )


	def uci_to_move(self , uci):
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


	def txt_to_move(self , txt):
		move = Move(
			self.coach.board,
			self.coach.board.this_move.fen
		)

		move.forced = True
		move.origin = self.coach.board.tile( C.FILES.index(txt[0]) , int(txt[1]) )
		move.target = self.coach.board.tile( C.FILES.index(txt[2]) , int(txt[3]) )

		return move


	@property
	def fen(self):
		return self.coach.board.this_move.fen