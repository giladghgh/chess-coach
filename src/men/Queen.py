import pygame

from src.Man import Man
from src.Constants import C





class Queen(Man):
	def __init__(self , position , colour , board):
		super().__init__(position , colour , board)
		self.creed = "Q"
		self.id    = self.colour + self.creed + self.pgn

		self.image_path = C.DIR_SETS + colour + "_queen.png"
		self.image = pygame.image.load(self.image_path)
		self.image = pygame.transform.scale(self.image , (C.TILE_WIDTH-20 , C.TILE_HEIGHT-20))


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

		return self.bound(moves)