import pygame

from data.Man import Man



class Bishop(Man):
	def __init__(self , position , colour , board):
		super().__init__(position, colour, board)
		self.creed = 'B'
		self.id = self.colour + self.creed

		self.image_path = Man.image_dir + colour + '_bishop.png'
		self.image = pygame.image.load(self.image_path)
		self.image = pygame.transform.scale(self.image , (board.tile_width-20 , board.tile_height-20))


	def legal_moves(self , board):
		out = []

		moves_nw = []
		for i in range(1,8):
			if (self.f-i < 0) or (self.r-i < 0):
				break
			moves_nw.append(board.tile_of(
				(self.f-i , self.r-i)
			))
		out.append(moves_nw)

		moves_ne = []
		for i in range(1,8):
			if (self.f+i > 7) or (self.r-i < 0):
				break
			moves_ne.append(board.tile_of(
				(self.f+i , self.r-i)
			))
		out.append(moves_ne)

		moves_se = []
		for i in range(1,8):
			if (self.f+i > 7) or (self.r+i > 7):
				break
			moves_se.append(board.tile_of(
				(self.f+i , self.r+i)
			))
		out.append(moves_se)

		moves_sw = []
		for i in range(1,8):
			if (self.f-i < 0) or (self.r+i > 7):
				break
			moves_sw.append(board.tile_of(
				(self.f-i , self.r+i)
			))
		out.append(moves_sw)

		return out