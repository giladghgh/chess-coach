import pygame

from data.Man import Man
from data.Constants import C



class Bishop(Man):
	def __init__(self , position , colour , board):
		super().__init__(position , colour , board)
		self.creed = "B"
		self.id    = self.colour + self.creed

		self.image_path = C.DIR_SETS + colour + "_bishop.png"
		self.image = pygame.image.load(self.image_path)
		self.image = pygame.transform.scale(self.image , (C.TILE_WIDTH-20 , C.TILE_HEIGHT-20))


	def stencil_moves(self):
		moves_nw, moves_ne, moves_sw, moves_se = [], [], [], []
		for i in range(1, 9):
			moves_nw.append(
				(-i , i)
			)
			moves_ne.append(
				(i , i)
			)
			moves_sw.append(
				(-i , -i)
			)
			moves_se.append(
				(i , -i)
			)

		moves = [moves_nw] + [moves_ne] + [moves_sw] + [moves_se]

		return self.bound(self,moves)