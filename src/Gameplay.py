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

		### sounds
		self.sound_clean = pygame.mixer.Sound(C.DIR_SOUNDS + "\\board_clean.wav")
		self.sound_flipA = pygame.mixer.Sound(C.DIR_SOUNDS + "\\board_flipA.wav")
		self.sound_flipB = pygame.mixer.Sound(C.DIR_SOUNDS + "\\board_flipB.wav")
		self.sound_check = pygame.mixer.Sound(C.DIR_SOUNDS + "\\move_check.wav")
		self.sound_void  = pygame.mixer.Sound(C.DIR_SOUNDS + "\\board_void.wav")

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


	def compose(self , blueprint):
		self.all_tiles.clear()
		for r,rank in enumerate(blueprint):
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
				self.this_move.clean()

			# Select agent:
			elif chosen_tile.occupant.colour == self.ply:
				self.agent 			= chosen_tile.occupant
				self.agent.position = chosen_tile.position

		# Continue move:
		else:
			# Complete move:
			if self.agent.go(self.this_move , chosen_tile , promo , show):
				# Mechanics
				### unrestricted turn control
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

				# Calibrate
				self.calibrate()

				### clock
				self.coach.clock.tack()

			# Switch agent:
			elif chosen_tile.occupant:
				if chosen_tile.occupant.colour == self.ply:
					if chosen_tile.occupant is self.agent:
						self.agent = None
					else:
						self.agent 			= chosen_tile.occupant
						self.agent.position = chosen_tile.position

				# Deselect agent & clear annotations:
				else:
					self.agent = None
					self.this_move.clean()

			# Moot move
			else:
				self.agent = None
				self.sound_void.play()


	def calibrate(self):
		if self.last_move:
			# Fifty move rule
			if self.last_move.agent.creed and not self.last_move.capture:
				self.rulecount_fiftymoves += 1
			else:
				self.rulecount_fiftymoves = 0

			# Threefold repetition rule
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


	@property
	def dreaming(self):
		return self.halfmovenum != len(self.movelog)



