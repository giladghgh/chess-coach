import pygame

from source.Man import Man
from source.Constants import C





class Knight(Man):
	def __init__(self , position , colour , board):
		super().__init__(position , colour , board)
		self.creed = "N"
		self.id    = self.colour + self.creed + self.pgn

		self.image_path = C.DIR_SETS + colour + "_knight.png"
		self.image = pygame.image.load(self.image_path)
		self.image = pygame.transform.scale(self.image , (C.TILE_WIDTH-20 , C.TILE_HEIGHT-20))


	def stencil_moves(self):
		moves = [
			[(1 , -2)],
			[(2 , -1)],
			[(2 , 1)],
			[(1 , 2)],
			[(-1 , 2)],
			[(-2 , 1)],
			[(-2 , -1)],
			[(-1 , -2)]
		]

		return self.bound(moves)