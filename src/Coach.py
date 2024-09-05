import time

from datetime import datetime

from src.Constants import C
from src.Gameplay import Board,Move
from src.Engine import Engine
from src.Settings import Settings
from src.Analysis import Analysis
from src.Elements import *





class Coach:
	def __init__(self):
		self.display = pygame.display.set_mode(C.WINDOW_SIZE)
		pygame.display.set_caption("Chess Coach")

		# Faculties
		self.board  = Board(self)
		self.engine = Engine(self)

		# Contexts
		self.settings = Settings(self)
		self.analysis = Analysis(self)

		# Reader
		self.reader = Reader(
			self,
			(2/5)*C.BOARD_HEIGHT,
			C.SIDEBAR_Y_MARGIN + C.BUTTON_HEIGHT + C.TEXTBOX_HEIGHT + C.GRID_GAP
		)

		# Interface
		### gameplay
		self.black_first = False
		self.flipped 	 = False

		### annotations
		self.anchor = None

		### fonts
		self.font = pygame.font.SysFont("Consolas", 14, bold=True)

		### writers
		self.writers = {
			"TITLE" : Writer(
				self,
				self.font,
				(20/30)*C.BOARD_HEIGHT,
				'EventTitle'
			),
			"DATE"  : Writer(
				self,
				self.font,
				(21.5/30)*C.BOARD_HEIGHT,
				datetime.today().strftime("%Y-%m-%d")
			),
			"WHITE" : Writer(
				self,
				self.font,
				(23/30)*C.BOARD_HEIGHT,
				'White'
			),
			"BLACK" : Writer(
				self,
				self.font,
				(25/30)*C.BOARD_HEIGHT,
				'Black'
			),
		}

		### buttons
		self.btn_show_settings = ButtonShowSettings(
			self,
			"SHOW_SETTINGS",
			C.SIDEBAR_X_MARGIN,
			C.SIDEBAR_Y_MARGIN
		)
		self.btn_show_analysis = ButtonShowAnalysis(
			self,
			"SHOW_ANALYSIS",
			C.SIDEBAR_X_MARGIN + C.BUTTON_WIDTH + C.GRID_GAP,
			C.SIDEBAR_Y_MARGIN
		)
		self.btn_reset = ButtonReset(
			self,
			"RESET",
			C.SIDEBAR_X_MARGIN,
			C.SIDEBAR_Y_MARGIN + C.BUTTON_HEIGHT + C.TEXTBOX_HEIGHT + (2/5)*C.BOARD_HEIGHT + 2*C.GRID_GAP
		)
		self.btn_prev = ButtonPrevious(
			self,
			"PREVIOUS",
			C.SIDEBAR_X_MARGIN + C.TEXTBOX_WIDTH - 2*C.BUTTON_WIDTH,
			C.SIDEBAR_Y_MARGIN + C.BUTTON_HEIGHT + C.TEXTBOX_HEIGHT + (2/5)*C.BOARD_HEIGHT + 2*C.GRID_GAP
		)
		self.btn_next = ButtonNext(
			self,
			"NEXT",
			C.SIDEBAR_X_MARGIN + C.TEXTBOX_WIDTH - C.BUTTON_WIDTH,
			C.SIDEBAR_Y_MARGIN + C.BUTTON_HEIGHT + C.TEXTBOX_HEIGHT + (2/5)*C.BOARD_HEIGHT + 2*C.GRID_GAP
		)
		self.btn_import = ButtonImport(
			self,
			"IMPORT",
			C.SIDEBAR_X_MARGIN,
			C.BOARD_HEIGHT - 2*C.BUTTON_HEIGHT
		)
		self.btn_export = ButtonExport(
			self,
			"EXPORT",
			C.SIDEBAR_X_MARGIN + C.TEXTBOX_WIDTH - C.BUTTON_WIDTH,
			C.BOARD_HEIGHT - 2*C.BUTTON_HEIGHT
		)
		self.buttons = [                ### ordered such that tooltips aren't obscured
			self.btn_reset,
			self.btn_next,
			self.btn_prev,
			self.btn_show_analysis,
			self.btn_show_settings,
			self.btn_import,
			self.btn_export
		]

		# Assemble
		### board  (assembling on black's turn will cause movelog issues... button import instead)
		self.import_FEN(C.INIT_FEN)


	def reset(self , fen=C.INIT_FEN):
		# Mechanics
		self.board.__init__(self)
		self.import_FEN(fen)

		if self.board.ply == "b":
			self.board.halfmovenum = 1
			self.black_first 	   = True

		# Movetext
		self.reader.update(self.board.movelog)

		# Movelog (as this might be different to C.INIT_FEN)
		self.board.this_move = Move(self.board,fen)
		self.board.movelog = [self.board.this_move,]

		# Stats
		self.board.refresh_stats()


	def render(self):
		# Board
		for arrow in self.board.this_move.quiver:
			arrow.shoot()

		# CONTEXT:	Settings
		if self.settings.show:
			self.settings.render()

		# CONTEXT:  Analysis
		elif self.analysis.show:
			self.analysis.render()

		# NO CONTEXT
		else:
			# Elements
			for element in [
				self.reader,
				*self.writers.values(),
				*self.buttons,
			]:
				element.render()

			# Idle text
			self.display.blit(
				self.font.render("vs", True, (255, 255, 255)),
				(
					C.SIDEBAR_X_MARGIN + 10,
					(24/30)*C.BOARD_HEIGHT
				)
			)

		############# SIDEBAR MIDLINE #############
		# pygame.draw.line(
		# 	self.display,
		# 	(0,0,0),
		# 	(C.SIDEBAR_WIDTH/2,0),
		# 	(C.SIDEBAR_WIDTH/2,C.BOARD_HEIGHT),
		# )
		###########################################


	def handle_click(self , event):
		# Regular left click
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			# Board
			if event.pos[0] > C.SIDEBAR_WIDTH:
				self.board.handle_click(*self.gridify(event.pos))

			# Sidebar
			else:
				### buttons
				if self.settings.show:
					for button in self.settings.buttons:
						if button.rect.collidepoint(event.pos):
							button.click()
						elif button.active:
							for option in button.dropdown:
								if option.rect.collidepoint(event.pos):
									option.click()
							button.active = False

				elif self.analysis.show:
					for button in self.analysis.buttons:
						if button.rect.collidepoint(event.pos):
							button.click()

				else:
					for button in self.buttons:
						if button.rect.collidepoint(event.pos):
							button.click()

		# Annotations
		elif event.type in (pygame.MOUSEBUTTONDOWN,pygame.MOUSEBUTTONUP) and event.button == 3 and event.pos[0] > C.SIDEBAR_WIDTH:
			f,r = self.gridify(event.pos)

			### anchor down
			if event.type == pygame.MOUSEBUTTONDOWN:
				self.anchor = self.board.tile_of(f,r)

			### anchor up
			elif event.type == pygame.MOUSEBUTTONUP and self.anchor:
				if self.anchor is (header := self.board.tile_of(f,r)):
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

					self.board.this_move.quiver.append(Arrow(
						self,
						self.anchor,
						header
					))

		# Reader
		elif event.type == pygame.MOUSEWHEEL:
			self.reader.scroll(event.y)

		# Writers
		for writer in self.writers.values():
			if event.type == pygame.KEYDOWN:
				if writer.active:
					if event.key == pygame.K_BACKSPACE:
						writer.text = writer.text[:-1]
					else:
						writer.text += event.unicode
			elif event.type == pygame.MOUSEBUTTONDOWN and not any([
				self.settings.show,
				self.analysis.show,
			]):
				writer.active = writer.rect.collidepoint(event.pos)


	def is_game_over(self):
		# Stats
		if self.board.rulecount_threereps >= 3:
			print("force draw by repetition!")
			return True
		if self.board.rulecount_fiftymoves > 99:
			print("force draw by boredom!")
			return True

		# Calculations
		whites = [man.creed or "P" for man in self.board.all_men("w")]
		blacks = [man.creed or "P" for man in self.board.all_men("b")]

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

		pgn = []
		### multiline movetext (up to 999 turns):
		for t,turn in enumerate(re.split(r"\d{1,3}\." , self.board.movetext)):
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

				tile = self.board.tile_of(f,r)
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
		for colour in ("w","b"):
			[king] = self.board.all_men(colour=colour,creed="K")
			if not king.has_moved and king.position in ((5,1),(5,8)):
				for rook in self.board.all_men(colour=colour,creed="R"):
					if not rook.has_moved and rook.position in ((1,1),(1,8),(8,1),(8,8)):
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

		### halfmove clock (fifty move rule)
		fen_config.append(str(self.board.rulecount_fiftymoves))

		### fullmove clock
		fen_config.append(str(self.board.movenum))


		fen_config = " ".join(fen_config)

		fen = fen_board + " " + fen_config

		return fen


	# TODO: READ TAGS BEFORE MOVETEXT ON IMPORT
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
		fen        = fen_raw.split()
		fen_board  = fen[0]
		fen_config = fen[1:]

		# Board
		self.board.agent = None
		self.board.compose(
			model=self.FEN_to_model(fen_board)
		)

		# Configuration
		### active colour
		self.board.ply = fen_config[0]

		### castlability
		castlability = fen_config[1]
		for side in {"K","Q","k","q"} - set(castlability):
			corner = self.board.tile_of(
				1 if side.upper() == "Q" else 8,
				1 if side.isupper() else 8
			)

			if corner.occupant and corner.occupant.creed == "R":
				corner.occupant.has_moved = True

		### en passant availability
		ep_square = fen_config[2]
		if ep_square.isalnum():
			self.board.tile_of(
				C.FILES.index(ep_square[-2]),
				int(ep_square[-1]) + (1 if self.board.ply == "b" else -1)
			).occupant.just_moved_double = True

		### halfmove capture clock
		self.board.rulecount_fiftymoves = int(fen_config[3])

		### fullmove clock
		self.board.movenum = int(fen_config[4])

		# Other (internals)
		### halfmoves
		#####   last term accounts for FENs imported at black's turn; without it, prev/next buttons loop.
		self.board.halfmovenum = 2*self.board.movenum - (self.board.ply == "w") - bool(self.black_first)

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


	def PGN_to_move(self , ply , movetextraw):
		move = Move(self.board)
		move.forced = True
		move.text 	= movetextraw

		# Standard Algebraic Notation
		san = movetextraw

		if movetextraw.count("#"):
			san = san.replace("#","")
		elif movetextraw.count("+"):
			san = san.replace("+","")
			move.check = True

		if movetextraw.count("x"):
			# san = san.replace("x","")
			move.capture = True

		if "..." in san:
			return None

		elif "=" in san:
			# axb8=R
			move.origin = self.board.tile_of(
				C.FILES.index(san[0]),
				2 if ply else 7
			)
			move.target = self.board.tile_of(
				C.FILES.index(san[-4]),
				1 if ply else 8
			)

			move.promo = san[-1]

		elif "-" in san:
			# O-O-O
			# O-O
			move.origin = self.board.tile_of(
				5,
				8 if ply else 1
			)
			move.target = self.board.tile_of(
				7 if san.count("-") == 1 else 3,
				8 if ply else 1
			)

		elif san.isalnum():
			# b4
			# Nf7
			# exd6
			# Raxb8
			# Qh4xe1
			move.target = self.board.tile_of(
				C.FILES.index(san[-2]),
				int(san[-1])
			)

			attackers = self.board.attackers_of(
				move.target,
				colour="b" if ply else "w",
				creed=san[0] if san[0].isupper() else ""
			)

			if len(attackers) == 1:
				move.origin = self.board.tile_of(*attackers[0].position)
			else:
				# Disambiguation
				clue = "".join([char for char in san[:-2] if char.islower() or char.isnumeric()])
				print("clue:" , clue , [a.pgn for a in attackers])
				for opp in attackers:
					if clue in opp.pgn:
						print(opp.pgn)
						move.origin = self.board.tile_of(*opp.position)

		else:
			print(movetextraw , san)
			raise Exception("Imported PGN move not recognised!")

		return move


	def force_move(self , move , show=True):
		for tile in (move.origin,move.target):
			self.board.handle_click(
				file=tile.f,
				rank=tile.r,
				promo=move.promo,
				show=show
			)

			if show and tile == move.target:
				self.reader.update(self.board.movelog)
				self.board.render()
				self.render()

			pygame.display.update()

		if show:
			time.sleep(1/8)


	def gridify(self , coords):
		if self.flipped:
			return (
				8 - ((coords[0] - C.SIDEBAR_WIDTH) // C.TILE_WIDTH),
				1 + (coords[1] // C.TILE_HEIGHT)
			)
		else:
			return (
				1 + ((coords[0] - C.SIDEBAR_WIDTH) // C.TILE_WIDTH),
				8 - (coords[1] // C.TILE_HEIGHT)
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
