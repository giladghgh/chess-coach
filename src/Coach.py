import pygame,time

from src.Constants import C
from src.Gameplay import Board,Move,Clock
from src.Tile import Tile
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
			self,
			self.pane,
			C.X_MARGIN + C.TEXTBOX_WIDTH - C.BUTTON_WIDTH/2,
			C.Y_MARGIN
		)
		self.buttons_nav = {
			"COACHING"  : ButtonContextOpen(
				self,
				self.pane,
				C.X_MARGIN + 2*(C.BUTTON_WIDTH + C.GRID_GAP),
				C.Y_MARGIN,
				context=self.coaching
			),
			"ANALYSIS"  : ButtonContextOpen(
				self,
				self.pane,
				C.X_MARGIN + 1*(C.BUTTON_WIDTH + C.GRID_GAP),
				C.Y_MARGIN,
				context=self.analysis
			),
			"SETTINGS"  : ButtonContextOpen(
				self,
				self.pane,
				C.X_MARGIN,
				C.Y_MARGIN,
				context=self.settings
			),
		}
		self.buttons_turns = {
			"NEXT"  : ButtonNext(
				self,
				self.pane,
				C.X_MARGIN + C.TEXTBOX_WIDTH - C.BUTTON_WIDTH,
				self.reader.rect.bottom + C.GRID_GAP
			),
			"PREV"	: ButtonPrevious(
				self,
				self.pane,
				C.X_MARGIN + C.TEXTBOX_WIDTH - 2*C.BUTTON_WIDTH,
				self.reader.rect.bottom + C.GRID_GAP
			),
			"RESET"	: ButtonReset(
				self,
				self.pane,
				C.X_MARGIN + C.TEXTBOX_WIDTH - 3*C.BUTTON_WIDTH,
				self.reader.rect.bottom + C.GRID_GAP
			),
			"ECOInterpreter": ButtonECOInterpreter(
				self,
				self.pane,
				C.X_MARGIN,
				self.reader.rect.bottom + C.GRID_GAP
			),
		}
		self.buttons_bots = {
			"BOT_BLACK"	: ButtonBot(
				self,
				self.pane,
				C.X_MARGIN,
				self.banners["BOTS"].bottom + C.GRID_GAP,
				player="BLACK"
			),
			"BOT_WHITE"	: ButtonBot(
				self,
				self.pane,
				C.X_MARGIN,
				self.banners["BOTS"].bottom + 2*C.BUTTON_HEIGHT + 3*C.GRID_GAP,
				player="WHITE"
			),
		}
		self.buttons = {				### right->left (& bottom->top if tight enough) so tooltips aren't obscured
			**self.buttons_nav,
			**self.buttons_turns,
			**self.buttons_bots,
		}

		### sounds
		self.sound_game_start = pygame.mixer.Sound(C.DIR_SOUNDS + "\\game_start.wav")
		self.sound_game_end   = pygame.mixer.Sound(C.DIR_SOUNDS + "\\game_end.wav")

		self.sound_game_start.play()

		### mouse
		self.mouse_pos = None
		self.hovering  = None

		### file i/o
		self.tags = {tag : self.settings.writers[tag.upper()].pretext for tag in (
			"Event",
			"Site",
			"Date",
			"Round",
			"White",
			"Black",
			"Mode",                 ### Result handled automatically. Mode included cos why not.
		)}

		# Assemble!
		### visuals
		self.screen.fill([(L+D)/2 for L,D in zip(C.BOARD_STYLE[0],C.BOARD_STYLE[2])])
		self.pane.fill(C.BACKGR_PANE)
		self.tray.fill(C.BACKGR_TRAY)
		self.screen.blits([
			(self.pane , (0,0)),
			(self.tray , (C.PANE_WIDTH + C.BOARD_WIDTH,0))
		])
		pygame.display.update()

		### mechanics
		time.sleep(1/5)             ### pause for effect
		self.reset()
		for context in reversed(self.contexts):     ### plug in AFTER declaring contexts. Reversed for tooltip exposure.
			context.plug_in()


	def reset(self , fen=C.INIT_FEN):
		self.board.__init__(self)
		self.import_FEN(fen)

		self.board.last_move = None
		self.board.this_move = Move(self.board,fen)
		self.board.movelog   = [self.board.this_move,]

		self.mouse_pos = pygame.mouse.get_pos()
		pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

		# For imports:
		### ply agnostic
		if self.board.ply == "b":
			self.reader.halfmove_offset = True
		### movenum agnostic
		self.reader.fullmove_offset = self.board.movenum

		# Calibrate
		self.board.calibrate()

		### clock
		self.clock.reset()


	def render(self):
		self.mouse_pos = pygame.mouse.get_pos()
		self.hovering  = None

		for tile in self.board.all_tiles:
			if tile.occupant and tile.occupant.colour == self.board.ply and tile.rect.collidepoint(self.mouse_pos):
				self.hovering = tile

		# Tray
		if self.tray:
			self.tray.fill((0,0,0,0))
			self.tray.fill(C.BACKGR_TRAY , (C.TRAY_GAP,0,C.TRAY_WIDTH,C.BOARD_HEIGHT))

			### clock
			for button in self.clock.buttons.values():
				button.render()

				if button.active is not None and button.rect.collidepoint((
					self.mouse_pos[0] + C.TRAY_GAP - C.PANE_WIDTH - C.BOARD_WIDTH,
					self.mouse_pos[1],
				)):
					self.hovering = button
				else:
					button.paint()

			### graveyard
			self.graveyard.render()

			self.screen.blit(self.tray , (C.PANE_WIDTH + C.BOARD_WIDTH - C.TRAY_GAP,0))


		# Sidebar
		### CONTEXT
		if any(cntxt.show for cntxt in self.contexts):
			### tabs
			begin = [
				( 2*C.X_MARGIN + C.TEXTBOX_WIDTH + C.GRID_GAP , 0 ),
				( 2*C.X_MARGIN + C.TEXTBOX_WIDTH + C.GRID_GAP + 10 , 0.1*C.TILE_HEIGHT ),
				( 2*C.X_MARGIN + C.TEXTBOX_WIDTH + C.GRID_GAP + 10 , 0.9*C.TILE_HEIGHT ),
				( 2*C.X_MARGIN + C.TEXTBOX_WIDTH + C.GRID_GAP , C.TILE_HEIGHT ),
			]

			for c,context in sorted( enumerate(self.contexts) , key=lambda _:_[1].show ):
				if context.show:
					context.render()

					if h := context.hovering:       ### /hovering/ never redefined to /None/ as that would discard tray hovers
						self.hovering = h

					shift = [
						(0 , c*0.9*C.TILE_HEIGHT),
						(8 , c*0.9*C.TILE_HEIGHT),
						(8 , c*0.9*C.TILE_HEIGHT),
						(0 , c*0.9*C.TILE_HEIGHT),
					]

				else:
					shift = [
						(0 , c*0.9*C.TILE_HEIGHT),
						(0 , c*0.9*C.TILE_HEIGHT),
						(0 , c*0.9*C.TILE_HEIGHT),
						(0 , c*0.9*C.TILE_HEIGHT),
					]

				points = []
				for b,s in zip(begin,shift):
					points.append(
						(b[0]+s[0] , b[1]+s[1])
					)

				pygame.draw.polygon(
					self.screen,
					context.colour,
					points
				)

		### NO CONTEXT
		else:
			### pane
			self.pane.fill((0,0,0,0))
			self.pane.fill(C.BACKGR_PANE , (0,0,C.PANE_WIDTH,C.BOARD_HEIGHT))

			### banners
			for subtitle,banner in self.banners.items():
				prose = self.font.render(subtitle,True,C.BUTTON_IDLE)
				pygame.draw.rect(
					self.pane,
					(110,110,110),
					banner
				)
				self.pane.blit(prose , prose.get_rect(center=banner.center))

			### reader
			self.reader.render()

			### buttons
			for button in self.buttons.values():
				button.render()

				### hover mechanics
				if button.dropdown:
					for option in button.dropdown:
						if option.active is not None and option.rect.collidepoint(self.mouse_pos):
							self.hovering = option
						else:
							option.paint()
				else:
					if button.active is not None and button.rect.collidepoint(self.mouse_pos):
						self.hovering = button
					else:
						button.paint()

			self.screen.blit(self.pane,(0,0))

		### de-hover
		if self.hovering:
			if issubclass(type(self.hovering) , Button):
				pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
			elif type(self.hovering) is Writer:
				pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
			elif type(self.hovering) is Tile:
				pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
				return

			if self.hovering.active is False:
				if type(self.hovering) is ButtonContextOpen:
					self.hovering.colour = self.hovering.context.colour
				elif not str(self.hovering).endswith("Exit"):
					self.hovering.colour = C.BUTTON_LOOM
		else:
			pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)


	def handle_click(self , event):
		# Left click
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			hits = []

			# Tray
			if event.pos[0] > C.PANE_WIDTH + C.BOARD_WIDTH:
				local_pos = (
					event.pos[0] - C.PANE_WIDTH - C.BOARD_WIDTH + C.TRAY_GAP,
					event.pos[1],
				)
				for button in self.clock.buttons.values():
					if button.rect.collidepoint(local_pos) and button.active is not None:   ### /None/ used to disable buttons
						hits.append(button)

			# Board
			elif event.pos[0] > C.PANE_WIDTH:
				self.board.handle_click(*self.gridify(event.pos))

			# Pane
			else:
				### CONTEXT
				for context in self.contexts:
					if context.show:
						hits.extend( context.handle_click(event) )
						break

				### NO CONTEXT
				else:
					# Buttons
					for button in self.buttons.values():
						if button.rect.collidepoint(event.pos):
							hits.append(button)

						elif button.dropdown and (button.dropdown.persist or button.active):
							for option in button.dropdown:                  ### bot dropdowns always clickable
								if option.rect.collidepoint(event.pos):
									hits.append(option)

			### only click top-layer button:
			if hits:
				hits[-1].click()
			### tidy on quiet clicks:
			else:
				for context in self.contexts:
					if context.show:
						context.tidy()

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

		# Reader (scroll)
		elif event.type == pygame.MOUSEWHEEL:
			self.reader.scroll(event.y)

		elif event.type == pygame.KEYDOWN:
			# Writers
			### file i/o
			if self.settings.show:
				for writer in self.settings.writers.values():
					if writer.active:
						writer.type(event)
						break

			### clock controls
			# elif self.tray:
			# 	for control in (self.clock.whiteface.dropdown,self.clock.blackface.dropdown):
			# 		if type(control) is Writer:

			# Navigators
			else:
				### port
				if event.key == pygame.K_a:
					for c,context in enumerate(self.contexts):
						if context.show:
							context.show = False
							if c:
								self.contexts[c-1].show = True
							break
					else:
						self.contexts[-1].show = True

				### starboard
				elif event.key == pygame.K_d:
					for c,context in enumerate(self.contexts):
						if context.show:
							context.show = False
							if len(self.contexts) - c - 1:
								self.contexts[c+1].show = True
							break
					else:
						self.contexts[0].show = True

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
			print("Draw by repetition!")
			return True
		if self.board.rulecount_fiftymoves > 99:
			print("Draw by boredom!")
			return True

		# Calculations
		whites = [man.creed for man in self.board.all_men("w")]
		blacks = [man.creed for man in self.board.all_men("b")]

		if len(whites) > 2 or len(blacks) > 2:
			if self.board.is_in_checkmate():
				self.sound_game_end.play()
				return True

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
		# incremented in prev/next buttons

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


	def import_PGN(self , filename):
		import re

		with open(filename,"r") as file:
			for line in file.readlines():
				# Tags
				if pair := re.match( r"^\[(.+) \"(.+)\"\]" , line ):
					tag,val = pair.group(1,2)
					self.tags[tag] = val
					if (TAG := tag.upper()) in self.settings.writers.keys():
						self.settings.writers[TAG].pretext = val

				# Movetext
				elif re.match( r"^\d{1,3}\." , line ):
					for ply,movetext in enumerate( re.split( '[. ]' , line.strip() )[1:] ):     ### first split is movenum, last is newline
						move = Move(self.board , self.export_FEN())
						move.enact(movetext,ply)

						self.force_move(move)


	def force_move(self , move , show=True):
		for tile in (move.origin,move.target):
			self.board.handle_click(
				file=tile.f,
				rank=tile.r,
				promo=move.promo,
				show=show
			)

			if show and tile == move.target:
				self.screen.fill(C.BACKGR_PANE)
				self.reader.update()
				self.board.render()
				self.render()

			pygame.display.update()

		if show:
			time.sleep(0.1)


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
