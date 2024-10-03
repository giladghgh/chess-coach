import pygame,time

from src.Constants import C
from src.Gameplay import Board,Move,Clock
from src.Engine import Engine
from src.Contexts import *
from src.Elements import *





class Coach:
	def __init__(self):
		self.screen = pygame.display.set_mode(C.WINDOW_SIZE)

		# Faculties
		self.board  = Board(self)
		self.engine = Engine(self)

		# Contexts
		self.settings = Settings(self)
		self.analysis = Analysis(self)
		self.coaching = Coaching(self)
		self.contexts = [
			self.settings,
			self.analysis,
			self.coaching,
		]

		# Interface
		self.font = pygame.font.SysFont("Consolas",14,bold=True)
		self.pane = pygame.Surface(C.PANE_SIZE,pygame.SRCALPHA)
		self.tray = pygame.Surface(C.TRAY_SIZE,pygame.SRCALPHA)

		### facets
		self.graveyard = Graveyard(self)
		self.reader    = Reader(self)
		self.clock     = Clock(self)

		### annotations
		self.anchor = None

		### banners
		self.banners = {
			"BOTS"  : pygame.Rect(
				C.X_MARGIN,
				125 + 5*(C.BUTTON_HEIGHT + 3*C.GRID_GAP),
				*C.TEXTBOX_SIZE
			),
		}

		### buttons
		self.toggle_tray = ToggleTray(
			self.pane,
			C.X_MARGIN + C.TEXTBOX_WIDTH - C.BUTTON_WIDTH/2,
			C.Y_MARGIN,
			C.BUTTON_SIZE,
			True,
			coach=self
		)
		self.contexts_menu = {
			"COACHING"  : ButtonContextOpen(
				self.pane,
				C.X_MARGIN + 2*(C.BUTTON_WIDTH + C.GRID_GAP),
				C.Y_MARGIN,
				context=self.coaching,
				coach=self
			),
			"ANALYSIS"  : ButtonContextOpen(
				self.pane,
				C.X_MARGIN + 1*(C.BUTTON_WIDTH + C.GRID_GAP),
				C.Y_MARGIN,
				context=self.analysis,
				coach=self
			),
			"SETTINGS"  : ButtonContextOpen(
				self.pane,
				C.X_MARGIN,
				C.Y_MARGIN,
				context=self.settings,
				coach=self
			),
		}
		self.buttons_turns = {
			"NEXT"  : ButtonNext(
				self.pane,
				C.X_MARGIN + C.TEXTBOX_WIDTH - C.BUTTON_WIDTH,
				self.reader.rect.bottom + C.GRID_GAP,
				coach=self
			),
			"PREV"	: ButtonPrevious(
				self.pane,
				C.X_MARGIN + C.TEXTBOX_WIDTH - 2*C.BUTTON_WIDTH,
				self.reader.rect.bottom + C.GRID_GAP,
				coach=self
			),
			"RESET"	: ButtonReset(
				self.pane,
				C.X_MARGIN,
				self.reader.rect.bottom + C.GRID_GAP,
				coach=self
			),
		}
		self.buttons_bots = {
			"BOT_BLACK"	: ButtonBot(
				self.pane,
				15,
				553,
				player="BLACK",
				engine=self.engine
			),
			"BOT_WHITE"	: ButtonBot(
				self.pane,
				15,
				683,
				player="WHITE",
				engine=self.engine
			),
		}
		self.buttons = {				##### right->left (& bottom->top if near enough) so tooltips aren't obscured
			**self.contexts_menu,
			**self.buttons_turns,
			**self.buttons_bots,
		}

		# Assemble!
		self.reset()


		###########################################
		self.tests = []
		for i in range(3):
			self.tests.append(Writer(
				self.tray,
				C.TRAY_GAP + C.TRAY_WIDTH/2 - C.TEXTBOX_WIDTH/4,
				150 + i*(C.TEXTBOX_HEIGHT+5),
				C.TEXTBOX_WIDTH/2,
				""
			))
		###########################################


		self.coaching.plug_in()         ### sorted such that tooltips aren't obscured
		self.analysis.plug_in()
		self.settings.plug_in()


	def reset(self , fen=C.INIT_FEN):
		self.board.__init__(self)
		self.import_FEN(fen)

		self.board.last_move = None
		self.board.this_move = Move(self.board,fen)
		self.board.movelog   = [self.board.this_move,]

		# For imports:
		### ply agnostic
		if self.board.ply == "b":
			self.reader.halfmove_offset = True
		### movenum agnostic
		if self.board.movenum > 1:
			self.reader.fullmove_offset = self.board.movenum

		# Calibrate
		self.board.calibrate()

		### clock
		self.clock.reset()


	def render(self):
		# Tray
		if self.tray:
			self.tray.fill((0,0,0,0))
			self.tray.fill(C.BACKGR_TRAY , (C.TRAY_GAP,0,C.TRAY_WIDTH,C.BOARD_HEIGHT))

			### clock
			for button in self.clock.buttons.values():
				button.render()

			### graveyard
			self.graveyard.render()


			###########################################
			# self.tests[0].field = str(self.board.this_move.commence)+"-"+str(self.board.this_move.conclude)
			# if self.board.last_move:
			# 	self.tests[1].field = str(self.board.last_move.commence)+"-"+str(self.board.last_move.conclude)
			# else:
			# 	self.tests[1].field = "None---None"
			# for test in self.tests:
			# 	test.render()
			###########################################


			self.screen.blit(self.tray , (C.PANE_WIDTH + C.BOARD_WIDTH - C.TRAY_GAP,0))

		#                           #
		# Board rendered separately #
		#                           #

		# Pane
		### CONTEXT
		### pane
		c = None
		for i,context in enumerate(self.contexts):
			if context.show:
				c = i
				context.render()
				break

		### NO CONTEXT
		else:
			# Pane
			self.pane.fill((0,0,0,0))
			self.pane.fill(C.BACKGR_PANE , (0,0,C.PANE_WIDTH,C.BOARD_HEIGHT))

			### elements
			for element in (
				self.reader,
				*self.buttons.values(),
			):
				element.render()

			### banners
			for subtitle,banner in self.banners.items():
				prose = self.font.render(subtitle,True,C.BUTTON_IDLE)
				pygame.draw.rect(
					self.pane,
					(110,110,110),
					banner
				)
				self.pane.blit(prose , prose.get_rect(center=banner.center))


			self.screen.blit(self.pane,(0,0))

		### tabs
		if c is not None:
			# J = len(self.contexts) - 1
			for j,cntxt in sorted( enumerate(self.contexts) , key=lambda ec : ec[1].show):
				pygame.draw.polygon(
					self.screen,
					cntxt.colour,
					points=[
						( 2*C.X_MARGIN + C.TEXTBOX_WIDTH + C.GRID_GAP , j*0.9*C.TILE_HEIGHT ),
						( 2*C.X_MARGIN + C.TEXTBOX_WIDTH + C.GRID_GAP + 10 + 8*(j==c) , j*0.9*C.TILE_HEIGHT + 0.1*C.TILE_HEIGHT ),
						( 2*C.X_MARGIN + C.TEXTBOX_WIDTH + C.GRID_GAP + 10 + 8*(j==c) , j*0.9*C.TILE_HEIGHT + 0.9*C.TILE_HEIGHT ),
						( 2*C.X_MARGIN + C.TEXTBOX_WIDTH + C.GRID_GAP , j*0.9*C.TILE_HEIGHT + C.TILE_HEIGHT ),
					]
				)


		############### SCAFFOLDING ###############
		# def xscaff(x , colour=None):
		# 	pygame.draw.line(
		# 		self.screen,colour or (0,0,0),(x,0),(x,C.BOARD_HEIGHT),
		# 	)
		# def yscaff(y , colour=None):
		# 	pygame.draw.line(
		# 		self.screen,colour or (0,0,0),(C.PANE_WIDTH+C.BOARD_WIDTH,y),(C.WINDOW_SIZE[0],y),
		# 	)
		# x,y = pygame.mouse.get_pos()
		# xscaff(x)
		# yscaff(y)
		# yscaff(C.BOARD_HEIGHT/2)
		# xscaff(C.PANE_WIDTH+C.BOARD_WIDTH+C.TRAY_WIDTH/2)
		# xscaff(2*C.X_MARGIN + C.TEXTBOX_WIDTH)
		# xscaff(C.PANE_WIDTH)
		###########################################


	# TODO: CLICK ONLY TRIGGER TOP RENDERED ELEMENT
	def handle_click(self , event):
		# Left click
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			# Tray
			if event.pos[0] > C.PANE_WIDTH + C.BOARD_WIDTH and self.tray:
				local_pos = (
					event.pos[0] - C.PANE_WIDTH - C.BOARD_WIDTH + C.TRAY_GAP,
					event.pos[1],
				)
				for button in self.clock.buttons.values():
					if button.rect.collidepoint(local_pos) and button.active is not None:   ### specifically "is not None" for turn controls
						button.click()

			# Board
			elif event.pos[0] > C.PANE_WIDTH:
				self.board.handle_click(*self.gridify(event.pos))

				### collapse dropdowns
				if event.pos[0] > C.PANE_WIDTH:
					for context in self.contexts:
						for button in context.buttons.values():
							if button.dropdown:
								button.active = False

			# Pane
			else:
				### CONTEXT
				for context in self.contexts:
					if context.show:
						context.handle_click(event)
						break

				### NO CONTEXT
				else:
					# Buttons
					for button in self.buttons.values():
						if button.rect.collidepoint(event.pos):
							button.click()

						elif button.dropdown:
							### dropdown always renders in mainpane
							for option in button.dropdown:
								if option.rect.collidepoint(event.pos):
									option.click()

		# Annotations
		elif event.type in (pygame.MOUSEBUTTONDOWN,pygame.MOUSEBUTTONUP) and event.button == 3:
			f,r = self.gridify(event.pos)
			for coord in (f,r):
				if coord < 1 or coord > 8:
					return

			### anchor down
			if event.type == pygame.MOUSEBUTTONDOWN:
				self.anchor = self.board.tile(f,r)

			### anchor up
			elif event.type == pygame.MOUSEBUTTONUP and self.anchor:
				if self.anchor is (header := self.board.tile(f,r)):
					if self.anchor in self.board.this_move.lights:
						self.board.this_move.lights.remove(self.anchor)
					else:
						self.board.this_move.lights.append(self.anchor)
				else:
					for arrow in self.board.this_move.quiver:
						if all([
							arrow.base is self.anchor,
							arrow.roof is header
						]):
							self.board.this_move.quiver.remove(arrow)
							break
					else:
						self.board.this_move.quiver.append(
							Arrow(
								self,
								self.anchor,
								header
							)
						)

		# Reader
		elif event.type == pygame.MOUSEWHEEL:
			self.reader.scroll(event.y)

		# Writers
		elif event.type == pygame.KEYDOWN:
			for context in self.contexts:
				if context.show:
					for writer in context.writers.values():
						if writer.active:
							if event.key == pygame.K_BACKSPACE:
								if writer.field:
									writer.field = writer.field[:-1]
								else:
									writer.active = False
							else:
								writer.field += event.unicode

		# Sliders
		if (
			event.type == pygame.MOUSEMOTION and event.buttons[0]
		) or (
			event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
		):
			for slider in Slider.all:
				if slider.trigger.active and slider.rect.collidepoint(event.pos):
					slider.hold(event.pos)


	# TODO: HANDLE END OF GAME
	def is_game_over(self):
		# Stats
		if self.board.rulecount_threereps >= 3:
			print("draw by repetition!")
			return True
		if self.board.rulecount_fiftymoves > 99:
			print("draw by boredom!")
			return True

		# Calculations
		whites = [man.creed for man in self.board.all_men("w")]
		blacks = [man.creed for man in self.board.all_men("b")]

		if len(whites) > 2 or len(blacks) > 2:
			return self.board.is_in_checkmate()

		if any([
			set(whites) == {"K"} and not all([
				set(blacks) - {"K"},
				set(blacks) - {"K","B"},
				set(blacks) - {"K","N"}
			]),
			set(blacks) == {"K"} and not all([
				set(whites) - {"K"},
				set(whites) - {"K","B"},
				set(whites) - {"K","N"}
			]),
		]):
			self.board.outcome = (
				"Draw",
				"Insufficient material"
			)
			return True


	# TODO: OVERHAUL I/O
	def export_FEN(self):
		# Board
		fen_board = ''
		for r in range(8):
			r = 8 - r

			empties = 0
			for f in range(8):
				f = 1 + f

				tile = self.board.tile(f,r)
				if tile.occupant:
					if empties:
						fen_board += str(empties)
						empties = 0

					if tile.occupant.colour == "w":
						fen_board += tile.occupant.creed.upper() or "P"
					else:
						fen_board += tile.occupant.creed.lower() or "p"
				else:
					empties += 1

			if empties:
				fen_board += str(empties)

			if r > 1:
				fen_board += "/"

		# Configuration
		fen_config = []

		### active colour (colour to move)
		fen_config.append(self.board.ply)

		### castlability
		castlability = ''
		for king in self.board.all_men(creed="K"):
			if not king.has_moved and king.position in ((5,1),(5,8)):
				for rook in self.board.all_men(colour=king.colour, creed="R"):
					if not rook.has_moved and rook.position in (
							(1,1), (8,1) if rook.colour == "w" else (8, 1), (8, 8)
					):
						can_castle = "K" if rook.f > king.f else "Q"
						castlability += {
							"w" : can_castle.upper(),
							"b" : can_castle.lower()
						}[king.colour]

		fen_config.append("".join(sorted(castlability)) if castlability else "-")

		### en passant availability
		epability = None
		for pawn in self.board.all_men(creed=""):
			if pawn.just_moved_double:
				epability = C.FILES[pawn.f] + str(pawn.r-1 if pawn.colour == "w" else pawn.r + 1)

		fen_config.append(epability or "-")

		### fifty move rule clock...	must compute before turnover
		fen_config.append(str(self.board.rulecount_fiftymoves))

		### fullmove clock
		fen_config.append(str(self.board.movenum))


		fen_config = " ".join(fen_config)

		fen = fen_board + " " + fen_config

		return fen


	def export_PGN(self):
		import re

		# Seven Tag Roster:
		# 1) Event
		# 2) Site
		# 3) Date
		# 4) Round
		# 5) White
		# 6) Black
		# 7) Result

		pgn = []
		### multiline movetext (up to 999 turns):
		for t,turn in enumerate(re.split(r"\d{1,3}\." , self.reader.movetext)):
			if not t: continue
			pgn.append("\n" + str(t) + ". " + turn.strip())

		return pgn


	def import_FEN(self , fen_raw):
		fen = fen_raw.split()

		# Board
		self.board.agent = None
		self.board.compose(
			self.blueprint(fen[0])
		)

		# Configuration
		### active colour
		self.board.ply = fen[1]

		### castlability
		castlability = fen[2]
		for side in {"K","Q","k","q"} - set(castlability):
			corner = self.board.tile(
				1 if side.upper() == "Q" else 8,
				1 if side.isupper() else 8
			)

			if corner.occupant and corner.occupant.creed == "R":
				corner.occupant.has_moved = True

		### en passant availability
		ep_tgt = fen[3]
		if ep_tgt.isalnum():
			ep_target = self.board.tile(
				C.FILES.index(ep_tgt[-2]),
				int(ep_tgt[-1]) + (1 if self.board.ply == "b" else -1)
			)
			if pawn := ep_target.occupant:
				pawn.just_moved_double = True

		### halfmove capture clock
		self.board.rulecount_fiftymoves = int(fen[4])

		### fullmove clock
		self.board.movenum = int(fen[5])

		# Other
		### halfmoves
		# #####   last term accounts for FENs imported at black's turn; without it, turn controls loop.
		# self.board.halfmovenum = 2*self.board.movenum - (self.board.ply == "w")

		### pawn double moves
		for pawn in self.board.all_men(creed=""):
			if (
					pawn.colour == "w"
					and
					pawn.r != 2
			) or (
					pawn.colour == "b"
					and
					pawn.r != 7
			):
				pawn.has_moved = True


	def import_PGN(self , filename , multiline=True):
		import re

		with open(filename,"r") as file:
			if multiline:
				for movenum,line in enumerate([line for line in file.readlines() if re.match(r"^\d{1,3}\.",line)]):
					for ply,movetext in enumerate(line.strip().split()[1:]):
						move = Move(self,self.export_FEN())
						self.force_move(
							move.enact(movetext,ply)
						)


	def force_move(self , move , show=True):
		for tile in (move.origin,move.target):
			self.board.handle_click(
				file=tile.f,
				rank=tile.r,
				promo=move.promo,
				show=show
			)

			if show and tile == move.target:
				self.reader.update()
				self.board.render()
				self.render()

			pygame.display.update()

		if show:
			time.sleep(1/8)


	@staticmethod
	def gridify(mouseclick):
		if C.BOARD_FLIPPED:
			return (
				8 - ((mouseclick[0] - C.PANE_WIDTH) // C.TILE_WIDTH),
				1 + (mouseclick[1] // C.TILE_HEIGHT)
			)
		else:
			return (
				1 + ((mouseclick[0] - C.PANE_WIDTH) // C.TILE_WIDTH),
				8 - (mouseclick[1] // C.TILE_HEIGHT)
			)


	@staticmethod
	def blueprint(fenboard):
		model = [[]]
		y = 0
		for char in fenboard:
			if char == "/":
				model.append([])
				y += 1
			else:
				if char.isnumeric():
					model[y].extend(["  "]*int(char))
				else:
					c = "w" if char.isupper() else "b"
					model[y].append(c + char.upper())

		return model
