import pygame

from src.Man import Man
from src.Constants import C





class Queen(Man):
	def __init__(self , *args):
		super().__init__(*args)
		self.creed = "Q"
		self.id    = self.colour + self.creed + self.pgn

		self.image = pygame.transform.scale(
			pygame.image.load(C.DIR_SET + self.colour + "_queen.png"),
			self.image_size
		)

	def stencil_moves(self):
		moves_n,moves_e,moves_s,moves_w = [],[],[],[]
		moves_nw,moves_ne,moves_sw,moves_se = [],[],[],[]
		for i in range(1,9):
			# STRAIGHTS
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

			# DIAGONALS
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

		moves = [moves_n] + [moves_e] + [moves_s] + [moves_w] + [moves_nw] + [moves_ne] + [moves_sw] + [moves_se]

		return self.confine(moves)