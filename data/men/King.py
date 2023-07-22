import pygame

from data.Man import Man



class King(Man):
	def __init__(self , position , colour , board):
		super().__init__(position, colour, board)
		self.creed = 'K'
		self.id = self.colour + self.creed

		self.image_path = Man.image_dir + colour + '_king.png'
		self.image = pygame.image.load(self.image_path)
		self.image = pygame.transform.scale(self.image , (board.tile_width-20 , board.tile_height-20))


	def legal_moves(self , board):
		out = []

		moves = [
			(0 , -1),
			(1 , -1),
			(1 , 0),
			(1 , 1),
			(0 , 1),
			(-1 , 1),
			(-1 , 0),
			(-1 , -1)
		]
		for m in moves:
			target_position = (self.f+m[0] , self.r+m[1])
			if all((
					target_position[0] < 8,
					target_position[0] >= 0,
					target_position[1] < 8,
					target_position[1] >= 0
			)):
				out.append([board.tile_of(
						target_position
				)])

		return out


	def can_castle(self , board):
		if not self.has_moved:
			if self.colour == 'w':
				qside_rook = board.tile_of((0,7)).occupant
				kside_rook = board.tile_of((7,7)).occupant

				if qside_rook is not None:
					if not qside_rook.has_moved:
						if [
							board.tile_of((i,7)).occupant for i in range(1,4)
						] == [None,None,None]:
							return 'qside'
				if kside_rook is not None:
					if not kside_rook.has_moved:
						if [
							board.tile_of((i,7)).occupant for i in range(5,7)
						] == [None,None]:
							return 'kside'
			elif self.colour == 'b':
				qside_rook = board.tile_of((0,0)).occupant
				kside_rook = board.tile_of((7,0)).occupant

				if qside_rook is not None:
					if not qside_rook.has_moved:
						if [
							board.tile_of((i,0)).occupant for i in range(1,4)
						] == [None,None,None]:
							return 'qside'
				if kside_rook is not None:
					if not kside_rook.has_moved:
						if [
							board.tile_of((i,0)) for i in range(5,7)
						] == [None,None]:
							return 'kside'


	def valid_moves(self, board):
		out = []
		for tile in self.moves(board):
			if not board.is_in_check(self.colour, movement=[self.position, tile.position]):
				out.append(tile)
		if self.can_castle(board) == 'qside':
			out.append(board.tile_of(
				(self.f-2 , self.r)
			))
		if self.can_castle(board) == 'kside':
			out.append([board.tile_of(
				(self.f+2 , self.r)
			)])

		return out
