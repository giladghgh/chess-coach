import time
import pygame

from source.Constants import C
from source.Tile import Tile

from source.men.Pawn import Pawn
from source.men.Knight import Knight
from source.men.Bishop import Bishop
from source.men.Rook import Rook
from source.men.Queen import Queen
from source.men.King import King





class Board:
	def __init__(self , coach):
		self.coach = coach

		# Interface
		self.w = C.BOARD_WIDTH
		self.h = C.BOARD_HEIGHT

		self.show_coords = False
		self.show_legals = True

		# Mechanics
		self.ply   = "w"
		self.agent = None

		# self.movetext    = ''
		self.movenum     = 1
		self.halfmovenum = 1

		self.this_move = Move(self,fen=C.INIT_FEN)
		self.last_move = None
		self.movelog   = [self.this_move,]

		# Gameplay
		self.opening = None
		self.outcome = (None,None)

		# Stats
		self.rulecount_fiftymoves = 0
		self.rulecount_threereps  = 1

		# Audio
		self.sound_move_quiet   = pygame.mixer.Sound(C.DIR_SOUNDS + "/move_quiet.wav")
		self.sound_move_check   = pygame.mixer.Sound(C.DIR_SOUNDS + "/move_check.wav")
		self.sound_move_capture = pygame.mixer.Sound(C.DIR_SOUNDS + "/move_capture.wav")


	def compose(self , model):
		self.all_tiles = []
		for r,rank in enumerate(model):
			r = 8 - r
			for f,man in enumerate(rank):
				f = 1 + f

				self.all_tiles.append(
					Tile(self , f , r , *C.TILE_SIZE)
				)

				if not man.isspace():
					colour = man[0]
					creed  = man[1]
					tile   = self.tile_of(f,r)

					if creed == "P":
						tile.occupant = Pawn(  self , colour , (f,r))
					elif creed == "N":
						tile.occupant = Knight(self , colour , (f,r))
					elif creed == "B":
						tile.occupant = Bishop(self , colour , (f,r))
					elif creed == "R":
						tile.occupant = Rook(  self , colour , (f,r))
					elif creed == "Q":
						tile.occupant = Queen( self , colour , (f,r))
					elif creed == "K":
						tile.occupant = King(  self , colour , (f,r))


	def tile_of(self , file , rank):
		for t in self.all_tiles:
			if t.position == (file,rank):
				return t


	def all_men(self , colour=None , creed=None):
		men = [tile.occupant for tile in self.all_tiles if tile.occupant]

		if colour is not None:
			if type(colour) is not tuple:
				colour = (str(colour),)
			men = [man for man in men if man.colour in colour]
		if creed is not None:
			if type(creed) is not tuple:
				creed = (str(creed),)
			men = [man for man in men if man.creed in creed]

		return men


	def attackers_of(self , tile , colour=None , creed=None):
		attackers = []
		for man in self.all_men(colour,creed):
			for tgt in man.legal_moves():
				if tgt.position == tile.position:
					attackers.append(man)

		return attackers


	def render(self):
		# Fresh tiles
		if self.agent:
			self.tile_of(*self.agent.position).is_fresh = True
		if self.last_move:
			if self.last_move.origin:
				self.tile_of(*self.last_move.origin.position).is_fresh = True
			if self.last_move.target:
				self.tile_of(*self.last_move.target.position).is_fresh = True

		# Spotlit tiles
		for tile in self.this_move.lights:
			self.tile_of(*tile.position).is_focus = True

		# Legal move dots
		if self.show_legals and self.agent:
			for tile in self.agent.legal_moves():
				self.tile_of(*tile.position).is_legal = True

		# Render then reset decor
		for tile in self.all_tiles:
			self.tile_of(*tile.position).render()
			self.tile_of(*tile.position).is_fresh = False
			self.tile_of(*tile.position).is_focus = False
			self.tile_of(*tile.position).is_legal = False


	def handle_click(self , file , rank , promo=None , show=True):
		chosen_tile = self.tile_of(file,rank)

		# Initiate move:
		if self.agent is None:
			# Empty tile
			if not chosen_tile.occupant:
				self.this_move.rinse()

			# Select agent:
			elif chosen_tile.occupant.colour == self.ply:
				self.agent 			  = chosen_tile.occupant

				self.this_move.clean()
				self.this_move.origin = chosen_tile

		# Progress move:
		else:
			# Complete move:
			if self.agent.go(self.this_move , chosen_tile , promo , show):
				### mechanics
				self.turnover()

				### movetext
				self.coach.reader.update(self.movelog)

				### stats
				self.refresh_stats()

			# Switch agent:
			elif chosen_tile.occupant and chosen_tile.occupant.colour == self.ply:
				if chosen_tile.occupant is self.agent:
					self.agent 			  = None
					self.this_move.origin = None
				else:
					self.agent 			  = chosen_tile.occupant
					self.this_move.origin = chosen_tile

			# Deselect agent:
			else:
				self.agent 			  = None
				self.this_move.origin = None
				self.this_move.rinse()


	def turnover(self):
		# Mechanics
		if self.ply == "w":
			self.ply = "b"
		else:
			self.ply = "w"
			self.movenum += 1
		self.halfmovenum += 1

		# Movelog
		### unrestricted time control
		del self.movelog[self.halfmovenum - 2:]

		### handover
		self.last_move = self.this_move
		self.this_move = Move(self,fen=self.coach.export_FEN())

		### log
		self.movelog.append(self.last_move)
		self.movelog.append(self.this_move)


	def refresh_stats(self):
		if self.last_move:
			# Fifty move rule
			if not self.last_move.capture and type(self.last_move.agent) is not Pawn:
				self.rulecount_fiftymoves += 1
			else:
				self.rulecount_fiftymoves = 0

			# Threefold repetition rule
			fenlog = [tuple(move.fen.split()[:3]) for move in self.movelog[:self.halfmovenum+1]]
			self.rulecount_threereps = {fen : fenlog.count(fen) for fen in fenlog}[
				tuple(self.coach.export_FEN().split()[:3])
			]

			# Movelog
			self.last_move.rulecount_fiftymoves = self.rulecount_fiftymoves
			self.last_move.rulecount_threereps  = self.rulecount_threereps
		else:
			self.rulecount_fiftymoves = 0
			self.rulecount_threereps  = 1

		# Counters
		self.coach.analysis.ctr_fifty_move.text = str(self.rulecount_fiftymoves)
		self.coach.analysis.ctr_three_reps.text = str(self.rulecount_threereps)


	def is_in_check(self , colour , movement=None):
		in_check = False

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

		for man in self.all_men(colour=("w" if colour == "b" else "b")):
			for tile in man.pseudolegal_moves():
				if tile.occupant and (
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


	def is_in_checkmate(self , ply=None):
		colour = ply or self.ply

		# Can any of your men make a move that averts or relieves a check?
		for man in self.all_men(colour=colour):
			if man.legal_moves():
				return False

		# If not, the game is over, one way or another.
		if self.is_in_check(colour):
			self.outcome = (
				"Black" if colour == "w" else "White",
				"Checkmate"
			)
		else:
			self.outcome = (
				"Draw",
				"Stalemate"
			)

		return True


	def peek(self , t=5):
		self.render()
		pygame.display.update()
		time.sleep(t)


	@property
	def plynot(self):
		return "w" if self.ply == "b" else "b"



class Move:
	def __init__(self , board , fen=None):
		self.board = board
		self.fen   = fen

		# Immutables
		self.number = None
		self.colour = None

		# Basics
		self.origin = None
		self.target = None
		self.agent  = None

		# Specials
		self.forced = None
		self.castle = None
		self.promo  = None
		self.ep     = None

		# Extras
		self.text = ''

		self.capture 	  = None
		self.in_check 	  = None
		self.in_checkmate = None

		self.rulecount_fiftymoves = None
		self.rulecount_threereps  = None

		# Annotations
		self.lights = []
		self.quiver = []


	def __str__(self):
		attributes = vars(self).copy()

		attributes["promo"]  = self.promo
		attributes["origin"] = self.origin.position if self.origin else None
		attributes["target"] = self.target.position if self.target else None
		attributes["origin occupant"] = self.origin.occupant if self.origin else None
		attributes["target occupant"] = self.target.occupant if self.target else None

		### push "submove" to the end
		if self.castle:
			attributes["submove"] = attributes.pop("submove")

		rep = ["---------------"]
		for k,v in attributes.items():
			rep.append(k + ":\t" + str(v))
		rep.append("---------------")

		return "\n".join(rep)


	def vocalise(self):
		if self.board.is_in_check(("w","b")[self.board.ply == "w"]):
			pygame.mixer.Sound.play(self.board.sound_move_check)
		elif self.capture:
			pygame.mixer.Sound.play(self.board.sound_move_capture)
		else:
			pygame.mixer.Sound.play(self.board.sound_move_quiet)


	def rewind(self):
		from copy import copy

		unmove = copy(self)

		unmove.origin , unmove.target = unmove.target , unmove.origin
		if unmove.castle:
			unmove.submove = copy(unmove.submove).rewind()

		return unmove


	def scribe(self):
		self.text = ''

		# Castling
		if self.castle == "q":
			self.text += "O-O-O"
		elif self.castle == "k":
			self.text += "O-O"
		else:
			# Mechanics
			### agent identifier
			self.text += self.agent.creed if not self.capture else (self.agent.creed or C.FILES[self.origin.f])

			### disambiguation (unnecessary for pawns)
			if self.agent.creed:
				cache = self.target.occupant
				self.target.occupant = None
				attackers = self.board.attackers_of(self.target,self.agent.colour,self.agent.creed)
				self.target.occupant = cache

				if attackers:
					# If another chessman of the same creed and colour contends for the target square
					if not any([man.f == self.origin.f for man in attackers]):
						self.text += self.origin.pgn[0]
					elif not any([man.r == self.origin.r for man in attackers]):
						self.text += self.origin.pgn[1]
					else:
						self.text += self.origin.pgn

			### moves & captures
			self.text += "x" if self.capture else ""
			self.text += C.FILES[self.target.f] + str(self.target.r)

			### promotions
			if self.promo:
				self.text += "=" + self.promo.creed

		return self.text


	def animate(self , brake=8):
		dx = self.target.x - self.origin.x
		dy = self.target.y - self.origin.y

		sprite = pygame.Surface.convert_alpha(self.agent.image)
		rect   = sprite.get_rect(center=self.origin.rect.center)
		ox,oy  = rect.x,rect.y

		if self.castle:
			self.submove.origin.occupant = self.submove.target.occupant = None
			self.board.tile_of(*self.submove.target.position).occupant  = None

			dx_rook = self.submove.target.x - self.submove.origin.x
			dy_rook = self.submove.target.y - self.submove.origin.y

			sprite_rook = pygame.Surface.convert_alpha(self.submove.agent.image)
			rect_rook   = sprite.get_rect(center=self.submove.origin.rect.center)
			ox_rook,oy_rook = rect_rook.x,rect_rook.y

		total_frames = brake * round( (abs(self.target.f - self.origin.f) + abs(self.target.r - self.origin.r))**(2/3) )
		for frame in range(total_frames):
			rect.x = ox + dx*(frame/total_frames)
			rect.y = oy - dy*(frame/total_frames)

			self.origin.is_fresh = self.target.is_fresh = True

			self.board.render()
			self.board.coach.display.blit(sprite,rect)

			if self.castle:
				rect_rook.x = ox_rook + dx_rook*(frame/total_frames)
				rect_rook.y = oy_rook - dy_rook*(frame/total_frames)
				self.board.coach.display.blit(sprite_rook,rect_rook)

			pygame.display.update()

		if self.castle:
			self.board.tile_of(*self.submove.target.position).occupant = self.submove.agent
			self.submove.agent.push(self.submove.target)


	def promote(self, force=None):
		if force:
			# Reading movetext
			if force == "Q":
				from source.men.Queen import Queen
				self.promo = Queen(
					self.board,
					self.colour,
					self.agent.position,
				)
			elif force == "R":
				from source.men.Rook import Rook
				self.promo = Rook(
					self.board,
					self.colour,
					self.agent.position,
				)
			elif force == "B":
				from source.men.Bishop import Bishop
				self.promo = Bishop(
					self.board,
					self.colour,
					self.agent.position,
				)
			elif force == "N":
				from source.men.Knight import Knight
				self.promo = Knight(
					self.board,
					self.colour,
					self.agent.position,
				)
			else:
				raise Exception("Invalid (forced) promotion!")

		# Selection UI
		else:
			veil = pygame.Surface(C.BOARD_SIZE,pygame.SRCALPHA)
			veil.fill((125,125,125,5))

			promo_images = [
				pygame.transform.scale(
					pygame.image.load(C.DIR_SETS + self.colour + "_queen.png"),
					C.TILE_SIZE
				),
				pygame.transform.scale(
					pygame.image.load(C.DIR_SETS + self.colour + "_rook.png"),
					C.TILE_SIZE
				),
				pygame.transform.scale(
					pygame.image.load(C.DIR_SETS + self.colour + "_bishop.png"),
					C.TILE_SIZE
				),
				pygame.transform.scale(
					pygame.image.load(C.DIR_SETS + self.colour + "_knight.png"),
					C.TILE_SIZE
				)
			]

			screen_centre = [l/2 for l in C.BOARD_SIZE]
			promo_rects = [
				promo_images[0].get_rect(bottomright=screen_centre),
				promo_images[1].get_rect(bottomleft=screen_centre),
				promo_images[2].get_rect(topright=screen_centre),
				promo_images[3].get_rect(topleft=screen_centre)
			]

			paused = True
			while paused:
				for event in pygame.event.get():
					if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
						cursor = (event.pos[0] - C.SIDEBAR_WIDTH , event.pos[1])
						if promo_rects[0].collidepoint(cursor):
							from source.men.Queen import Queen
							self.promo = Queen(
								self.board,
								self.colour,
								self.agent.position,
							)
							paused = False
						elif promo_rects[1].collidepoint(cursor):
							from source.men.Rook import Rook
							self.promo = Rook(
								self.board,
								self.colour,
								self.agent.position,
							)
							paused = False
						elif promo_rects[2].collidepoint(cursor):
							from source.men.Bishop import Bishop
							self.promo = Bishop(
								self.board,
								self.colour,
								self.agent.position,
							)
							paused = False
						elif promo_rects[3].collidepoint(cursor):
							from source.men.Knight import Knight
							self.promo = Knight(
								self.board,
								self.colour,
								self.agent.position,
							)
							paused = False

				self.board.coach.display.blit(veil,(C.SIDEBAR_WIDTH,0))
				for rect,img in zip(promo_rects,promo_images):
					pygame.draw.rect(
						veil,
						(60,60,66),
						rect
					)
					veil.blit(
						img,
						rect.topleft
					)

				pygame.display.update()


	def rinse(self):
		self.lights.clear()
		self.quiver.clear()


	def clean(self):
		# Basics
		self.target = None
		self.agent  = None

		# Specials
		self.forced = None
		self.castle = None
		self.promo  = None
		self.ep     = None


	@property
	def id(self):
		return (self.origin.pgn if self.origin else "") + "->" + (self.target.pgn if self.target else "")


class Line(list):
	# CAN ADD:
	#   1)  Validate appended moves.
	#   2)
	def __init__(self , board):
		super().__init__()
		self.board = board

	def __str__(self):
		# return " - ".join(move.origin.pgn + move.target.pgn for move in self)
		return "-".join([move.uci() for move in self])

	# Ensures ".copy()" returns object of type Line rather than list.
	def copy(self):
		new = Line(self.board)
		new.extend(self)
		return new