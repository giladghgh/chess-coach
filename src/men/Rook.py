import pygame

from src.Man import Man
from src.Constants import C





class Rook(Man):
	def __init__(self , *args):
		super().__init__(*args)
		self.creed = "R"
		self.id    = self.colour + self.creed + self.pgn

		self.image = pygame.transform.scale(
			pygame.image.load(C.DIR_SET + self.colour + "r.png"),
			self.image_size
		)

	def stencil_moves(self):
		moves_n,moves_e,moves_s,moves_w = [],[],[],[]
		for i in range(1,9):
			moves_n.append(
				(0 , i)
			)
			moves_e.append(
				(i , 0)
			)
			moves_s.append(
				(0 , -i)
			)
			moves_w.append(
				(-i , 0)
			)

		moves = [moves_n] + [moves_e] + [moves_s] + [moves_w]

		return self.confine(moves)