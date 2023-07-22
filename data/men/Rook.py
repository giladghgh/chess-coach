import pygame

from data.Man import Man



class Rook(Man):
	def __init__(self , position , colour , board):
		super().__init__(position, colour, board)
		self.creed = 'R'
		self.id = self.colour + self.creed

		self.image_path = Man.image_dir + colour + '_rook.png'
		self.image = pygame.image.load(self.image_path)
		self.image = pygame.transform.scale(self.image , (board.tile_width-20 , board.tile_height-20))


	def legal_moves(self , board):
		out = []

		moves_n = []
		for y in range(self.r)[::-1]:
			moves_n.append(board.tile_of(
				(self.f , y)
			))
		out.append(moves_n)

		moves_e = []
		for i in range(self.f+1 , 8):
			moves_e.append(board.tile_of(
				(i , self.r)
			))
		out.append(moves_e)

		moves_s = []
		for y in range(self.r+1 , 8):
			moves_s.append(board.tile_of(
				(self.f , y)
			))
		out.append(moves_s)

		moves_w = []
		for i in range(self.f)[::-1]:
			moves_w.append(board.tile_of(
				(i , self.r)
			))
		out.append(moves_w)

		return out