class Move:
	# Sounds    (Move sound system uses mixer.Music, not mixer.Sound, to play simulatenous audio)
	sound_capture   = C.DIR_SOUNDS + "\\move_capture.wav"
	sound_castle    = C.DIR_SOUNDS + "\\move_castle.wav"
	sound_check     = C.DIR_SOUNDS + "\\move_check.wav"
	sound_checkmate = C.DIR_SOUNDS + "\\move_checkmate.wav"
	sound_promo     = C.DIR_SOUNDS + "\\move_promote.wav"
	sound_quiet     = C.DIR_SOUNDS + "\\move_quiet.wav"
	sound_void      = C.DIR_SOUNDS + "\\move_void.wav"

	def __init__(self , board , fen=None):
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
		self.score = None           ### score of fen AFTER move, NOT before (so unlike move.fen)
		self.text  = None

		self.capture 	  = None
		self.in_check 	  = None
		self.in_checkmate = None

		# Draw criteria
		self.rulecount_fiftymoves = None
		self.rulecount_threereps  = None

		# Clock
		self.commence = None
		self.duration = None
		self.conclude = None

		# Annotations
		self.lights = []
		self.quiver = []


	def __repr__(self):
		return (self.origin.pgn if self.origin else "") + "->" + (self.target.pgn if self.target else "")


	def rewind(self):
		unmove = Move(self.board,self.fen)

		unmove.__dict__ = self.__dict__.copy()

		unmove.origin , unmove.target = unmove.target , unmove.origin
		if unmove.castle:
			unmove.submove = unmove.submove.rewind()

		return unmove


	def talk(self):
		if self.promo:
			pygame.mixer.music.load(Move.sound_promo)
		elif self.capture:
			pygame.mixer.music.load(Move.sound_capture)
		elif self.castle:
			pygame.mixer.music.load(Move.sound_castle)
		else:
			pygame.mixer.music.load(Move.sound_quiet)
		pygame.mixer.music.play()

		if self.in_check:           ### checks sound simultaneously
			self.board.sound_check.play()


	def note(self):
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
				attackers = self.board.all_threats(self.target, self.agent.colour, self.agent.creed)
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
					pygame.image.load(C.DIR_SET + self.colour + "q.png"),
					C.TILE_SIZE
				),
				pygame.transform.scale(
					pygame.image.load(C.DIR_SET + self.colour + "r.png"),
					C.TILE_SIZE
				),
				pygame.transform.scale(
					pygame.image.load(C.DIR_SET + self.colour + "b.png"),
					C.TILE_SIZE
				),
				pygame.transform.scale(
					pygame.image.load(C.DIR_SET + self.colour + "n.png"),
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
						cursor = (event.pos[0] - C.PANE_WIDTH , event.pos[1])
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

				self.board.coach.screen.blit(veil,(C.PANE_WIDTH,0))
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


	def enact(self, text, is_white):
		if "..." in text or not text:
			return None

		self.forced = True
		self.text 	= text

		# Standard Algebraic Notation
		san = text

		if text.count("#"):
			san = san.replace("#","")
			self.in_checkmate = True
		elif text.count("+"):
			san = san.replace("+","")
			self.in_check = True

		if text.count("x"):
			san = san.replace("x","")
			self.capture = True

		if "=" in san:
			# axb8=R
			self.origin = self.board.tile(
				C.FILES.index(san[0]),
				2 if is_white else 7
			)
			self.target = self.board.tile(
				C.FILES.index(san[-4]),
				1 if is_white else 8
			)

			self.promo = san[-1]

		if "-" in san:
			# O-O-O
			# O-O
			self.origin = self.board.tile(
				5,
				8 if is_white else 1
			)
			self.target = self.board.tile(
				7 if san.count("-") == 1 else 3,
				8 if is_white else 1
			)

		elif san.isalnum():
			# b4
			# Nf7
			# exd6
			# Raxb8
			# Qh4xe1
			self.target = self.board.tile(
				C.FILES.index(san[-2]),
				int(san[-1])
			)

			attackers = self.board.all_threats(
				self.target,
				colour=("w","b")[is_white],
				creed=san[0] if san[0].isupper() else ""
			)

			if len(attackers) == 1:
				self.origin = self.board.tile(*attackers[0].position)
			else:
				# Disambiguation
				for opp in attackers:
					if "".join([char for char in san[:-2] if char.islower() or char.isnumeric()]) in opp.pgn:
						self.origin = self.board.tile(*opp.position)

		else:
			return False


	def clean(self):
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


	def __add__(self , other):
		return Line(self,other)


	def append(self , this):
		super().append(this)

		if this.eval > self.eval:
			self.eval = this.eval
			self.main.append(this)



class Clock:
	def __init__(self , coach):
		self.coach = coach

		self.cache = None           ### remembers face activities during turn control

		# Buttons
		from src.Elements import ButtonClockFace,ButtonClockLinkLock

		self.whiteface = ButtonClockFace(
			self.coach,
			self.coach.tray,
			C.TRAY_GAP + 2*C.BUTTON_WIDTH + C.GRID_GAP,
			C.BOARD_HEIGHT/2 + C.TILE_HEIGHT,
			clock=self,
			player="WHITE"
		)
		self.blackface = ButtonClockFace(
			self.coach,
			self.coach.tray,
			C.TRAY_GAP + 2*C.BUTTON_WIDTH + C.GRID_GAP,
			C.BOARD_HEIGHT/2 - C.TILE_HEIGHT - C.BUTTON_HEIGHT,
			clock=self,
			player="BLACK"
		)
		self.linklock  = ButtonClockLinkLock(
			self.coach,
			self.coach.tray,
			C.TRAY_GAP + + (5/2)*C.BUTTON_WIDTH + C.GRID_GAP - (3/8)*C.BUTTON_WIDTH,
			C.BOARD_HEIGHT/2 - (3/8)*C.BUTTON_HEIGHT,
			[3*L/4 for L in C.BUTTON_SIZE],
			clock=self
		)
		self.buttons = {
			"WHITE"    : self.whiteface,
			"BLACK"    : self.blackface,
			"LINKLOCK" : self.linklock,
		}

		# Mechanics
		self.time = 0
		self.TICK = pygame.event.Event(pygame.event.custom_type(),player=None)

		self.TICKS = (
			self.TICK,
			self.whiteface.timer.TICK,
			self.blackface.timer.TICK,
		)

		# Sounds
		self.sound_clock_tick     = pygame.mixer.Sound(C.DIR_SOUNDS + "\\clock_tick.wav")
		self.sound_clock_tack     = pygame.mixer.Sound(C.DIR_SOUNDS + "\\clock_tack.wav")
		self.sound_clock_click    = pygame.mixer.Sound(C.DIR_SOUNDS + "\\clock_click.wav")
		self.sound_clock_scramble = pygame.mixer.Sound(C.DIR_SOUNDS + "\\clock_scramble.wav")
		self.sound_clock_tick.set_volume(0.75)
		self.sound_clock_tack.set_volume(0.5)
		self.sound_clock_click.set_volume(0.25)


	def reset(self):
		self.whiteface.active = False
		self.blackface.active = False
		self.cache = None

		self.time = 0
		pygame.time.set_timer(self.TICK,0)
		pygame.time.set_timer(self.TICK,10)     ### 10ms ideal resolution, OS bottleneck

		### link lock
		self.linklock.reset()

		### external timers
		self.whiteface.reset()
		self.blackface.reset()

		### move clock
		self.coach.board.this_move.commence = (
			self.whiteface.timer.time,
			self.blackface.timer.time,
		)[self.coach.board.ply == "b"]


	def handle_tick(self , event):
		self.time += 1

		# Clocks
		if event.player is None:
			### reader
			if self.coach.buttons_turns["ECOInterpreter"].active and self.coach.board.opening.startswith("."):
				self.coach.reader._time += 1
				self.coach.board.opening = {
					False : "...",
					True  : ".",
				}[not self.coach.reader._time%100]

		# Timers
		if not self.coach.board.dreaming:                                       ### skips when dreaming ...
			for face in (self.whiteface,self.blackface):
				if face.active is not False and face.player == event.player:    ### ... and if inactive or wrong-colour tick
					face.timer.tick()

					### scramble
					if face.timer.scramble:
						if face.timer.time > 1000:
							face.timer.scramble = False
					elif face.timer.time <= 1000:
						face.timer.scramble = True
						self.sound_clock_scramble.play()

					### tick sound
					if face.timer.scramble:
						if not face.timer.time % 100:                           ### no correction needed ...
							self.sound_clock_tick.play(loops=1)
					else:
						if not (face.timer.time-50) % 100:                      ### ... but here it is??
							self.sound_clock_tick.play()


	def tack(self):
		board  = self.coach.board
		wtimer = self.whiteface.timer
		btimer = self.blackface.timer

		if board.ply == "w":
			board.this_move.commence = wtimer.time
			board.last_move.conclude = btimer.time

			wtimer.case_colour = C.TIMER_CASE_LIVE
			btimer.case_colour = C.TIMER_CASE_IDLE
			if self.whiteface.active:      ### is None when locked
				wtimer.play()
				self.sound_clock_tack.play()
			if self.blackface.active:
				btimer.time += btimer.bonus
				btimer.wait()

		else:
			board.this_move.commence = btimer.time
			board.last_move.conclude = wtimer.time

			wtimer.case_colour = C.TIMER_CASE_IDLE
			btimer.case_colour = C.TIMER_CASE_LIVE
			if self.whiteface.active:
				wtimer.time += wtimer.bonus
				wtimer.wait()
			if self.blackface.active:
				btimer.play()
				self.sound_clock_tack.play()

		board.last_move.duration = board.last_move.conclude - board.last_move.commence


	def jibe(self , resume=False):
		board = self.coach.board
		white = self.whiteface
		black = self.blackface

		ply_is_white = board.ply == "w"

		if resume:
			### resume button states
			self.linklock.state = self.cache[0]
			self.linklock.apply()

			white.active , black.active = self.cache[1:]
			self.cache = None

			### resume readings
			white.timer.text = self.read(white.timer.time)
			black.timer.text = self.read(black.timer.time)

			### resume timers
			if ply_is_white:
				white.timer.case_colour = C.TIMER_CASE_LIVE
				black.timer.case_colour = C.TIMER_CASE_IDLE
				if self.whiteface.active:
					white.timer.play()
				else:
					white.timer.stop()

				if self.blackface.active:
					black.timer.wait()
				else:
					black.timer.stop()

			else:
				white.timer.case_colour = C.TIMER_CASE_IDLE
				black.timer.case_colour = C.TIMER_CASE_LIVE
				if self.whiteface.active:
					white.timer.wait()
				else:
					white.timer.stop()

				if self.blackface.active:
					black.timer.play()
				else:
					black.timer.stop()

		else:
			self.cache = self.cache or [
				self.linklock.state,
				white.active,
				black.active,
			]

			self.linklock.reset()

			if self.cache[1]:
				white.timer.wait()
			else:
				white.timer.stop()

			if self.cache[2]:
				black.timer.wait()
			else:
				black.timer.stop()

			if ply_is_white:
				white.timer.text = self.read(board.this_move.commence)
				black.timer.text = self.read(board.last_move.conclude if board.last_move else 100*black.start)

				white.timer.case_colour = C.TIMER_CASE_LIVE
				black.timer.case_colour = C.TIMER_CASE_IDLE

			else:
				white.timer.text = self.read(board.last_move.conclude if board.last_move else 100*white.start)
				black.timer.text = self.read(board.this_move.commence)

				white.timer.case_colour = C.TIMER_CASE_IDLE
				black.timer.case_colour = C.TIMER_CASE_LIVE


	@staticmethod
	def read(time , scramble=False):
		if not time:
			return ""

		if scramble:
			s,ms = divmod( round(time) , 100 )
			return f'{s:02d}.{ms:02d}'

		else:
			m,s = divmod( round(time/100) , 60 )
			h,m = divmod(m,60)
			return f'{h:02d}:{m:02d}:{s:02d}' if h else f'{m:02d}:{s:02d}'

	@property
	def active(self):
		return self.whiteface.active or self.blackface.active

	@property
	def actives(self):
		return self.whiteface.active , self.blackface.active

	@property
	def times_elapsed(self):
		w,b = 0,0
		for move in self.coach.board.movelog:
			match move.colour:
				case "w":
					w += move.duration
				case "b":
					b += move.duration

		return w,b