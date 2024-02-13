from data.Constants import C



class Man:
	all = []
	def __init__(self , position , colour , board):
		Man.all.append(self)
		self.position = position
		self.f        = position[0]
		self.r        = position[1]
		self.colour   = colour
		self.board    = board

		self.creed  = None
		self.id     = None

		self.has_taken  = False
		self.has_moved  = False
		self.just_moved_double = None


	def go(self , board , tile , forced=False):
		valid   = False
		special = None
		for t in board.all_tiles:
			t.highlight = False

		if forced or (tile in self.legal_moves(board)):
			# For disambiguation:
			attackers = board.attackers_of(tile , self.colour , self.creed)

			# Mechanics
			origin_tile   = board.tile_of(self.position)
			self.position = tile.position
			self.f = tile.f
			self.r = tile.r

			self.has_moved = True
			self.has_taken = bool(tile.occupant)

			origin_tile.occupant = None
			board.animate(origin_tile,tile)
			tile.occupant = self

			if not self.creed:
				# Promotion
				if self.r in (1,8):
					board.appoint_promotion(tile,forced)
					special = tile.occupant

				# En Passant
				for man in Man.all:
					if not man.creed:
						if all([
							man.just_moved_double,
							man.colour != self.colour,
							abs(man.f - origin_tile.f) == 1,
							man.r == origin_tile.r
						]):
							board.tile_of(man.position).occupant = None
							self.has_taken = True

			# Castling
			if self.creed == "K":
				if origin_tile.f - self.f == 2:
					# 0-0-0
					special = "Q"
					board.agent = board.tile_of((1,self.r)).occupant
					board.agent.go(board , board.tile_of(
						(4,self.r)
					) , forced=True)
				elif origin_tile.f - self.f == -2:
					# 0-0
					special = "K"
					board.agent = board.tile_of((8,self.r)).occupant
					board.agent.go(board , board.tile_of(
						(6,self.r)
					) , forced=True)

			# Reset just_moved attributes
			for man in Man.all:
				if not man.creed:
					if all([
						man is self,
						abs(origin_tile.r - tile.r) == 2
					]):
						man.just_moved_double = True
					else:
						man.just_moved_double = False

			valid = True
			if not forced or type(forced) is str:
				board.movetext += board.scribe(self , origin_tile , tile , self.has_taken , attackers , special)

		return valid


	def moves(self , board):
		out = []

		# Stop at obstacles:
		for direction in self.stencil_moves():
			for pos in direction:
				tile = board.tile_of(pos)
				if tile.occupant is not None:
					if tile.occupant.colour != self.colour:
						out.append(tile)
					break
				else:
					out.append(tile)
		return out


	def legal_moves(self , board):
		out = []
		for tile in self.moves(board):
			if not board.is_in_check(self.colour , movement=[self.position,tile.position]):
				out.append(tile)

		return out


	@staticmethod
	def bound(man , moves):
		out = []
		for direction in moves:
			bdirection = []
			for m in direction:
				target_position = (man.f+m[0] , man.r+m[1])
				if all((
						target_position[0] <= 8,
						target_position[0] >= 1,
						target_position[1] <= 8,
						target_position[1] >= 1
				)):
					bdirection.append(
						target_position
					)
			out.append(bdirection)
		return out

	@property
	def pgn(self):
		return C.FILES[self.f] + str(self.r)