from src.Constants import C





class Man:
	def __init__(self , board , colour , position):
		self.board    = board
		self.colour   = colour
		self.position = position
		self.f        = position[0]
		self.r        = position[1]

		self.creed = None
		self.id    = None
		self.pgn   = C.FILES[self.f] + str(self.r)

		self.has_taken = False
		self.has_moved = False


	def push(self , tile):
		self.position = tile.position
		self.f = tile.f
		self.r = tile.r

		self.pgn = C.FILES[self.f] + str(self.r)
		self.id = self.colour + self.creed + self.pgn


	def go(self , move , tile , special=None , show=True , tell=True):
		if special or (tile in self.legal_moves()):
			# Move mechanics
			move.agent = None
			move.agent , self.board.agent = self.board.agent , move.agent

			move.number = self.board.movenum
			move.colour = self.board.ply

			move.origin = self.board.tile_of(*self.position)
			move.target = tile

			move.capture = tile.occupant or False

			# Board Mechanics
			self.push(tile)

			self.has_moved = True
			self.has_taken = bool(tile.occupant)

			### pick up the pieces ...
			move.origin.occupant = None
			move.target.occupant = move.capture
			### ...

			# TODO: TURN THESE INTO METHODS IN THEIR RESPECTIVE CLASSES
			# Special Mechanics
			if not self.creed:
				### promotion
				move.promo = False
				if special or (
					self.colour == "w"
					and
					self.r == 8
				) or (
					self.colour == "b"
					and
					self.r == 1
				):
					move.promote(special)

				### en passant
				move.ep = False
				for man in self.board.all_men(
						colour=("w","b")[self.colour == "w"],
						creed=""
				):
					if all([
						abs(man.f - move.origin.f) == 1,
						man.r == move.origin.r,
						man.f == move.target.f,
						man.just_moved_double,
					]):
						move.ep = move.capture = man
						self.has_taken = True


			### castling
			if self.creed == "K":
				move.castle = False

				step = move.origin.f - move.target.f
				if step == 2:
					move.castle = "q"
				elif step == -2:
					move.castle = "k"

				if move.castle:
					from src.Gameplay import Move

					move.submove = Move(self.board)

					move.submove.forced = True
					move.submove.origin = self.board.tile_of(
						1 if move.castle == "q" else 8,
						self.r
					)
					move.submove.target = self.board.tile_of(
						4 if move.castle == "q" else 6,
						self.r
					)
					move.submove.agent = move.submove.origin.occupant

					move.submove.origin.occupant = None
					move.submove.target.occupant = move.submove.agent
					move.submove.agent.push(move.submove.target)

			if show:
				move.animate()

			### ...
			move.target.occupant = move.promo or move.agent
			if move.ep:
				self.board.tile_of(*move.ep.position).occupant = None
			### ... and put them down.

			# Reset board attributes
			for pawn in self.board.all_men(creed=""):
				pawn.just_moved_double = pawn is self

			# Other
			move.scribe()
			move.in_checkmate = self.board.is_in_checkmate("w" if move.colour == "b" else "b")
			move.in_check 	  = self.board.is_in_check("w" if move.colour == "b" else "b")

			# Movenoise
			if tell:
				move.vocalise()

			return True
		else:
			return False


	def pseudolegal_moves(self):
		moves = []
		for direction in self.stencil_moves():
			for f,r in direction:
				tile = self.board.tile_of(f,r)
				if tile.occupant:
					if tile.occupant.colour != self.colour:
						moves.append(tile)
					break
				else:
					moves.append(tile)

		return moves


	def legal_moves(self):
		moves = []
		for tile in self.pseudolegal_moves():
			if not self.board.is_in_check(self.colour , movement=[self.position,tile.position]):
				moves.append(tile)

		return moves


	def bound(self , moves):
		tiles = []
		for direction in moves:
			bdirection = []
			for move in direction:
				target_position = [sum(s) for s in zip(self.position,move)]
				if all([1 <= coord <= 8 for coord in target_position]):
					bdirection.append(target_position)
			tiles.append(bdirection)
		return tiles