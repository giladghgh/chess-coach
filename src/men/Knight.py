import pygame

from src.Man import Man
from src.Constants import C





class Knight(Man):
	def __init__(self , *args):
		super().__init__(*args)
		self.creed = "N"
		self.id    = self.colour + self.creed + self.pgn

		self.image = pygame.transform.scale(
			pygame.image.load(C.DIR_SET + self.colour + "n.png"),
			self.image_size
		)

	def stencil_moves(self):
		moves = [
			[( 1 , -2)],
			[( 2 , -1)],
			[( 2 ,  1)],
			[( 1 ,  2)],
			[(-1 ,  2)],
			[(-2 ,  1)],
			[(-2 , -1)],
			[(-1 , -2)]
		]

		return self.confine(moves)