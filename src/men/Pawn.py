import pygame

from src.Constants import C

from src.Man import Man





class Pawn(Man):
	def __init__(self , *args):
		super().__init__(*args)
		self.creed = ""
		self.id    = self.colour + self.creed + self.pgn

		self.image = pygame.transform.scale(
			pygame.image.load(C.DIR_SET + self.colour + "_pawn.png"),
			self.image_size
		)

		# Unique pawn attribute
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

		return self.confine(stencil_moves)


	def pseudolegal_moves(self):
		moves = []

		# Stop at obstacles:
		for direction in self.stencil_moves():
			for pos in direction:
				tile = self.board.tile(*pos)
				if not tile.occupant:
					moves.append(tile)
				else:
					break

		# Diagonal captures
		if self.colour == "w":
			if (self.f+1 < 9) and (self.r+1 < 9):
				tile = self.board.tile(
					self.f+1,
					self.r+1
				)
				if tile.occupant:
					if tile.occupant.colour != self.colour:
						moves.append(tile)
			if (self.f-1 > 0) and (self.r+1 < 9):
				tile = self.board.tile(
					self.f-1,
					self.r+1
				)
				if tile.occupant:
					if tile.occupant.colour != self.colour:
						moves.append(tile)

		elif self.colour == "b":
			if (self.f+1 < 9) and (self.r-1 > 0):
				tile = self.board.tile(
					self.f+1,
					self.r-1
				)
				if tile.occupant:
					if tile.occupant.colour != self.colour:
						moves.append(tile)
			if (self.f-1 > 0) and (self.r-1 > 0):
				tile = self.board.tile(
					self.f-1,
					self.r-1
				)
				if tile.occupant:
					if tile.occupant.colour != self.colour:
						moves.append(tile)

		# En Passant
		if self.r == (5 if self.colour == "w" else 4):
			for pawn in self.board.all_men(
					colour=("w","b")[self.colour == "w"],
					creed=""
			):
				if all([
					abs(pawn.f - self.f) == 1,
					pawn.r == self.r,
					pawn.just_moved_double,
				]):
					ep_victim_pos = (pawn.f , pawn.r + (1 if self.colour == "w" else -1))

					### cannot e.p. into a check:
					if not self.board.is_in_check(
							self.colour,
							movement=(
									self.position,
									ep_victim_pos
							)
					):
						moves.append(self.board.tile(*ep_victim_pos))

		return moves
