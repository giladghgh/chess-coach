import pygame

from src.Man import Man
from src.Constants import C





class Bishop(Man):
	def __init__(self , *args):
		super().__init__(*args)
		self.creed = "B"
		self.id    = self.colour + self.creed + self.pgn

		self.image_path = C.DIR_SET + self.colour + "_bishop.png"
		self.image = pygame.image.load(self.image_path)
		self.image = pygame.transform.scale(self.image , self.image_size)


	def stencil_moves(self):
		moves_nw,moves_ne,moves_sw,moves_se = [],[],[],[]
		for i in range(1,9):
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

		return self.confine(moves)