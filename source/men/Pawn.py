import pygame

from source.Constants import C

from source.Man import Man





class Pawn(Man):
	def __init__(self , position , colour , board):
		super().__init__(position , colour , board)
		self.creed = ""
		self.id    = self.colour + self.creed + self.pgn

		self.image_path = C.DIR_SETS + colour + "_pawn.png"
		self.image = pygame.image.load(self.image_path)
		self.image = pygame.transform.scale(self.image , (C.TILE_WIDTH-35 , C.TILE_HEIGHT-35))

		# Unique Pawn attribute
		self.just_moved_double = False


	def stencil_moves(self):
		stencil_moves = [
			[(0 , 1 if self.colour == "w" else -1)]
		]

		if (
			self.colour == "w"
			and
			self.r == 2
		) or (
			self.colour == "b"
			and
			self.r == 7
		) and not self.has_moved:
			stencil_moves[0].append(
				(0 , 2 if self.colour == "w" else -2)
			)

		return self.bound(stencil_moves)


	def pseudolegal_moves(self):
		out = []

		# Stop at obstacles:
		for direction in self.stencil_moves():
			for pos in direction:
				tile = self.board.tile_of(*pos)
				if not tile.occupant:
					out.append(tile)
				else:
					break

		# Diagonal captures
		if self.colour == "w":
			if (self.f+1 < 9) and (self.r+1 < 9):
				tile = self.board.tile_of(
					self.f+1,
					self.r+1
				)
				if tile.occupant:
					if tile.occupant.colour != self.colour:
						out.append(tile)
			if (self.f-1 > 0) and (self.r+1 < 9):
				tile = self.board.tile_of(
					self.f-1,
					self.r+1
				)
				if tile.occupant:
					if tile.occupant.colour != self.colour:
						out.append(tile)

		elif self.colour == "b":
			if (self.f+1 < 9) and (self.r-1 > 0):
				tile = self.board.tile_of(
					self.f+1,
					self.r-1
				)
				if tile.occupant:
					if tile.occupant.colour != self.colour:
						out.append(tile)
			if (self.f-1 > 0) and (self.r-1 > 0):
				tile = self.board.tile_of(
					self.f-1,
					self.r-1
				)
				if tile.occupant:
					if tile.occupant.colour != self.colour:
						out.append(tile)

		# En Passant
		if self.r == (5 if self.colour == "w" else 4):
			for t in self.board.all_tiles:
				if t.occupant and not t.occupant.creed:
					if all([
						t.occupant.just_moved_double,
						self.colour != t.occupant.colour,
						abs(self.f - t.f) == 1,
						self.r == t.r,
					]):
						ep_victim_pos = (t.f , t.r + (1 if self.colour == "w" else -1))

						### cannot e.p. into a check:
						cache = None
						t.occupant , cache = cache , t.occupant
						if not self.board.is_in_check(
							self.colour,
							movement=(
								self.position,
								ep_victim_pos
							)
						):
							out.append(self.board.tile_of(*ep_victim_pos))

						t.occupant , cache = cache , t.occupant

		return out