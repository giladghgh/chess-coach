import pygame

from src.Man import Man
from src.Constants import C





class King(Man):
	def __init__(self , *args):
		super().__init__(*args)
		self.creed = "K"
		self.id    = self.colour + self.creed + self.pgn

		self.image = pygame.transform.scale(
			pygame.image.load(C.DIR_SET + self.colour + "k.png"),
			self.image_size
		)

		self.toppled = False
		self.image_toppled = pygame.transform.scale(
			pygame.transform.rotate(pygame.image.load(C.DIR_SET + self.colour + "k.png"),90),
			self.image_size
		)

	def stencil_moves(self):
		moves = [
			[(0 , -1)],
			[(1 , -1)],
			[(1 , 0)],
			[(1 , 1)],
			[(0 , 1)],
			[(-1 , 1)],
			[(-1 , 0)],
			[(-1 , -1)]
		]

		return self.confine(moves)

	def can_castle(self , board):
		castles = ''
		if not self.has_moved and not self.board.has_check(self.colour):
			backrank = 1 if self.colour == "w" else 8

			# Kingside
			kside_rook = board.tile(8,backrank).occupant
			if kside_rook is not None and kside_rook.creed == "R":
				if not kside_rook.has_moved:
					kside_path = [board.tile(i,backrank) for i in range(6,8)]
					if (
						# CLEAR
						not any([t.occupant for t in kside_path])
					) and (
						# SAFE
						not any([board.has_check(self.colour , movement=[self.position,t.position]) for t in kside_path])
					):
						castles += "k"

			# Queenside
			qside_rook = board.tile(1,backrank).occupant
			if qside_rook is not None and qside_rook.creed == "R":
				if not qside_rook.has_moved:
					qside_path = [board.tile(i,backrank) for i in range(2,5)]
					if (
						# CLEAR
						not any([t.occupant for t in qside_path])
					) and (
						# SAFE
						not any([board.has_check(self.colour , movement=[self.position,t.position]) for t in qside_path])
					):
						castles += "q"

		return castles

	def legal_moves(self):
		out = []
		for tile in self.pseudolegal_moves():
			if not self.board.has_check(self.colour , movement=[self.position,tile.position]):
				out.append(tile)

		# Castling
		castles = self.can_castle(self.board)
		if "q" in castles:
			out.append(self.board.tile(
				self.f-2,
				self.r
			))
		if "k" in castles:
			out.append(self.board.tile(
				self.f+2,
				self.r
			))

		return out
