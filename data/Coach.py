import pygame
import time

from datetime import datetime

from data.Constants import C
from data.Board import Board
from data.Engine import Engine
from data.Settings import Settings
from data.Elements import Button,Writer,Reader,Dropdown
from data.Man import Man



class Coach:
	def __init__(self):
		self.display = pygame.display.set_mode((C.BOARD_WIDTH + C.SIDEBAR_WIDTH , C.BOARD_HEIGHT))

		self.board  = Board(self)
		self.engine = Engine(self)

		self.settings = Settings(self)

		# Graphics
		### fonts
		self.writer_font  = pygame.font.SysFont("Britannic" , 14)
		self.reader_font  = pygame.font.SysFont("Consolas" , 13)
		self.opening_font = pygame.font.SysFont("Consolas" , 13 , bold=True)

		### buttons
		self.button_import = Button(
			self,
			"IMPORT",
			C.TEXTBOX_X_OFFSET,
			515
		)
		self.button_export = Button(
			self,
			"EXPORT",
			C.TEXTBOX_X_OFFSET + C.TEXTBOX_WIDTH - C.BUTTON_WIDTH,
			515
		)

		### writers
		self.writer_title = Writer(self , self.writer_font , 'EventTitle' , 345)
		self.writer_date  = Writer(self , self.writer_font , datetime.today().strftime("%Y-%m-%d") , 380)
		self.writer_white = Writer(self , self.writer_font , 'White' , 430)
		self.writer_black = Writer(self , self.writer_font , 'Black' , 480)

		### movetext reader
		self.reader_movetext = Reader(self , self.reader_font)

		# Encyclopedia of Chess Openings
		self.eco = None


	def render(self):
		# Elements
		for button in Button.all:
			if not button.context:
				# contextual buttons (e.g. Settings buttons) rendered downstream
				button.render(self.display)

		for writer in Writer.all:
			writer.render(self.display)

		self.reader_movetext.render(self.display)

		# Statics
		self.display.blit(
			self.writer_font.render("vs." , True , (255,255,255)),
			(C.TEXTBOX_X_OFFSET + 10 , 455)
		)

		# Settings context
		if self.settings.showing:
			self.settings.render()

		# # Analysis context
		# if self.anaylsis.showing:
		# 	self.analysis.render()

		# ECO reader
		if not any([
			self.settings.showing,
			#self.analysis.showing
		]):
			self.display.blit(
				self.opening_font.render(
					self.eco.read(self.board.movetext) if self.eco else self.board.opening,
					True,
					(255, 255, 255)
				),
				(C.TEXTBOX_X_OFFSET + 5, 35)
			)


	def handle_click(self , event):
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			# Gameplay
			if event.pos[0] > C.SIDEBAR_WIDTH:
				self.board.handle_click(*pygame.mouse.get_pos())
				if self.board.agent is None and self.board.movenum > 1:
					self.reader_movetext.update(self.board.movetext)
			else:
				# Collapse dropdowns:
				for ddn in Dropdown.all:
					if ddn.showing and not any([
						ddn.trigger.rect.collidepoint(event.pos),
						*[btn.rect.collidepoint(event.pos) for btn in ddn.options]
					]):
						ddn.showing = False

			# Buttons
			for button in Button.all:
				if not button.context and not any([
					self.settings.showing,
					#self.analysis.showing,
				]):
					if button.rect.collidepoint(event.pos):
						button.click()
						break

				elif button.context == "settings" and self.settings.showing:
					if button.rect.collidepoint(event.pos):
						button.click()

				# elif button.context == "analysis" and self.analysis.showing:
				# 	if event.type == pygame.MOUSEBUTTONDOWN:
				# 		if button.rect.collidepoint(event.pos):
				# 			button.click()
				#           break


		elif event.type == pygame.MOUSEWHEEL:
			# Scroll reader
			self.reader_movetext.scroll(event.y)

		# Writers
		for writer in Writer.all:
			if event.type == pygame.KEYDOWN:
				if writer.active:
					if event.key == pygame.K_BACKSPACE:
						writer.text = writer.text[:-1]
					else:
						writer.text += event.unicode
			elif event.type == pygame.MOUSEBUTTONDOWN:
				writer.active = writer.rect.collidepoint(event.pos)


	def is_game_over(self):
		game_over = False
		whites = [man.creed or "P" for man in self.board.all_men("w")]
		blacks = [man.creed or "P" for man in self.board.all_men("b")]

		if len(whites) > 2 or len(blacks) > 2:
			game_over = self.board.is_in_checkmate()

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
			self.finish = (
				"Draw",
				"Insufficient material"
			)
			game_over = True

		return game_over


	def board_flip(self):
		self.board.flipped = not self.board.flipped
		for t in self.board.all_tiles:
			t.x = 7*C.TILE_WIDTH  - t.x
			t.y = 7*C.TILE_HEIGHT - t.y


	def board_export(self):
		import re

		# Information
		title = self.writer_title.text
		date  = self.writer_date.text
		white = self.writer_white.text
		black = self.writer_black.text

		# date & time
		# date = datetime_start.strftime("%Y-%m-%d")
		# dur_total = (datetime_end - datetime_start).total_seconds()
		# dur_hours,dur_rem = divmod(dur_total,60*60)
		# dur_mins,dur_secs = divmod(dur_rem,60)
		# duration = "{}:{}:{}".format(
		# 	str(dur_hours).zfill(2),
		# 	str(dur_mins).zfill(2),
		# 	str(dur_secs).zfill(2)
		# )

		### results
		result = None
		if self.board.finish[0] == "Checkmate":
			if self.board.finish[1] == "White":
				result = "1-0"
			else:
				result = "0-1"
		elif self.board.finish[0] == "Draw":
			result = ".5-.5"

		# Filing
		gamedir = C.DIR + "\\games\\" + title + "__" + date + ".pgn"
		with open(gamedir,"w") as file:
			file.write("[Event \"" + title + "\"]\n")
			file.write("[Date \""  + date  + "\"]\n")
			file.write("[White \"" + white + "\"]\n")
			file.write("[Black \"" + black + "\"]\n")
			if result:
				file.write("[Result \"" + result + "\"]\n")

			### multiline movetext (up to 999 turns):
			for i,line in enumerate(re.split(r"\d{1,3}\." , self.board.movetext)):
				if not i: continue
				file.write("\n" + str(i) + ". ")
				file.write(line.strip())

			if self.board.finish[1] in ("White","Black"):
				file.write("#")
			if result:
				file.write("\n" + result)


	def board_import_PGN(self , filename , multiline=True):
		import re

		self.board.agent = None

		with open(filename,"r") as file:
			if multiline:
				movelines = [line for line in file.readlines() if re.match(r"^\d{1,3}\.", line)]
				for i,line in enumerate(movelines):
					line = re.sub(r"[#+x]" , "" , line.strip())
					for ply,move in enumerate(line.split(" ")[1:]):
						special    = None
						origin_pos = None
						target_pos = None

						if "=" in move:
							# f8=N
							# ab8=R
							special = move[-1]

							origin_pos = (
								C.FILES.index(move[0]),
								2 if ply else 7
							)
							target_pos = (
								C.FILES.index(move[-4]),
								1 if ply else 8
							)
						elif "-" in move:
							# O-O-O
							# O-O
							origin_pos = (5 , 8 if ply else 1)
							if move.count("-") == 1:
								target_pos = (
									7,
									8 if ply else 1
								)
							else:
								target_pos = (
									3,
									8 if ply else 1
								)
						elif move.isalnum():
							# b4
							# ba5
							# Nf7
							target_pos = (
								C.FILES.index(move[-2]),
								int(move[-1])
							)

							attackers = self.board.attackers_of(
								target_pos,
								colour="b" if ply else "w",
								creed=move[0] if move[0].isupper() else ""
							)

							if len(attackers) == 1:
								origin_pos = attackers[0].position
							else:
								# Disambiguation
								print(target_pos, [o.pgn for o in attackers])
								raise Exception("I can't (yet) read ambiguous movetext!")

						else:
							raise Exception("Imported move not recognised!")

						self.force_move(origin_pos , target_pos , special)


	def board_export_FEN(self):
		# Board
		board = ''
		for r in range(8):
			r = 8 - r

			empty_streak = 0
			for f in range(8):
				f = 1 + f
				
				tile = self.board.tile_of(f,r)
				if tile.occupant:
					if empty_streak:
						board += str(empty_streak)
						empty_streak = 0
					
					if tile.occupant.colour == "w":
						board += tile.occupant.creed.upper() or "P"
					else:
						board += tile.occupant.creed.lower() or "p"
				else:
					empty_streak += 1

			if empty_streak:
				board += str(empty_streak)
		
			if r > 1:
				board += "/"
		
		fen = board[:-1]

		# Config
		config = []

		### active colour
		config.append( self.board.ply )

		### castlability
		castlability = ''
		for colour in ("w","b"):
			[king] = self.board.all_men(colour=colour,creed="K")
			if not king.has_moved:
				for rook in self.board.all_men(colour=colour,creed="R"):
					if not rook.has_moved:
						can_castle = "K" if rook.f > king.f else "Q"
						castlability += {
							"w" : can_castle.upper(),
							"b" : can_castle.lower()
						}[king.colour]
		
		config.append( "".join(sorted(castlability)) if castlability else "-" )
		
		### en passant availability
		epability = None
		for pawn in self.board.all_men(creed=""):
			if pawn.just_moved_double:
				epability = C.FILES[pawn.f] + str(pawn.r-1 if pawn.colour == "w" else pawn.r+1)
		
		config.append( epability or "-" )

		### halfmove clock
		# ...

		### fullmove clock
		# ...

		fen += " " + " ".join(config)
		print(fen)


	def board_import_FEN(self , fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
		fen        = fen.split(" ")
		fen_board  = fen[0]
		fen_config = fen[1:]

		# Board
		Man.all.clear()

		model = self.board_model_FEN(fen_board)
		self.board.setup(model)

		# Config
		### active colour
		self.board.ply = fen_config[0]

		### castlability
		# rook.has_moved if rook doesn't appear in string

		### en passant availability
		# ditto but pawns



	def board_model_FEN(self , fen_board):
		model = [[]]
		x,y   = 0,0
		for s in fen_board:
			if s == "/":
				model.append([])
				x  = 0
				y += 1
			else:
				if s.isnumeric():
					s = int(s)
					for xx in range(s):
						model[y].append("  ")
				else:
					c = "w" if s.isupper() else "b"
					model[y].append(c + s.upper())
		
		return model
	

	def force_move(self , origin , target , special):
		for tile in (origin,target):
			self.board.handle_click(force=(tile,special))

			self.board.render()
			if tile == target:
				self.reader_movetext.update(self.board.movetext)
				self.render()
			pygame.display.update()

		time.sleep(1/10)
