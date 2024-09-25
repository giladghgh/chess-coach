import pygame,time

from src.Constants import C
from src.Gameplay import Board,Move,Clock
from src.Engine import Engine
from src.Context import *
from src.Element import *





class Coach:
	def __init__(self):
		self.screen = pygame.display.set_mode(C.WINDOW_SIZE)

		pygame.time.set_timer(pygame.USEREVENT,1000)

		# Faculties
		self.board  = Board(self)
		self.engine = Engine(self)
		self.reader = Reader(self)

		# Contexts
		self.settings = Settings(self)
		self.analysis = Analysis(self)
		self.tutorial = Tutorial(self)
		self.contexts = [
			self.settings,
			self.analysis,
			self.tutorial,
		]

		# Interface
		self.font = pygame.font.SysFont("Consolas",14,bold=True)
		self.pane = pygame.Surface(C.PANE_SIZE,pygame.SRCALPHA)
		self.tray = pygame.Surface(C.TRAY_SIZE,pygame.SRCALPHA)

		### amenities
		self.graveyard = Graveyard(self)    ### a moment of silence please
		self.anchor    = None               ### annotations
		self.clock     = Clock(self)        ### timekeeping

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
			"TUTORIAL"  : ButtonContextOpen(
				self.pane,
				C.X_MARGIN + 2*(C.BUTTON_WIDTH + C.GRID_GAP),
				C.Y_MARGIN,
				context=self.tutorial,
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
		self.buttons_reader = {
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
		self.buttons = {				##### right->left (+ bottom->top if too near) so tooltips aren't obscured.
			**self.contexts_menu,
			**self.buttons_reader,
			**self.buttons_bots,
		}

		# Assemble!
		self.import_FEN(C.INIT_FEN)		### assembling on black's turn may cause movelog issues... button import instead
		self.tutorial.plug_in()
		self.analysis.plug_in()
		self.settings.plug_in()

		print(self.analysis.buttons)


	def reset(self , fen=C.INIT_FEN):
		# Mechanics
		self.board.__init__(self)
		self.import_FEN(fen)

		self.board.last_move = None
		self.board.this_move = Move(self.board,fen)
		self.board.movelog   = [self.board.this_move,]

		### ply agnostic
		if self.board.ply == "b":
			self.reader.halfmove_offset = True
		### movenum agnostic
		if self.board.movenum > 1:
			self.reader.fullmove_offset = self.board.movenum

		# Clock
		self.clock.reset()

		# Calibrate
		self.board.calibrate()


	def render(self):
		# Sidebar
		### CONTEXT
		for context in self.contexts:
			if context.show:
				context.render()
				break

		### NO CONTEXT
		else:
			# Pane
			self.pane.fill((0,0,0,0))
			self.pane.fill(C.BACKGR_PANE , (0,0,C.SIDEBAR_WIDTH,C.BOARD_HEIGHT))

			### elements
			for element in (
				self.reader,
				*self.buttons.values(),
			):
				element.render()

			### banners
			for subtitle,banner in self.banners.items():
				prose = self.font.render(subtitle,True,C.BUTTON_DEAD)
				pygame.draw.rect(
					self.pane,
					(110,110,110),
					banner
				)
				self.pane.blit(prose , prose.get_rect(center=banner.center))


			self.screen.blit(self.pane,(0,0))

		################### BEAMS ##################
		# x0 = pygame.mouse.get_pressed()[0]
		# pygame.draw.line(
		# 	self.screen,(0,0,0),(x0,0),(x0,C.BOARD_HEIGHT),
		# )
		# x1 = C.X_MARGIN
		# pygame.draw.line(
		# 	self.screen,(0,0,0),(x1,0),(x1,C.BOARD_HEIGHT),
		# )
		# x2 = C.X_MARGIN + 0.1*C.BUTTON_WIDTH
		# pygame.draw.line(
		# 	self.screen,(0,0,0),(x2,0),(x2,C.BOARD_HEIGHT),
		# )
		# y1 = C.Y_MARGIN
		# pygame.draw.line(
		# 	self.screen,(0,0,0),(0,y1),(C.SIDEBAR_WIDTH,y1),
		# )
		# y2 = C.Y_MARGIN + 0.1*C.BUTTON_HEIGHT
		# pygame.draw.line(
		# 	self.screen,(0,0,0),(0,y2),(C.SIDEBAR_WIDTH,y2),
		# )
		###########################################

		# Tray
		if self.tray:
			self.tray.fill((0,0,0,0))
			self.tray.fill(C.BACKGR_TRAY , (C.TRAY_PAD,0,C.TRAY_WIDTH,C.BOARD_HEIGHT))

			### clock
			self.clock.render()

			### graveyard
			self.graveyard.render()


			self.screen.blit(self.tray , (C.PANE_WIDTH + C.BOARD_WIDTH - C.TRAY_PAD,0))



	def handle_click(self , event):
		# Left click
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			# Tray
			if event.pos[0] > C.SIDEBAR_WIDTH + C.BOARD_WIDTH:
				if self.tray:
					local_pos = (
						event.pos[0] - C.SIDEBAR_WIDTH - C.BOARD_WIDTH,
						event.pos[1],
					)
					for button in self.clock.buttons:
						if button.rect.collidepoint(local_pos):
							button.click()

			# Board
			elif event.pos[0] > C.SIDEBAR_WIDTH:
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
					### bot options
					for bot in self.buttons_bots.values():
						for option in bot.options:
							if option.rect.collidepoint(event.pos):
								option.click()

		# Annotations
		elif event.type in (pygame.MOUSEBUTTONDOWN,pygame.MOUSEBUTTONUP) and event.button == 3:
			f,r = self.gridify(event.pos)

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
							return

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
				for rook in self.board.all_men(colour=king.colour,creed="R"):
					if not rook.has_moved and rook.position in (
							(1,1),(8,1) if rook.colour == "w" else (8,1),(8,8)
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
				epability = C.FILES[pawn.f] + str(pawn.r-1 if pawn.colour == "w" else pawn.r+1)

		fen_config.append(epability or "-")

		### fifty move rule clock...	must compute before turnover
		fen_config.append(str(self.board.rulecount_fiftymoves))

		### fullmove clock
		fen_config.append(str(self.board.movenum))


		fen_config = " ".join(fen_config)

		fen = fen_board + " " + fen_config

		return fen


	def import_PGN(self , filename , multiline=True):
		import re

		with open(filename,"r") as file:
			if multiline:
				for movenum,line in enumerate([line for line in file.readlines() if re.match(r"^\d{1,3}\.",line)]):
					for ply,movetext in enumerate(line.strip().split()[1:]):
						self.force_move(
							self.PGN_to_move(ply,movetext)
						)


	def import_FEN(self , fen_raw):
		fen = fen_raw.split()

		# Board
		self.board.agent = None
		self.board.compose(
			shell=self.FEN_to_model(fen[0])
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
		ep_square = fen[3]
		if ep_square.isalnum():
			self.board.tile(
				C.FILES.index(ep_square[-2]),
				int(ep_square[-1]) + (1 if self.board.ply == "b" else -1)
			).occupant.just_moved_double = True

		### halfmove capture clock
		self.board.rulecount_fiftymoves = int(fen[4])

		### fullmove clock
		self.board.movenum = int(fen[5])

		# Other
		### halfmoves
		# #####   last term accounts for FENs imported at black's turn; without it, prev/next buttons loop.
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


	def PGN_to_move(self , ply , movetextraw):
		if "..." in movetextraw:
			return None

		move = Move(self.board)
		move.forced = True
		move.text 	= movetextraw

		# Standard Algebraic Notation
		san = movetextraw

		if movetextraw.count("#"):
			san = san.replace("#","")
			move.in_checkmate = True
		elif movetextraw.count("+"):
			san = san.replace("+","")
			move.in_check = True

		if movetextraw.count("x"):
			san = san.replace("x","")
			move.capture = True

		elif "=" in san:
			# axb8=R
			move.origin = self.board.tile(
				C.FILES.index(san[0]),
				2 if ply else 7
			)
			move.target = self.board.tile(
				C.FILES.index(san[-4]),
				1 if ply else 8
			)

			move.promo = san[-1]

		elif "-" in san:
			# O-O-O
			# O-O
			move.origin = self.board.tile(
				5,
				8 if ply else 1
			)
			move.target = self.board.tile(
				7 if san.count("-") == 1 else 3,
				8 if ply else 1
			)

		elif san.isalnum():
			# b4
			# Nf7
			# exd6
			# Raxb8
			# Qh4xe1
			move.target = self.board.tile(
				C.FILES.index(san[-2]),
				int(san[-1])
			)

			attackers = self.board.all_threats(
				move.target,
				colour="b" if ply else "w",
				creed=san[0] if san[0].isupper() else ""
			)

			if len(attackers) == 1:
				move.origin = self.board.tile(*attackers[0].position)
			else:
				# Disambiguation
				clue = "".join([char for char in san[:-2] if char.islower() or char.isnumeric()])
				print("clue:" , clue , [a.pgn for a in attackers])
				for opp in attackers:
					if clue in opp.pgn:
						print(opp.pgn)
						move.origin = self.board.tile(*opp.position)

		else:
			print(movetextraw , san)
			raise Exception("Imported PGN move not recognised!")

		return move


	@staticmethod
	def gridify(mouseclick):
		if C.BOARD_FLIPPED:
			return (
				8 - ((mouseclick[0] - C.SIDEBAR_WIDTH) // C.TILE_WIDTH),
				1 + (mouseclick[1] // C.TILE_HEIGHT)
			)
		else:
			return (
				1 + ((mouseclick[0] - C.SIDEBAR_WIDTH) // C.TILE_WIDTH),
				8 - (mouseclick[1] // C.TILE_HEIGHT)
			)


	@staticmethod
	def FEN_to_model(fenboard):
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
