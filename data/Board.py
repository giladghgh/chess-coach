from datetime import datetime

from data.Constants import C
from data.Tile import Tile

from data.men.Pawn import Pawn
from data.men.Knight import Knight
from data.men.Bishop import Bishop
from data.men.Rook import Rook
from data.men.Queen import Queen
from data.men.King import King



class Board:
	def __init__(self, w , h):
		self.w = w
		self.h = h
		self.tile_width = w // 8
		self.tile_height = h // 8

		self.agent = None

		self.movenum = 0
		self.movetext = str()

		self.ply = 'w'
		self.model = C.INAUGURATION
		self.tiles = self.build_board()

		self.dress_board()


	def tile_of(self, *args):
		if len(args) == 1:
			f = args[0][0]
			r = args[0][1]
		elif len(args) == 2:
			f = args[0]
			r = args[1]
		else:
			raise Exception('Board.title_of() must be used with only 1 or 2 arguements!')

		f = int(f)
		r = int(r)
		return self.tiles[(8*r) + f]


	def build_board(self):
		out = []
		for r in range(8):
			for f in range(8):
				out.append(
					Tile(f , r , self.tile_width , self.tile_height)
				)

		return out


	def dress_board(self):
		for r,rank in enumerate(self.model):
			for f,man in enumerate(rank):
				if man != '  ':
					colour = man[0]
					creed = man[1]

					tile = self.tile_of(f , r)
					if creed == 'P':
						tile.occupant = Pawn((f,r) , colour , self)
					if creed == 'N':
						tile.occupant = Knight((f,r) , colour , self)
					if creed == 'B':
						tile.occupant = Bishop((f,r) , colour , self)
					if creed == 'R':
						tile.occupant = Rook((f,r) , colour , self)
					if creed == 'Q':
						tile.occupant = Queen((f,r) , colour , self)
					if creed == 'K':
						tile.occupant = King((f,r) , colour , self)


	def is_in_check(self , colour , movement=None):
		validity = False

		king_position = None
		origin_tile = None
		origin_man = None
		target_tile = None
		target_man = None

		if movement is not None:
			for tile in self.tiles:
				if tile.position == movement[0]:
					origin_tile = tile
					origin_man = tile.occupant
					origin_tile.occupant = None
			for tile in self.tiles:
				if tile.position == movement[1]:
					target_tile = tile
					target_man = target_tile.occupant
					target_tile.occupant = origin_man

		men = [t.occupant for t in self.tiles if t.occupant is not None]

		if origin_man is not None:
			if origin_man.creed == 'K':
				king_position = target_tile.position
		if king_position is None:
			for man in men:
				if (man.creed == 'K') and (man.colour == colour):
					king_position = man.position
		for man in men:
			if man.colour != colour:
				for tile in man.prey(self):
					if tile.position == king_position:
						validity = True
		if movement is not None:
			origin_tile.occupant = origin_man
			target_tile.occupant = target_man

		return validity


	def is_in_checkmate(self , colour):
		validity = False
		king = None
		for man in [t.occupant for t in self.tiles]:
			if man is not None:
				if (man.creed == 'K') and (man.colour == colour):
					king = man
		if all([
			king.valid_moves(self) == [],
			self.is_in_check(colour)
		]):
			validity = True

		return validity


	def handle_click(self , m_x , m_y):
		f = m_x // self.tile_width
		r = m_y // self.tile_height
		chosen_tile = self.tile_of(f,r)

		if self.agent is None:
			if chosen_tile.occupant is not None:
				if self.ply == chosen_tile.occupant.colour:
					self.agent = chosen_tile.occupant
		else:
			movement = self.agent.move(self, chosen_tile)
			if movement:
				if self.ply == 'w':
					self.movenum += 1
					self.movetext += str(self.movenum) + '. '
					self.ply = 'b'
				else:
					self.ply = 'w'

				self.movetext += movement + ' '
				print(self.movetext)
				print("----------------")
			elif chosen_tile.occupant is not None:
				if self.ply == chosen_tile.occupant.colour:
					self.agent = chosen_tile.occupant


	def draw(self , display):
		if self.agent is not None:
			self.tile_of(self.agent.position).highlight = True
			for tile in self.agent.valid_moves(self):
				tile.highlight = True
		for tile in self.tiles:
			tile.draw(display)


	@staticmethod
	def export():
		opening = "Test01"
		date = datetime.today().strftime('%Y-%m-%d')
		result = None