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


	def send(self , tile):
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

			move.origin = self.board.tile(*self.position)
			move.target = tile

			move.capture = tile.occupant or False

			# Board Mechanics
			self.send(tile)

			self.has_moved = True
			self.has_taken = bool(tile.occupant)

			### pick up the pieces ...
			move.origin.occupant = None
			move.target.occupant = move.capture
			### ...

			# Special Mechanics
			### promotion
			if not self.creed:
				move.promo = False
				if special or (
						move.colour == "w"
						and
						move.target.r == 8
				) or (
						move.colour == "b"
						and
						move.target.r == 1
				):
					move.promote(special)

			### en passant
			if not self.creed:
				move.ep = False
				for pawn in self.board.all_men(
						colour=("w","b")[move.colour == "w"],
						creed=""
				):
					if all([
						abs(pawn.f - move.origin.f) == 1,
						pawn.r == move.origin.r,
						pawn.just_moved_double,
					]):
						move.ep = move.capture = pawn
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

					move.submove = Move(self.board,None)

					move.submove.forced = True
					move.submove.origin = self.board.tile(
						1 if move.castle == "q" else 8,
						self.r
					)
					move.submove.target = self.board.tile(
						4 if move.castle == "q" else 6,
						self.r
					)
					move.submove.agent = move.submove.origin.occupant

					move.submove.origin.occupant = None
					move.submove.target.occupant = move.submove.agent
					move.submove.agent.send(move.submove.target)

			if show:
				move.animate()

			### ...
			move.target.occupant = move.promo or move.agent
			if move.ep:
				self.board.tile(move.ep).occupant = None
			### ... and put them down.

			# Other
			### epability
			if self.creed == "" and abs(move.origin.r - move.target.r) == 2:
				for pawn in self.board.all_men(creed=""):
					pawn.just_moved_double = pawn is self

			### more info
			move.in_checkmate = self.board.is_in_checkmate("w" if move.colour == "b" else "b")
			move.in_check 	  = self.board.is_in_check("w" if move.colour == "b" else "b")
			move.note()

			### make yaself heard
			if tell:
				move.talk()

			return True
		else:
			return False


	def pseudolegal_moves(self):
		moves = []
		for direction in self.stencil_moves():
			for f,r in direction:
				tile = self.board.tile(f,r)
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


	def confine(self , moves):
		tiles = []
		for stencil_direction in moves:
			direction = []
			for stencil_move in stencil_direction:
				position = [sum(s) for s in zip(self.position,stencil_move)]
				if all([1 <= coord <= 8 for coord in position]):
					direction.append(position)
			tiles.append(direction)

		return tiles


	@property
	def image_size(self):
		squish = -40
		if self.creed:
			squish += 15
			if C.PIECE_STYLE.upper() in ("8-BIT","FONTAWESOME"):
				squish -= 10
		return [L + squish for L in C.TILE_SIZE]
