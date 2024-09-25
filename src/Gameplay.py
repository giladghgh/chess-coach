import time
import pygame

from src.Constants import C
from src.Tile import Tile

from src.men.Pawn import Pawn
from src.men.Knight import Knight
from src.men.Bishop import Bishop
from src.men.Rook import Rook
from src.men.Queen import Queen
from src.men.King import King





class Board:
	def __init__(self , coach):
		self.coach = coach

		# Interface
		self.w = C.BOARD_WIDTH
		self.h = C.BOARD_HEIGHT

		# Mechanics
		self.ply   = "w"
		self.agent = None

		self.halfmovenum = 1
		self.movenum     = 1

		self.last_move = None
		self.this_move = Move(self,fen=C.INIT_FEN)
		self.movelog   = [self.this_move,]

		self.all_tiles = []

		# Gameplay
		self.opening = ''
		self.outcome = (None,None)

		# Rule Counts
		self.rulecount_fiftymoves = 0
		self.rulecount_threereps  = 1

		# Audio
		self.sound_move_quiet   = pygame.mixer.Sound(C.DIR_SOUNDS + "\\move_quiet.wav")
		self.sound_move_check   = pygame.mixer.Sound(C.DIR_SOUNDS + "\\move_check.wav")
		self.sound_move_capture = pygame.mixer.Sound(C.DIR_SOUNDS + "\\move_capture.wav")


	def compose(self , shell):
		self.all_tiles.clear()
		for r,rank in enumerate(shell):
			r = 8 - r
			for f,man in enumerate(rank):
				f = 1 + f

				self.all_tiles.append(
					Tile(self.coach.screen , f , r , *C.TILE_SIZE)
				)

				if not man.isspace():
					colour = man[0]
					creed  = man[1]
					tile   = self.tile(f,r)

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


	def tile(self , *args):
		if len(args) == 1:
			file = args[0].f
			rank = args[0].r
		else:
			file = args[0]
			rank = args[1]

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


	def all_threats(self , tile , colour=None , creed=None):
		threats = []
		for man in self.all_men(colour,creed):
			for tgt in man.legal_moves():
				if tgt.position == tile.position:
					threats.append(man)

		return threats


	def render(self):
		# Tiles
		### legal (high overhead so separate loop)
		if C.SHOW_MOVE_LEGAL and self.agent:
			for tile in self.agent.legal_moves():
				self.tile(tile).is_legal = True

		for tile in self.all_tiles:
			### fresh
			if C.SHOW_MOVE_FRESH and ((
				self.agent
				and
				tile.position == self.agent.position
			) or (
				self.last_move
				and
				tile in (
					self.last_move.origin,
					self.last_move.target
				)
			)):
				tile.is_fresh = True

			### focus
			if tile in self.this_move.lights:
				tile.is_focus = True

			tile.render()
			tile.is_fresh = False
			tile.is_legal = False
			tile.is_focus = False

		# Annotations
		for arrow in self.this_move.quiver:
			arrow.shoot()


	def handle_click(self , file , rank , promo=None , show=True):
		chosen_tile = self.tile(file,rank)

		# Initiate move:
		if self.agent is None:
			# Wash annotations:
			if not chosen_tile.occupant:
				self.this_move.wash()

			# Select agent:
			elif chosen_tile.occupant.colour == self.ply:
				self.agent 			= chosen_tile.occupant
				self.agent.position = chosen_tile.position

		# Continue move:
		else:
			# Complete move:
			if self.agent.go(self.this_move , chosen_tile , promo , show):
				# Mechanics
				### unrestricted prev/next
				del self.movelog[self.halfmovenum - 1:]

				### turnover
				if self.ply == "w":
					self.ply = "b"
				else:
					self.ply = "w"
					self.movenum += 1
				self.halfmovenum += 1

				# Movelog
				self.last_move = self.this_move
				self.this_move = Move(self,fen=self.coach.export_FEN())

				self.movelog.append(self.last_move)
				self.movelog.append(self.this_move)

				# Clock
				self.coach.clock.tack()

				# Calibrate
				self.calibrate()

			# Switch agent:
			elif chosen_tile.occupant and chosen_tile.occupant.colour == self.ply:
				if chosen_tile.occupant is self.agent:
					self.agent = None
				else:
					self.agent 			= chosen_tile.occupant
					self.agent.position = chosen_tile.position

			# Deselect agent & wash:
			else:
				self.agent = None
				self.this_move.wash()


	def calibrate(self):
		# Threefold repetition rule
		if self.last_move:
			fenlog = [tuple(move.fen.split()[:3]) for move in self.movelog[:self.halfmovenum+1]]
			self.rulecount_threereps = {fen : fenlog.count(fen) for fen in fenlog}[
				tuple(self.this_move.fen.split()[:3])
			]

			### update movelog
			self.last_move.rulecount_fiftymoves = self.rulecount_fiftymoves
			self.last_move.rulecount_threereps  = self.rulecount_threereps

		# Counters
		self.coach.analysis.counters["RULECOUNT_FIFTYMOVES"].field = str(self.rulecount_fiftymoves)
		self.coach.analysis.counters["RULECOUNT_THREEREPS"].field  = str(self.rulecount_threereps)

		# Reader
		self.coach.reader.update()

		# Graveyard
		self.coach.graveyard.update()

		###################
		# self.coach.engine.model.set_fen(self.this_move.fen)
		# self.coach.analysis.counters["SCORE_SIMPLE"].field = f'{self.coach.engine.evaluate():.2f}'
		###################


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



