import pygame

from data.Constants import C

from data.Man import Man



class Pawn(Man):
	def __init__(self , position , colour , board):
		super().__init__(position , colour , board)
		self.creed = ""
		self.id    = self.colour + self.creed

		self.image_path = C.DIR_SETS + colour + "_pawn.png"
		self.image = pygame.image.load(self.image_path)
		self.image = pygame.transform.scale(self.image , (C.TILE_WIDTH-35 , C.TILE_HEIGHT-35))

		# Unique Pawn attribute
		self.just_moved_double = None


	def stencil_moves(self):
		stencil_moves = [
			[(0 , 1 if self.colour == "w" else -1)]
		]

		if not self.has_moved:
			stencil_moves[0].append(
				(0 , 2 if self.colour == "w" else -2)
			)

		return self.bound(self,stencil_moves)


	def moves(self , board):
		out = []

		# Stop at obstacles:
		for direction in self.stencil_moves():
			for target in direction:
				tile = board.tile_of(target)
				if tile.occupant is None:
					out.append(tile)
				else:
					break

		# Capture diagonally:
		if self.colour == "w":
			if (self.f+1 < 9) and (self.r+1 < 9):
				tile = board.tile_of(
					(self.f+1 , self.r+1)
				)
				if tile.occupant is not None:
					if tile.occupant.colour != self.colour:
						out.append(tile)
			if (self.f-1 > 0) and (self.r+1 < 9):
				tile = board.tile_of(
					(self.f-1 , self.r+1)
				)
				if tile.occupant is not None:
					if tile.occupant.colour != self.colour:
						out.append(tile)
		elif self.colour == "b":
			if (self.f+1 < 9) and (self.r-1 > 0):
				tile = board.tile_of(
					(self.f+1 , self.r-1)
				)
				if tile.occupant is not None:
					if tile.occupant.colour != self.colour:
						out.append(tile)
			if (self.f-1 > 0) and (self.r-1 > 0):
				tile = board.tile_of(
					(self.f-1 , self.r-1)
				)
				if tile.occupant is not None:
					if tile.occupant.colour != self.colour:
						out.append(tile)

		# En Passant:
		if self.r == (5 if self.colour == "w" else 4):
			for t in board.all_tiles:
				if type(t.occupant) is Pawn:
					if all([
						t.occupant.just_moved_double,
						t.occupant.colour != self.colour,
						abs(self.f - t.f) == 1,
						self.r == t.r
					]):
						out.append(board.tile_of(
							(t.f , t.r + (1 if self.colour == "w" else -1))
						))

		return out