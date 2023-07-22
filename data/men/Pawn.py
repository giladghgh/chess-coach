import pygame

from data.Man import Man



class Pawn(Man):
	def __init__(self , position , colour , board):
		super().__init__(position, colour, board)
		self.creed = 'P'
		self.id = self.colour + self.creed

		self.image_path = Man.image_dir + colour + '_pawn.png'
		self.image = pygame.image.load(self.image_path)
		self.image = pygame.transform.scale(self.image , (board.tile_width-35 , board.tile_height-35))


	def moves(self , board):
		out = []
		for tile in self.legal_moves(board):
			if tile.occupant is not None:
				break
			else:
				out.append(tile)

		if self.colour == 'w':
			if (self.f+1 < 8) and (self.r-1 >= 0):
				tile = board.tile_of(
					(self.f+1 , self.r-1)
				)
				if tile.occupant is not None:
					if tile.occupant.colour != self.colour:
						out.append(tile)
			if (self.f-1 >= 0) and (self.r-1 >= 0):
				tile = board.tile_of(
					(self.f-1 , self.r-1)
				)
				if tile.occupant is not None:
					if tile.occupant.colour != self.colour:
						out.append(tile)
		elif self.colour == 'b':
			if (self.f+1 < 8) and (self.r+1 < 8):
				tile = board.tile_of(
					(self.f+1 , self.r+1)
				)
				if tile.occupant is not None:
					if tile.occupant.colour != self.colour:
						out.append(tile)
			if (self.f-1 >= 0) and (self.r+1 < 8):
				tile = board.tile_of(
					(self.f-1 , self.r+1)
				)
				if tile.occupant is not None:
					if tile.occupant.colour != self.colour:
						out.append(tile)

		return out


	def prey(self , board):
		moves = self.moves(board)
		return [m for m in moves if m.f != self.f]

	def legal_moves(self, board):
		out = []

		moves = []
		if self.colour == 'w':
			moves.append((0, -1))
			if not self.has_moved:
				moves.append((0, -2))
		elif self.colour == 'b':
			moves.append((0, 1))
			if not self.has_moved:
				moves.append((0, 2))

		for m in moves:
			target_position = (self.f , self.r+m[1])
			if target_position[1] in range(7):
				out.append(board.tile_of(
					target_position
				))

		return out