import pygame

from data.Man import Man



class Knight(Man):
	def __init__(self , position , colour , board):
		super().__init__(position, colour, board)
		self.creed = 'N'
		self.id = self.colour + self.creed

		self.image_path = Man.image_dir + colour + '_knight.png'
		self.image = pygame.image.load(self.image_path)
		self.image = pygame.transform.scale(self.image , (board.tile_width-20 , board.tile_height-20))


	def legal_moves(self , board):
		out = []

		moves = [
			(1 , -2),
			(2 , -1),
			(2 , 1),
			(1 , 2),
			(-1 , 2),
			(-2 , 1),
			(-2 , -1),
			(-1 , -2)
		]
		for m in moves:
			target_position = (self.f+m[0] , self.r+m[1])
			if all([
					target_position[0] < 8,
					target_position[0] >= 0,
					target_position[1] < 8,
					target_position[1] >= 0
			]):
				out.append([board.tile_of(
					target_position
				)])

		return out