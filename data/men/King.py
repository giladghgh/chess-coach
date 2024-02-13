import pygame

from data.Man import Man
from data.Constants import C



class King(Man):
	def __init__(self , position , colour , board):
		super().__init__(position , colour , board)
		self.creed = "K"
		self.id    = self.colour + self.creed

		self.image_path = C.DIR_SETS + colour + "_king.png"
		self.image = pygame.image.load(self.image_path)
		self.image = pygame.transform.scale(self.image , (C.TILE_WIDTH-20 , C.TILE_HEIGHT-20))


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

		return self.bound(self,moves)


	def can_castle(self , board):
		castles = []
		if not self.has_moved:
			backrank = 1 if self.colour == "w" else 8
			qside_rook = board.tile_of((1,backrank)).occupant
			kside_rook = board.tile_of((8,backrank)).occupant

			if qside_rook is not None:
				if not qside_rook.has_moved:
					qside_path = [board.tile_of((i,backrank)) for i in range(2,5)]
					if (
						# CLEAR
						not any([t.occupant for t in qside_path])
					) and (
						# SAFE
						not any([board.is_in_check(self.colour , movement=[self.position,t.position]) for t in qside_path])
					):
						castles.append("q")

			if kside_rook is not None:
				if not kside_rook.has_moved:
					kside_path = [board.tile_of((i,backrank)) for i in range(6,8)]
					if (
						# CLEAR
						not any([t.occupant for t in kside_path])
					) and (
						# SAFE
						not any([board.is_in_check(self.colour, movement=[self.position,t.position]) for t in kside_path])
					):
						castles.append("k")
		
		return castles


	def legal_moves(self, board):
		out = []
		for tile in self.moves(board):
			if not board.is_in_check(self.colour , movement=[self.position,tile.position]):
				out.append(tile)

		castles = self.can_castle(board) or ""
		if "q" in castles:
			out.append(board.tile_of(
				(self.f-2 , self.r)
			))
		if "k" in castles:
			out.append(board.tile_of(
				(self.f+2 , self.r)
			))

		return out