class Move:
	def __init__(self , board , fen):
		self.board = board
		self.fen   = fen

		# Innates
		self.number = self.board.movenum
		self.colour = self.board.ply

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
		self.text = None

		self.capture 	  = None
		self.in_check 	  = None
		self.in_checkmate = None

		# Draw criteria
		self.rulecount_fiftymoves = None
		self.rulecount_threereps  = None

		# Clock
		self.commence = None
		# self.duration = None
		self.conclude = None

		# Annotations
		self.lights = []
		self.quiver = []


	def __repr__(self):
		return (self.origin.pgn if self.origin else "") + "->" + (self.target.pgn if self.target else "")


	def rewind(self):
		from copy import copy

		unmove = copy(self)

		unmove.origin , unmove.target = unmove.target , unmove.origin
		if unmove.castle:
			unmove.submove = copy(unmove.submove).rewind()

		return unmove


	def vocalise(self):
		if self.board.is_in_check(("w","b")[self.board.ply == "w"]):
			pygame.mixer.Sound.play(self.board.sound_move_check)
		elif self.capture:
			pygame.mixer.Sound.play(self.board.sound_move_capture)
		else:
			pygame.mixer.Sound.play(self.board.sound_move_quiet)


	def inscribe(self):
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
				attackers = self.board.all_threats(self.target , self.agent.colour , self.agent.creed)
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


	def animate(self):
		dx = self.target.x - self.origin.x
		dy = self.target.y - self.origin.y

		sprite = pygame.Surface.convert_alpha(self.agent.image)
		rect   = sprite.get_rect(center=self.origin.rect.center)
		ox,oy  = rect.x,rect.y

		# 1/3
		if self.castle:
			self.submove.origin.occupant = self.submove.target.occupant = None
			self.board.tile(*self.submove.target.position).occupant  = None

			dx_rook = self.submove.target.x - self.submove.origin.x
			dy_rook = self.submove.target.y - self.submove.origin.y

			sprite_rook = pygame.Surface.convert_alpha(self.submove.agent.image)
			rect_rook   = sprite.get_rect(center=self.submove.origin.rect.center)
			ox_rook,oy_rook = rect_rook.x,rect_rook.y

		manhattan 	 = abs(self.target.f - self.origin.f) + abs(self.target.r - self.origin.r)
		total_frames = round(C.MOVE_SPEED * manhattan**(1/2))
		for frame in range(total_frames):
			if C.SHOW_MOVE_FRESH:
				self.origin.is_fresh = self.target.is_fresh = True

			self.board.render()

			rect.x = ox + dx*(frame/total_frames)
			rect.y = oy - dy*(frame/total_frames)
			self.board.coach.screen.blit(sprite,rect)

			# 2/3
			if self.castle:
				rect_rook.x = ox_rook + dx_rook*(frame/total_frames)
				rect_rook.y = oy_rook - dy_rook*(frame/total_frames)
				self.board.coach.screen.blit(sprite_rook,rect_rook)

			pygame.display.update()

		# 3/3
		if self.castle:
			self.board.tile(self.submove.target).occupant = self.submove.agent
			self.submove.agent.send(self.submove.target)


	def promote(self , force=None):
		if force or C.AUTO_PROMOTE:
			# Reading movetext
			if "Q" in (force,C.AUTO_PROMOTE):
				from src.men.Queen import Queen
				self.promo = Queen(
					self.board,
					self.colour,
					self.agent.position,
				)
			elif "R" in (force,C.AUTO_PROMOTE):
				from src.men.Rook import Rook
				self.promo = Rook(
					self.board,
					self.colour,
					self.agent.position,
				)
			elif "B" in (force,C.AUTO_PROMOTE):
				from src.men.Bishop import Bishop
				self.promo = Bishop(
					self.board,
					self.colour,
					self.agent.position,
				)
			elif "N" in (force,C.AUTO_PROMOTE):
				from src.men.Knight import Knight
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
					pygame.image.load(C.DIR_SET + self.colour + "_queen.png"),
					C.TILE_SIZE
				),
				pygame.transform.scale(
					pygame.image.load(C.DIR_SET + self.colour + "_rook.png"),
					C.TILE_SIZE
				),
				pygame.transform.scale(
					pygame.image.load(C.DIR_SET + self.colour + "_bishop.png"),
					C.TILE_SIZE
				),
				pygame.transform.scale(
					pygame.image.load(C.DIR_SET + self.colour + "_knight.png"),
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
							from src.men.Queen import Queen
							self.promo = Queen(
								self.board,
								self.colour,
								self.agent.position,
							)
							paused = False
						elif promo_rects[1].collidepoint(cursor):
							from src.men.Rook import Rook
							self.promo = Rook(
								self.board,
								self.colour,
								self.agent.position,
							)
							paused = False
						elif promo_rects[2].collidepoint(cursor):
							from src.men.Bishop import Bishop
							self.promo = Bishop(
								self.board,
								self.colour,
								self.agent.position,
							)
							paused = False
						elif promo_rects[3].collidepoint(cursor):
							from src.men.Knight import Knight
							self.promo = Knight(
								self.board,
								self.colour,
								self.agent.position,
							)
							paused = False

				self.board.coach.screen.blit(veil,(C.SIDEBAR_WIDTH,0))
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


	def wash(self):
		self.lights.clear()
		self.quiver.clear()



class Line(list):
	def __init__(self , *args):
		super().__init__()

		self.eval = -float("inf")
		self.main = []

		for arg in args:
			try:
				for item in arg:
					self.append(item)
			except TypeError:
				self.append(arg)


	def __repr__(self):
		return str(self.eval) + "L" + str(len(self)) + super().__repr__()


	def __add__(self , this):
		return Line(self,this)


	def append(self , this):
		super().append(this)

		if this.eval > self.eval:
			self.eval = this.eval
			self.main.append(this)



class Clock:
	def __init__(self , coach):
		self.coach = coach

		from src.Element import ButtonClockFace,ButtonClockLink

		self.whiteface = ButtonClockFace(
			self.coach.tray,
			C.TRAY_PAD + C.TRAY_WIDTH/2 - C.BUTTON_WIDTH/2,
			(2/3)*C.BOARD_HEIGHT - C.BUTTON_HEIGHT,
			player="WHITE",
			clock=self
		)
		self.blackface = ButtonClockFace(
			self.coach.tray,
			C.TRAY_PAD + C.TRAY_WIDTH/2 - C.BUTTON_WIDTH/2,
			(1/3)*C.BOARD_HEIGHT,
			player="BLACK",
			clock=self
		)
		self.link = ButtonClockLink(
			self.coach.tray,
			C.TRAY_PAD + C.TRAY_WIDTH/2 - 0.375*C.BUTTON_WIDTH,
			C.BOARD_HEIGHT/2 - 0.175*C.BUTTON_HEIGHT,
			(
				0.75*C.BUTTON_WIDTH,
				0.35*C.BUTTON_HEIGHT,
			),
			True,
			clock=self
		)
		self.buttons = [
			self.whiteface,
			self.blackface,
			self.link,
		]

		self.time = None
		self.reset()

		self.alerts = []


	def reset(self):
		self.whiteface.active       = self.blackface.active       = False
		self.whiteface.colour       = self.blackface.colour       = C.BUTTON_DEAD
		self.whiteface.timer.colour = self.blackface.timer.colour = C.TIMER_DEAD

		self.time                 = 60*max(C.TIME_WHITE_START,C.TIME_BLACK_START) + max(C.TIME_WHITE_BONUS,C.TIME_BLACK_BONUS)
		self.whiteface.timer.time = 60*C.TIME_WHITE_START + C.TIME_WHITE_BONUS
		self.blackface.timer.time = 60*C.TIME_BLACK_START + C.TIME_BLACK_BONUS


	def render(self):
		for button in self.buttons:
			button.render()


	def tick(self):
		self.time -= 1

		# Propagate
		if self.whiteface.active and self.coach.board.ply == "w":
			self.whiteface.timer.time -= 1
		elif self.blackface.active and self.coach.board.ply == "b":
			self.blackface.timer.time -= 1

		# Alerts
		if self.time == 900:
			self.buzz()
		elif self.time == 0:
			self.bang()


	def tack(self):
		ply_is_white = self.coach.board.ply == "w"

		white = self.whiteface
		black = self.blackface

		# Movelog
		self.coach.board.last_move.conclude = black.timer.time if ply_is_white else white.timer.time
		self.coach.board.this_move.commence = white.timer.time if ply_is_white else black.timer.time

		# Timers
		### white
		if white.active:
			white.timer.colour = C.TIMER_LIVE if ply_is_white else C.TIMER_IDLE
		else:
			white.timer.colour = C.TIMER_DEAD

		### black
		if black.active:
			black.timer.colour = C.TIMER_IDLE if ply_is_white else C.TIMER_LIVE
		else:
			black.timer.colour = C.TIMER_DEAD


	def buzz(self):
		pass


	def bang(self):
		# Handle end of time
		pass
