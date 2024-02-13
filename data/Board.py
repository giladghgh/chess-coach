import time
import pygame

from data.Constants import C
from data.Tile import Tile

from data.Man import Man
from data.men.Pawn import Pawn
from data.men.Knight import Knight
from data.men.Bishop import Bishop
from data.men.Rook import Rook
from data.men.Queen import Queen
from data.men.King import King



class Board:
	def __init__(self , coach):
		self.coach = coach

		self.display = self.coach.display
		self.coach.board = self

		self.w = C.BOARD_WIDTH
		self.h = C.BOARD_HEIGHT

		self.ply    = "w"
		self.agent  = None
		self.finish = None

		self.movetext = ''
		self.movenum  = 1
		self.opening  = None

		self.setup(model=C.INIT_CONFIG)


	def setup(self , model , settings=None):
		self.all_tiles = []
		self.flipped   = False

		for r,rank in enumerate(model):
			r = 8 - r
			for f,man in enumerate(rank):
				f = 1 + f
				self.all_tiles.append(
					Tile(self , f , r , C.TILE_WIDTH , C.TILE_HEIGHT)
				)

				if not man.isspace():
					colour = man[0]
					creed  = man[1]
					tile   = self.tile_of(f,r)

					if creed == "P":
						tile.occupant = Pawn((f,r) , colour , self)
					elif creed == "N":
						tile.occupant = Knight((f,r) , colour , self)
					elif creed == "B":
						tile.occupant = Bishop((f,r) , colour , self)
					elif creed == "R":
						tile.occupant = Rook((f,r) , colour , self)
					elif creed == "Q":
						tile.occupant = Queen((f,r) , colour , self)
					elif creed == "K":
						tile.occupant = King((f,r) , colour , self)


	def all_men(self , colour=None , creed=None):
		out = [tile.occupant for tile in self.all_tiles if tile.occupant is not None]
		if colour is not None:
			out = [man for man in out if man.colour == colour]
		if creed is not None:
			out = [man for man in out if man.creed  == creed]

		return out


	def tile_of(self, *args):
		if len(args) == 1:
			f = int(args[0][0])
			r = int(args[0][1])
		elif len(args) == 2:
			f = int(args[0])
			r = int(args[1])
		else:
			raise Exception("Board.tile_of() must be used with only 1 or 2 arguments!")

		for t in self.all_tiles:
			if t.position == (f,r):
				return t


	def attackers_of(self , tile , colour=None , creed=None):
		(f,r)  = tile if type(tile) is tuple else tile.position

		attackers = list()
		for man in self.all_men(colour,creed):
			for t in man.legal_moves(self):
				if t.position == (f,r):
					attackers.append(man)

		return attackers


	def render(self):
		if self.agent:
			self.tile_of(self.agent.position).highlight = True
			for tile in self.agent.legal_moves(self):
				tile.highlight = True

		for tile in self.all_tiles:
			tile.render()


	def animate(self , origin , target):
		dx = target.x - origin.x
		dy = target.y - origin.y
		speed = 5                  # frames per square (fps is determined by computing power)

		sprite = pygame.Surface.convert_alpha(self.agent.image)
		rect   = sprite.get_rect()
		rect.center = origin.rect.center
		ox,oy  = rect.x , rect.y

		self.agent = None

		total_frames = speed * round( (abs(target.f - origin.f)**2 + abs(target.r - origin.r)**2)**.5 )
		for frame in range(1 + total_frames):
			rect.x = ox + dx*(frame/total_frames)
			rect.y = oy - dy*(frame/total_frames)

			self.render()
			self.display.blit(sprite,rect)
			pygame.display.update()


	def handle_click(self , m_x=None , m_y=None , force=(None,None)):
		# force = (
		#     force_pos,
		#     force_promo
		# )

		if force[0]:
			chosen_tile = self.tile_of(force[0])
		else:
			if self.flipped:
				f = 8 - ((m_x - C.SIDEBAR_WIDTH) // C.TILE_WIDTH)
				r = 1 + (m_y // C.TILE_HEIGHT)
			else:
				f = 1 + ((m_x - C.SIDEBAR_WIDTH) // C.TILE_WIDTH)
				r = 8 - (m_y // C.TILE_HEIGHT)

			if all([
				1 <= f <= 8,
				1 <= r <= 8
			]):
				chosen_tile = self.tile_of(f,r)
			else:
				return

		# IF: you're selecting your own piece.
		if self.agent is None:
			if chosen_tile.occupant is not None:
				if chosen_tile.occupant.colour == self.ply:
					self.agent = chosen_tile.occupant
		# OR: you're selecting the piece's destination (usually).
		else:
			if self.agent.go(self , chosen_tile , force[1]):
				if self.ply == "w":
					self.movenum += 1
					self.ply = "b"
				else:
					self.ply = "w"
			elif chosen_tile.occupant is not None and chosen_tile.occupant.colour == self.ply and chosen_tile.occupant is not self.agent:
				self.agent = chosen_tile.occupant
			else:
				self.agent = None


	def is_in_check(self , colour , movement=None):
		in_check = False

		origin_tile = None
		target_tile = None
		origin_man = None
		target_man = None

		if movement:
			for tile in self.all_tiles:
				if tile.position == movement[0]:
					origin_tile = tile
					origin_man  = tile.occupant
					origin_tile.occupant = None
			for tile in self.all_tiles:
				if tile.position == movement[1]:
					target_tile = tile
					target_man  = tile.occupant
					target_tile.occupant = origin_man

		# Must loop through tiles, not Man.all, because with (movement) param I temporarily change tile attributes, not man attributes.
		for man in self.all_men(colour=("w" if colour == "b" else "b")):
			for tile in man.moves(self):
				if tile.occupant is not None and (
					tile.occupant.creed == "K"
					and
					tile.occupant.colour == colour
				):
					in_check = True
					break

		if movement:
			origin_tile.occupant = origin_man
			target_tile.occupant = target_man

		return in_check


	def is_in_checkmate(self , player=None):
		colour = player or self.ply

		# Can any of your men make a move that averts or relieves a check?
		for man in self.all_men(colour=colour):
			if man.legal_moves(self):
				return False

		# If not, the game is over, one way or another.
		if self.is_in_check(colour):
			self.finish = (
				"Black" if colour == "w" else "White",
				"Checkmate"
			)
		else:
			self.finish = (
				"Draw",
				"Stalemate"
			)

		return True


	def scribe(self , piece , origin , target , capture , attackers , special=None):
		move = str()

		if piece.colour == "w":
			move += str(self.movenum) + ". "

		# Castling
		if special == "Q":
			move += "O-O-O"
		elif special == "K":
			move += "O-O"
		else:
			# Mechanics
			### ambiguous movetext
			if len(attackers) > 1:
				print("Ambiguous scription!")

			### moves & captures
			move += piece.creed if not capture else piece.creed or C.FILES[origin.f]
			move += "x" if capture else ""
			move += C.FILES[target.f] + str(target.r)

			### promotions:
			if type(special) in (Queen,Rook,Knight,Bishop):
				move += "=" + special.creed

		# Checks:
		other_colour = "w" if piece.colour == "b" else "b"
		if (
			self.is_in_check(other_colour)
			and not
			self.is_in_checkmate(other_colour)
		):
			move += "+"
		elif self.is_in_checkmate(other_colour):
			move += "#"

		move += " "

		return move


	def appoint_promotion(self , tile , forced=None):
		if forced:
			# Reading movetext
			if forced == "Q":
				from data.men.Queen import Queen
				tile.occupant = Queen(
					tile.position,
					tile.occupant.colour,
					self
				)
			if forced == "R":
				from data.men.Rook import Rook
				tile.occupant = Rook(
					tile.position,
					tile.occupant.colour,
					self
				)
			if forced == "N":
				from data.men.Knight import Knight
				tile.occupant = Knight(
					tile.position,
					tile.occupant.colour,
					self
				)
			if forced == "B":
				from data.men.Bishop import Bishop
				tile.occupant = Bishop(
					tile.position,
					tile.occupant.colour,
					self
				)
			return

		# Gameplay
		import pygame

		screen_centre = [l / 2 for l in C.BOARD_SIZE]

		pause_veil = pygame.Surface(C.BOARD_SIZE)
		pause_veil.fill([125]*3)
		pause_veil.set_alpha(5)

		piece_images = [
			pygame.transform.scale(
				pygame.image.load(C.DIR_SETS + tile.occupant.colour + "_queen.png"),
				(C.TILE_WIDTH,C.TILE_HEIGHT)
			),
			pygame.transform.scale(
				pygame.image.load(C.DIR_SETS + tile.occupant.colour + "_rook.png"),
				(C.TILE_WIDTH,C.TILE_HEIGHT)
			),
			pygame.transform.scale(
				pygame.image.load(C.DIR_SETS + tile.occupant.colour + "_knight.png"),
				(C.TILE_WIDTH,C.TILE_HEIGHT)
			),
			pygame.transform.scale(
				pygame.image.load(C.DIR_SETS + tile.occupant.colour + "_bishop.png"),
				(C.TILE_WIDTH,C.TILE_HEIGHT)
			)
		]

		piece_rects = [
			piece_images[0].get_rect(bottomright=screen_centre),
			piece_images[1].get_rect(bottomleft=screen_centre),
			piece_images[2].get_rect(topright=screen_centre),
			piece_images[3].get_rect(topleft=screen_centre)
		]

		paused = True
		while paused:
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN and (
					event.key == pygame.K_SPACE
					or
					event.key == pygame.K_ESCAPE
				):
					paused = False
				elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
					cursor = (event.pos[0] - C.SIDEBAR_WIDTH , event.pos[1])
					if piece_rects[0].collidepoint(cursor):
						paused = False
						from data.men.Queen import Queen
						tile.occupant = Queen(
							tile.position,
							tile.occupant.colour,
							self
						)
					elif piece_rects[1].collidepoint(cursor):
						paused = False
						from data.men.Rook import Rook
						tile.occupant = Rook(
							tile.position,
							tile.occupant.colour,
							self
						)
					elif piece_rects[2].collidepoint(cursor):
						paused = False
						from data.men.Knight import Knight
						tile.occupant = Knight(
							tile.position,
							tile.occupant.colour,
							self
						)
					elif piece_rects[3].collidepoint(cursor):
						paused = False
						from data.men.Bishop import Bishop
						tile.occupant = Bishop(
							tile.position,
							tile.occupant.colour,
							self
						)

			self.display.blit(pause_veil , (C.SIDEBAR_WIDTH,0))
			for rect,img in zip(piece_rects,piece_images):
				pygame.draw.rect(
					pause_veil,
					(60,60,66),
					rect
				)
				pause_veil.blit(
					img,
					rect.topleft
				)

			pygame.display.update()
