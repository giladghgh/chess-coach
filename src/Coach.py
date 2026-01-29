import pygame,time

from src.Constants import C,E
from src.Gameplay import Board,Move,Clock
from src.Tile import Tile
from src.Engine import Engine
from src.Contexts import *
from src.Elements import *





class Coach:
	def __init__(self):
		self.screen = pygame.display.set_mode(C.WINDOW_SIZE)

		### cosmetics
		self.icon = pygame.transform.scale(pygame.image.load(C.DIR_MEDIA + "coach_icon.png"),(150,150))
		self.screen.blit(
			self.icon,
			self.icon.get_rect(center=[L/2 for L in C.WINDOW_SIZE])
		)
		pygame.display.update()

		# Faculties
		self.board  = Board(self)
		self.engine = Engine(self)

		# Contexts
		self.settings = Settings(self)
		self.analysis = Analysis(self)
		self.coaching = Coaching(self)
		self.contexts = (
			self.settings,
			self.analysis,
			self.coaching,
		)

		# Interfaces
		self.current_w = pygame.display.Info().current_w

		self.pane = pygame.Surface(C.PANE_SIZE,pygame.SRCALPHA)
		self.tray = pygame.Surface(C.TRAY_SIZE,pygame.SRCALPHA)

		self.font = pygame.font.SysFont("Consolas",14,bold=True)

		### facets
		self.reader    = Reader(self)
		self.gauge     = Gauge(self)
		self.graveyard = Graveyard(self)
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
		self.btn_toggle_tray = ButtonToggleTray(
			self,
			self.tray,
			C.TRAY_GAP + C.GAUGE_WIDTH + C.BUTTON_WIDTH/2,
			C.WINDOW_HEIGHT/2 - C.BUTTON_HEIGHT/2
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
				C.X_MARGIN + 0*(C.BUTTON_WIDTH + C.GRID_GAP),
				C.Y_MARGIN,
				context=self.settings
			),
		}
		self.buttons_turns = {
			"NEXT"  : ButtonTurnNext(
				self,
				self.pane,
				C.X_MARGIN + C.TEXTBOX_WIDTH - C.BUTTON_WIDTH,
				self.reader.rect.bottom + C.GRID_GAP
			),
			"PREV"	: ButtonTurnPrevious(
				self,
				self.pane,
				C.X_MARGIN + C.TEXTBOX_WIDTH - 2*C.BUTTON_WIDTH,
				self.reader.rect.bottom + C.GRID_GAP
			),
			"RESET"	: ButtonBoardReset(
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
		self.buttons = {				        ### right->left (& bottom->top if tight enough) so tooltips aren't obscured
			**self.buttons_nav,
			**self.buttons_turns,
			**self.buttons_bots,
		}

		### audio
		self.audio_game_start  = pygame.mixer.Sound(C.DIR_AUDIO + "game_start.wav")
		self.audio_game_stop   = pygame.mixer.Sound(C.DIR_AUDIO + "game_stop.wav")
		self.audio_drill_start = pygame.mixer.Sound(C.DIR_AUDIO + "drill_start.wav")
		self.audio_drill_stop  = pygame.mixer.Sound(C.DIR_AUDIO + "drill_stop.wav")
		self.settings.buttons_ui["VOLUME"].apply()
		self.audio_game_start.play()

		### cursors
		self.mouse_pos = None

		self.CURSOR_TYPE = pygame.SYSTEM_CURSOR_IBEAM
		self.CURSOR_CALM = pygame.Cursor((5,3),pygame.image.load(C.DIR_CURSORS + "calm_" + self.board.ply + ".png"))
		self.CURSOR_THIS = pygame.Cursor((10,3),pygame.image.load(C.DIR_CURSORS + "this_" + self.board.ply + ".png"))
		self.CURSOR_PALM = pygame.Cursor((10,10),pygame.image.load(C.DIR_CURSORS + "palm_" + self.board.ply + ".png"))
		self.CURSOR_FIST = pygame.Cursor((10,10),pygame.image.load(C.DIR_CURSORS + "fist_" + self.board.ply + ".png"))
		self.CURSOR_DENY = pygame.Cursor((10,10),pygame.image.load(C.DIR_CURSORS + "deny_" + self.board.ply + ".png"))
		self.CURSOR_MOVE = pygame.Cursor((5,15),pygame.image.load(C.DIR_CURSORS + "move_" + self.board.ply + ".png"))
		self.CURSOR_HOLD = pygame.Cursor((5,15),pygame.image.load(C.DIR_CURSORS + "hold_" + self.board.ply + ".png"))

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

		# Commence
		self.exclude()
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
		pygame.mouse.set_cursor(self.CURSOR_CALM)

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

		hovering = None

		# Board
		if h := self.board.render():
			hovering = h

		# Pane
		### CONTEXT
		if any(cntxt.show for cntxt in self.contexts):
			### tabs
			begin = [
				( 2*C.X_MARGIN + C.TEXTBOX_WIDTH + C.GRID_GAP , 0 ),
				( 2*C.X_MARGIN + C.TEXTBOX_WIDTH + C.GRID_GAP + 10 , 0.1*C.TILE_HEIGHT ),
				( 2*C.X_MARGIN + C.TEXTBOX_WIDTH + C.GRID_GAP + 10 , 0.9*C.TILE_HEIGHT ),
				( 2*C.X_MARGIN + C.TEXTBOX_WIDTH + C.GRID_GAP , C.TILE_HEIGHT ),
			]

			for c,context in sorted( enumerate(self.contexts) , key=lambda cc:cc[1].show ):
				if context.show:
					if h := context.render():
						hovering = h

					### manila folder tabs
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

				### manila folder background
				pygame.draw.polygon(
					self.screen,
					context.colour,
					[ (b[0]+s[0] , b[1]+s[1]) for b,s in zip(begin,shift) ]
				)

		### NO CONTEXT
		else:
			### pane
			self.pane.fill((0,0,0,0))
			self.pane.fill(C.BACKGR_PANE , (0,0,C.PANE_WIDTH,C.PANE_HEIGHT))

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
				### ### button
				if button.active is not None and button.rect.collidepoint(self.mouse_pos):
					hovering = button
				else:
					button.paint()

				### ### dropdown
				if button.dropdown and (button.dropdown.persist or button.active):
					for option in button.dropdown:
						if option.active is not None and option.rect.collidepoint(self.mouse_pos):
							hovering = option
						else:
							option.paint()

				### ### slider
				if hasattr(button,"slider"):
					if button.active and button.slider.rect.collidepoint(self.mouse_pos):
						hovering = button.slider

			self.screen.blit(self.pane,(0,0))

		# Tray
		self.tray.fill((0,0,0,0))
		self.tray.fill(C.BACKGR_SHELF , (C.TRAY_GAP + C.GAUGE_WIDTH + C.GRAVE_WIDTH,0,C.SHELF_WIDTH,C.SHELF_HEIGHT))
		self.tray.fill(C.BACKGR_GRAVE , (C.TRAY_GAP,0,C.GAUGE_WIDTH + C.GRAVE_WIDTH,C.GRAVE_HEIGHT))

		for element in [
			self.clock,
			self.graveyard,
			self.gauge,
			self.btn_toggle_tray,
		]:
			if h := element.render():
				hovering = h

		self.screen.blit(self.tray , (C.PANE_WIDTH + C.BOARD_WIDTH - C.TRAY_GAP,0))

		# Hover action
		if hovering:
			hover_type = type(hovering)

			if issubclass(hover_type,Button) and hover_type is not ButtonBot:
				try:
					pygame.mouse.set_cursor(self.CURSOR_THIS)
				except pygame.error as e:
					print("ERROR:\t",e)                         ### WHY DOES THIS HAPPEN
			elif hover_type is Writer:
				pygame.mouse.set_cursor(self.CURSOR_TYPE)
			elif hover_type is Slider:
				pygame.mouse.set_cursor(self.CURSOR_FIST if pygame.mouse.get_pressed()[0] else self.CURSOR_PALM)
			elif hover_type is Tile:
				if hovering.occupant and (hovering.occupant.colour == self.board.ply):
					pygame.mouse.set_cursor(self.CURSOR_HOLD if self.board.agent else self.CURSOR_MOVE)
				else:
					try:
						pygame.mouse.set_cursor(self.CURSOR_HOLD if self.board.agent else self.CURSOR_DENY)
					except pygame.error as e:
						print("ERROR:\t",e)                     ### WHY DOES THIS HAPPEN

			if hasattr(hovering,"active"):
				if hovering.active is False:
					if hover_type is ButtonContextOpen:
						hovering.colour = hovering.context.colour
					elif hover_type is Writer:
						hovering.colour = C.TEXTBOX_LOOM
					elif not str(hovering).endswith("Exit"):
						hovering.colour = C.BUTTON_LOOM
		else:
			pygame.mouse.set_cursor(self.CURSOR_CALM)


		#####   #   LINE   #   #####
		# x = C.PANE_WIDTH + C.BOARD_WIDTH + C.GAUGE_WIDTH + C.GRAVE_WIDTH + C.SHELF_WIDTH/2
		# pygame.draw.line(self.screen,(0,0,0),(x,0),(x,C.WINDOW_HEIGHT),width=1)
		#
		# x2 = C.PANE_WIDTH + C.BOARD_WIDTH + C.GAUGE_WIDTH + C.GRAVE_WIDTH
		# pygame.draw.line(self.screen,(0,0,0),(x2,0),(x2,C.WINDOW_HEIGHT),width=1)
		####### # ######## # #######


	def handle_click(self , event):
		# Left click
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			clicks = []

			# Tray
			if event.pos[0] > C.PANE_WIDTH + C.BOARD_WIDTH:
				local_pos = (
					event.pos[0] - C.TRAY_OFFSET,
					event.pos[1],
				)
				### open/shut
				if self.btn_toggle_tray.rect.collidepoint(local_pos):
					clicks.append(self.btn_toggle_tray)

				### clock
				for button in self.clock.buttons.values():
					if button.rect.collidepoint(local_pos) and button.active is not None:   ### /None/ disables button
						clicks.append(button)

			# Board
			elif event.pos[0] > C.PANE_WIDTH:
				self.board.handle_click(*self.board.gridify(event.pos))

			# Pane
			else:
				### CONTEXT
				for context in self.contexts:
					if context.show:
						clicks.extend( context.handle_click(event) )
						break

				### NO CONTEXT
				else:
					# Buttons
					for button in self.buttons.values():
						if button.rect.collidepoint(event.pos):
							clicks.append(button)

						elif button.dropdown and (button.dropdown.persist or button.active):
							for option in button.dropdown:
								if option.active is not None and option.rect.collidepoint(event.pos):
									clicks.append(option)

			### only click topmost button:
			if clicks:
				clicks[-1].click()


		# Annotations
		elif event.type in (pygame.MOUSEBUTTONDOWN,pygame.MOUSEBUTTONUP) and event.button == 3:
			f,r = self.board.gridify(event.pos)
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
								header,
								C.ARROW_COACH_COLOUR
							)
						)

		# Readers (scroll)
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

		# Sliders
		if (
			event.type == pygame.MOUSEMOTION and event.buttons[0]
		) or (
			event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
		):
			for slider in Slider.all:
				if slider.trigger.active and slider.rect.collidepoint(event.pos):
					slider.hold(event.pos)


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
				for rook in self.board.all_men(colour=king.colour , creed="R"):
					if not rook.has_moved and rook.position in (
							((1,1),(8,1)) if rook.colour == "w" else ((1,8),(8,8))
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
		fen_config.append(str(self.board.rulecount_fiftymovs))

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
			if not t:
				continue

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
				int(ep_tgt[-1]) + (-1,1)[self.board.ply == "b"]
			)
			if pawn := ep_target.occupant:
				pawn.just_moved_double = True

		### halfmove capture clock
		self.board.rulecount_fiftymovs = int(fen[4])

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


	def exclude(self):
		for code in E.BOT_EXCLUDE:
			### engine
			del self.engine.bots[code]

			### bot option
			for option in (
				*self.buttons["BOT_WHITE"].dropdown,
				*self.buttons["BOT_BLACK"].dropdown,
				*self.analysis.buttons["BOT_WHITE"].dropdown,
				*self.analysis.buttons["BOT_BLACK"].dropdown,
			):
				if code == option.doctrine.code:
					option.active = None

			### gauge
			del self.analysis.counters["EVAL_"+code]
			del self.analysis.buttons["GAUGE_"+code]


	def wrap(self):
		# Banner
		who = self.board.outcome[0]
		how = self.board.outcome[1]
		print("###- GAME OVER -###")
		if who == "Draw":
			print(who + " by " + how.lower() + "!")
		else:
			print(who + " wins by " + how.lower() + "!")
		print("####-####-####-####")

		# Audio
		match who:
			case "Draw":
				self.audio_game_stop.play()
			case _:
				match how:
					case "Checkmate":
						self.audio_game_stop.play()
					case "Resignation":
						self.audio_game_stop.play()
					case "Timeout":
						self.audio_game_stop.play()

		# Freeze
		self.board.ply = None

		# Topple the king
		corpse = self.board.all_men(
			colour=("w","b")[who == "White"],
			creed="K"
		)[0]
		corpse.image = pygame.transform.rotate(corpse.image,90)


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
