import pygame

import tkinter as tk

from src.Constants import C





class Writer:
	def __init__(self , pane , x , y , font , pretext=''):
		self.pane = pane
		self.x	  = x
		self.y	  = y
		self.font = font
		self.text = pretext

		self.active = False
		self.rect   = pygame.Rect(
			self.x,
			self.y,
			C.TEXTBOX_WIDTH,
			C.TEXTBOX_HEIGHT
		)

	def render(self):
		pygame.draw.rect(
			self.pane,
			C.TEXTBOX_LIGHT if self.active else C.TEXTBOX_DARK,
			self.rect
		)
		self.pane.blit(
			self.prose,
			(
				self.rect.x + 5,
				self.rect.y + 0.15*C.TEXTBOX_HEIGHT
			)
		)

	@property
	def prose(self):
		return self.font.render(
			self.text,
			True,
			(255,255,255)
		)



class Reader:
	def __init__(self , coach , x , y , height):
		self.coach 	= coach
		self.x		= x
		self.y		= y
		self.height = height

		# Interpreter
		self.movetext  = ''
		self.filepath  = ''
		self.catalogue = {}

		# Mechanics
		self.first_line = 0
		self.lineparts  = []

		# Rendering
		self.columns = (
			(1/35)*C.TEXTBOX_WIDTH,
			(5/20)*C.TEXTBOX_WIDTH,
			(12.5/20)*C.TEXTBOX_WIDTH
		)

		self.title_font = pygame.font.SysFont("Consolas" , 13 , bold=True)
		self.text_font  = pygame.font.SysFont("Consolas" , 13)

		self.rect = pygame.Rect(
			self.x,
			self.y + C.TEXTBOX_HEIGHT,
			C.TEXTBOX_WIDTH,
			self.height
		)

		self.load()


	def unload(self):
		self.catalogue.clear()


	def load(self , filepath=C.DIR+"\\data\\catalogue.csv"):
		import csv

		with open(filepath,"r") as file:
			for row in csv.reader(file,delimiter="\t"):
				if self.movetext in row[2]:
					self.catalogue[ row[2] ] = row[1]


	def imprint(self , part , floodlight=False):
		text = self.text_font.render(
			part,
			True,
			(255,255,255)
		)

		if floodlight:
			sz = self.text_font.size(part)
			bg = pygame.Surface((
				sz[0] + 8,
				sz[1] + 4
			))
			bg.fill((175,175,175))

			return bg,text
		else:
			return text


	def update(self):
		self.lineparts = self.factorise(
			self.coach.board.movelog,
			self.coach.board.black_first
		)

		self.first_line = max(len(self.lineparts)-20 , 0)

		self.movetext = " ".join(
			[" ".join(line) for line in self.factorise(
				self.coach.board.movelog[:self.coach.board.halfmovenum]
			)]
		)

		try:
			self.coach.board.opening = self.catalogue[self.movetext]
		except KeyError:
			return


	def render(self):
		# Boxes
		### title
		pygame.draw.rect(
			self.coach.pane,
			(50,50,50),
			pygame.Rect(
				self.x,
				self.y - C.TEXTBOX_HEIGHT,
				C.TEXTBOX_WIDTH,
				2*C.TEXTBOX_HEIGHT + 3
			)
		)

		### movetext
		pygame.draw.rect(
			self.coach.pane,
			(80,80,80),
			self.rect
		)

		# Texts
		### double-decker title
		titleparts = self.coach.board.opening.split(": ")[:2]
		for i,part in enumerate(titleparts):
			if len(titleparts) > i+1:
				part += ","

			self.coach.pane.blit(
				self.title_font.render(
					part[:30],				# Character limit based on C.TEXTBOX_WIDTH
					True,
					(255,255,255)
				),
				(
					C.SIDEBAR_X_MARGIN + 5,
					C.SIDEBAR_Y_MARGIN + C.BUTTON_HEIGHT + C.GRID_GAP + i*C.TEXTBOX_HEIGHT + 3
				)
			)

		### movetext and floodlight
		for i,moveparts in enumerate(self.lineparts):
			if self.first_line <= i <= self.first_line + 20:
				for j,part in enumerate(moveparts):
					notation = self.imprint(
						part.rjust(4) if not j else part,
						(
							i == self.coach.board.movenum - (self.coach.board.ply == "w") - 1
							and
							j == (self.coach.board.ply == "w") + 1
						)
					)
					position = (
						5 + self.rect.x + self.columns[j],
						5 + self.rect.y - 17.5*(self.first_line - i)
					)
					if type(notation) is tuple:
						self.coach.pane.blit(
							notation[0],
							(
								position[0] - 4,
								position[1] - 2
							)
						)
						self.coach.pane.blit(notation[1],position)
					else:
						self.coach.pane.blit(notation,position)


	def scroll(self , nudge):
		if len(self.lineparts) < 4:
			self.first_line = 0
		else:
			self.first_line -= nudge
			final_line = len(self.lineparts) - 4

			if self.first_line < 0:
				self.first_line = 0
			elif self.first_line > final_line:
				self.first_line = final_line


	@staticmethod
	def factorise(movelog , bfirst=False):
		parts = []
		for move in movelog[:-1]:
			if move.colour == "w":
				parts.append(str(move.number) + ".")

			if move.in_checkmate and move.in_check:
				parts.append(move.text + "#")
			elif move.in_check:
				parts.append(move.text + "+")
			else:
				parts.append(move.text)

		if bfirst:
			parts.insert(0,"1.")
			parts.insert(1,"...")

		factors = list(zip(
			parts[0::3],
			parts[1::3],
			parts[2::3],
		))
		if len(parts) % 3:
			factors.append(tuple(parts[-2:]))

		return factors



class Button:
	def __init__(self , pane , x , y , size=C.BUTTON_SIZE , preactive=False):
		self.pane	 = pane
		self.x       = x
		self.y       = y
		self.size    = size
		self.active  = preactive

		self.colour = C.BUTTON_COLOUR_ACTIVE if self.active else C.BUTTON_COLOUR_NEUTRAL

		self.font = pygame.font.SysFont("Consolas",12)
		self.rect = pygame.Rect(
			self.x,
			self.y,
			*self.size,
		)

		self.image_path = None
		self.image      = None
		self.image_rect = None

		self.dropdown = []

		self.tooltip = None

	def render(self):
		pygame.draw.rect(
			self.pane,
			self.colour,
			self.image.get_rect(center=self.rect.center)
		)
		self.pane.blit(
			self.image,
			self.image.get_rect(center=self.rect.center)
		)

		# Tooltip
		if self.tooltip:
			mouse_pos = pygame.mouse.get_pos()
			if self.rect.collidepoint(mouse_pos):
				self.pane.blit(					### can only render on coach.display to avoid overlap
					self.font.render(
						self.tooltip,
						False,
						(0,0,0),
						(255,255,255,0)
					),
					(mouse_pos[0]+15 , mouse_pos[1]+10)
				)



class ButtonBot(Button):
	def __init__(self , *kw , engine , player):
		super().__init__(*kw)
		self.engine = engine
		self.player = player

		self.image_path = C.DIR_ICONS + "btn_bot_" + self.player.lower()
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path+".png"),
			self.size
		)

		self.dropdown = [
			ButtonBotOption(
				self.pane,
				self.x,
				self.y + C.BUTTON_HEIGHT + 5,
				philosophy="RANDOM",
				trigger=self
			),
			ButtonBotOption(
				self.pane,
				self.x,
				self.y + 2*C.BUTTON_HEIGHT + 5,
				philosophy="BASIC",
				trigger=self
			),
		]
		### initial conditions
		for option in self.dropdown:
			if self.engine.player_scheme[self.player=="BLACK"] == option.philosophy.upper():
				option.active = True

		self.tooltip = self.player.title() + " bot"

	def click(self):
		self.active = not self.active

	def render(self):
		if self.active:
			for option in self.dropdown:
				option.render()
		super().render()



class ButtonBotOption(Button):
	def __init__(self , *kw , philosophy , trigger):
		super().__init__(*kw)
		self.philosophy = philosophy
		self.trigger 	= trigger

		self.image_path = self.trigger.image_path + "_" + self.philosophy.lower()
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path+".png"),
			self.size
		)

		self.tooltip = self.philosophy.title()

	def click(self):
		# Mechanics
		self.trigger.active = False

		### single-select voluntary dropdown
		for option in self.trigger.dropdown:
			option.active = not option.active if option is self else False
			option.colour = C.BUTTON_COLOUR_ACTIVE if option.active else C.BUTTON_COLOUR_NEUTRAL

		# Function
		scheme = self.trigger.engine.player_scheme[self.trigger.player.upper() == "BLACK"]
		choice = self.philosophy.upper()
		self.trigger.engine.player_scheme[self.trigger.player.upper() == "BLACK"] = choice if scheme != choice else None



class ButtonPieceStylist(Button):
	def __init__(self , *kw , board):
		super().__init__(*kw)
		self.board = board

		self.image_path = C.DIR_ICONS + "btn_pstyle"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path+".png"),
			self.size
		)

		self.dropdown = [
			ButtonPieceStyleOption(
				self.pane,
				self.x + C.BUTTON_WIDTH + 55,
				self.y + 50,
				style="8-Bit",
				trigger=self
			),
			ButtonPieceStyleOption(
				self.pane,
				self.x + C.BUTTON_WIDTH + 5,
				self.y + 50,
				style="FontAwesome",
				trigger=self
			),
			ButtonPieceStyleOption(
				self.pane,
				self.x + C.BUTTON_WIDTH + 55,
				self.y,
				style="3D",
				trigger=self
			),
			ButtonPieceStyleOption(
				self.pane,
				self.x + C.BUTTON_WIDTH + 5,
				self.y,
				style="Classic",
				trigger=self
			),
		]
		### initial conditions
		for option in self.dropdown:
			if C.PIECE_STYLE == option.style:
				option.active = True
				option.colour = C.BUTTON_COLOUR_ACTIVE

		self.tooltip = "Piece style"

	def click(self):
		self.active = not self.active

	def render(self):
		if self.active:
			for option in self.dropdown:
				option.render()
		super().render()



class ButtonPieceStyleOption(Button):
	def __init__(self , *kw , style , trigger):
		super().__init__(*kw)
		self.style	 = style
		self.trigger = trigger

		self.image_path = self.trigger.image_path + "_" + self.style.lower()
		self.image = pygame.transform.scale(
			pygame.image.load(self.image_path+".png"),
			self.size
		)

		self.tooltip = self.style + " set"

	def click(self):
		# Mechanics
		self.trigger.active = False

		### single-select mandatory dropdown
		if (style := self.style.upper()) == C.PIECE_STYLE:
			return

		for option in self.trigger.dropdown:
			option.active = option is self
			option.colour = C.BUTTON_COLOUR_ACTIVE if option.active else C.BUTTON_COLOUR_NEUTRAL

		# Function
		C.PIECE_STYLE = style
		C.DIR_SETS    = C.DIR_MEDIA + "sets\\" + C.PIECE_STYLE + "\\"
		for tile in self.trigger.board.all_tiles:
			if tile.occupant:
				### scaling
				squish = -35
				if tile.occupant.creed:
					squish += 15
					if self.style == "8-Bit":
						squish -= 10

				image_size = [L+squish for L in C.TILE_SIZE]

				### applying
				tile.occupant.image_path = C.DIR_SETS + tile.occupant.colour + "_" + tile.occupant.image_path.split("_")[-1]
				tile.occupant.image = pygame.image.load(tile.occupant.image_path)
				tile.occupant.image = pygame.transform.scale(tile.occupant.image , image_size)
				tile.render()



class ButtonBoardStylist(Button):
	def __init__(self , *kw , board):
		super().__init__(*kw)
		self.board = board

		self.image_path = C.DIR_ICONS + "\\btn_bstyle"
		image_raw  = pygame.image.load(self.image_path+".png")
		self.image = pygame.transform.rotozoom(
			image_raw,
			angle=90,
			scale=self.size[0]/image_raw.get_size()[0]
		)

		self.dropdown = [
			ButtonBoardStyleOption(
				self.pane,
				self.x + C.BUTTON_WIDTH + 5,
				self.y + 50,
				style="BLEAK",
				trigger=self,
			),
			ButtonBoardStyleOption(
				self.pane,
				self.x + 2*C.BUTTON_WIDTH + 4,
				self.y,
				style="CHEAP",
				trigger=self,
			),
			ButtonBoardStyleOption(
				self.pane,
				self.x + C.BUTTON_WIDTH + 5,
				self.y,
				style="HAZEL",
				trigger=self,
			),
		]

		self.tooltip  = "Board style"

	def click(self):
		self.active = not self.active

	def render(self):
		if self.active:
			for option in self.dropdown:
				option.render()
		super().render()



class ButtonBoardStyleOption(Button):
	def __init__(self , *kw , style , trigger):
		super().__init__(*kw)
		self.style 	 = eval("C.BOARD_STYLE_" + style)
		self.trigger = trigger

		self.tooltip = style.title() + " board"

	def click(self):
		# Mechanics
		self.trigger.active = False

		### single-select mandatory dropdown
		if self.style == C.BOARD_STYLE:
			return

		for option in self.trigger.dropdown:
			option.active = not option.active if option is self else False
			option.colour = C.BUTTON_COLOUR_ACTIVE if option.active else C.BUTTON_COLOUR_NEUTRAL

		# Function
		C.BOARD_STYLE = self.style
		for tile in self.trigger.board.all_tiles:
			if (tile.f + tile.r) % 2 == 1:
				tile.rgb_basic = C.BOARD_STYLE[0]
				tile.rgb_fresh = C.BOARD_STYLE[1]
			else:
				tile.rgb_basic = C.BOARD_STYLE[2]
				tile.rgb_fresh = C.BOARD_STYLE[3]

	def render(self):
		### top left quadrant
		pygame.draw.rect(
			self.pane,
			self.style[0],
			pygame.Rect(
				self.x,
				self.y,
				(3/4)*self.size[0] + 1,
				(1/2)*self.size[1]
			)
		)
		### bottom left quadrant
		pygame.draw.rect(
			self.pane,
			self.style[2],
			pygame.Rect(
				self.x,
				self.y + self.size[1]/2,
				(3/4)*self.size[0] + 1,
				(1/2)*self.size[1]
			)
		)
		### top right quadrant
		pygame.draw.rect(
			self.pane,
			self.style[1],
			pygame.Rect(
				self.x + (3/4)*self.size[0],
				self.y,
				(1/4)*self.size[0],
				(1/2)*self.size[1]
			)
		)
		### bottom right quadrant
		pygame.draw.rect(
			self.pane,
			self.style[3],
			pygame.Rect(
				self.x + (3/4)*self.size[0],
				self.y + self.size[1]/2,
				(1/4)*self.size[0],
				(1/2)*self.size[1]
			)
		)

		# Tooltip
		if self.tooltip:
			mouse_pos = pygame.mouse.get_pos()
			if self.rect.collidepoint(mouse_pos):
				self.pane.blit(            # must blit from coach so it renders above other buttons and the board.
					self.font.render(
						self.tooltip,
						False,
						(0,0,0),
						(255,255,255,0)
					),
					(mouse_pos[0]+15 , mouse_pos[1]+10)
				)



class ButtonShowSettings(Button):
	def __init__(self , *kw , coach):
		super().__init__(*kw)
		self.coach = coach

		self.image_path = C.DIR_ICONS + "\\btn_show_settings.png"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path),
			self.size
		)

		self.tooltip = "Settings"

	def click(self):
		self.coach.settings.show = True
		self.coach.analysis.show = False



class ButtonShowAnalysis(Button):
	def __init__(self , *kw , coach):
		super().__init__(*kw)
		self.coach = coach

		self.image_path = C.DIR_ICONS + "\\btn_show_analysis.png"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path),
			self.size
		)

		self.tooltip = "Analysis"

	def click(self):
		self.coach.settings.show = False
		self.coach.analysis.show = True



class ButtonShut(Button):
	def __init__(self , *kw , coach):
		super().__init__(*kw)
		self.coach = coach

		self.colour = (85,75,75)

		self.image_path = C.DIR_ICONS + "\\btn_shut.png"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path),
			self.size
		)

		self.tooltip = "Close"

	def click(self):
		self.coach.settings.show = False
		self.coach.analysis.show = False



class ButtonPrevious(Button):
	def __init__(self , *kw , coach):
		super().__init__(*kw)
		self.coach = coach

		self.image_path = C.DIR_ICONS + "\\btn_prev.png"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path),
			self.size
		)

		self.tooltip = "Previous"

	def click(self):
		# print("--- PREV ---")
		# print(self.coach.board.this_move.id if self.coach.board.this_move else "")
		# print(self.coach.board.last_move.id if self.coach.board.last_move else "")
		# print(self.coach.board.halfmovenum,[m.id for m in self.coach.board.movelog])
		# print("---      ---")

		if self.coach.board.halfmovenum > 1:
			last_move = self.coach.board.movelog[self.coach.board.halfmovenum - 2]
			if self.coach.board.halfmovenum > 2:
				past_move = self.coach.board.movelog[self.coach.board.halfmovenum - 3]
			else:
				past_move = None

			# Board mechanics
			self.coach.import_FEN(last_move.fen)
			self.coach.board.this_move = last_move
			self.coach.board.last_move = past_move

			# Move mechanics
			unmove = last_move.rewind()

			cache = self.coach.board.tile_of(*unmove.target.position).occupant
			cache.position = unmove.target.position
			self.coach.board.tile_of(*unmove.target.position).occupant = None

			unmove.animate()

			self.coach.board.tile_of(*unmove.target.position).occupant = cache

			# Opening
			self.coach.reader.update()

			# Statistics
			self.coach.board.refresh_stats()

		# print(self.coach.board.this_move.id if self.coach.board.this_move else "")
		# print(self.coach.board.last_move.id if self.coach.board.last_move else "")
		# print(self.coach.board.halfmovenum,[m.id for m in self.coach.board.movelog])
		# print("------------")
		# print()



class ButtonNext(Button):
	def __init__(self , *kw , coach):
		super().__init__(*kw)
		self.coach = coach

		self.image_path = C.DIR_ICONS + "\\btn_next.png"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path),
			self.size
		)

		self.tooltip = "Next"

	def click(self):
		# print("--- NEXT ---")
		# print(self.coach.board.this_move.id if self.coach.board.this_move else "")
		# print(self.coach.board.last_move.id if self.coach.board.last_move else "")
		# print(self.coach.board.halfmovenum,[m.id for m in self.coach.board.movelog])
		# print("---      ---")

		if self.coach.board.halfmovenum < len(self.coach.board.movelog):
			next_move = self.coach.board.movelog[self.coach.board.halfmovenum]
			this_move = self.coach.board.movelog[self.coach.board.halfmovenum - 1]

			# Board mechanics
			self.coach.import_FEN(next_move.fen)
			self.coach.board.this_move = next_move
			self.coach.board.last_move = this_move

			# Move mechanics
			cache = self.coach.board.tile_of(*this_move.target.position).occupant
			cache.position = this_move.target.position
			if this_move.ep:
				self.coach.board.tile_of(*this_move.target.position).occupant = None
				self.coach.board.tile_of(*this_move.ep.position).occupant     = this_move.capture
			else:
				self.coach.board.tile_of(*this_move.target.position).occupant = this_move.capture

			this_move.animate()

			self.coach.board.tile_of(*this_move.target.position).occupant = cache
			if this_move.ep:
				self.coach.board.tile_of(*this_move.ep.position).occupant = None

			# Opening
			self.coach.reader.update()

			# Statistics
			self.coach.board.refresh_stats()

		# print(self.coach.board.this_move.id if self.coach.board.this_move else "")
		# print(self.coach.board.last_move.id if self.coach.board.last_move else "")
		# print(self.coach.board.halfmovenum,[m.id for m in self.coach.board.movelog])
		# print("------------")
		# print()



class ButtonECOI(Button):
	def __init__(self , *kw , reader):
		super().__init__(*kw)
		self.reader = reader

		self.image_path = C.DIR_ICONS + "\\btn_ecoi.png"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path),
			self.size
		)

		self.tooltip = "Interpret opening"

	def click(self):
		if self.active:
			self.active = False
			self.reader.unload()
		else:
			self.active = True
			self.reader.load()
			self.reader.update()



class ButtonFlip(Button):
	def __init__(self , *kw , board):
		super().__init__(*kw)
		self.board = board

		self.image_path = C.DIR_ICONS + "\\btn_flip.png"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path),
			self.size
		)

		self.tooltip = "Flip board"

	def click(self):
		self.board.flipped = not self.board.flipped



class ButtonImport(Button):
	def __init__(self , *kw , coach):
		super().__init__(*kw)
		self.coach = coach

		self.image_path = C.DIR_ICONS + "\\btn_import.png"
		image_raw  = pygame.image.load(self.image_path)
		self.image = pygame.transform.rotozoom(
			image_raw,
			angle=90,
			scale=self.size[0]/image_raw.get_size()[0]
		)

		self.tooltip = "Import"

	def click(self):
		# Imports
		from tkinter import Tk

		# Load
		root = Tk()
		root.withdraw()

		# Ask
		D = Dilemma(
			self.coach,
			"Import PGN or FEN?",
			"PGN","FEN"
		)
		D.wait_window()

		if D.choice == "PGN":
			from tkinter import filedialog

			if filename := filedialog.askopenfilename(
				parent=root,
				title="Import PGN"
			):
				self.coach.reset()
				self.coach.import_PGN(filename)

		elif D.choice == "FEN":
			from tkinter import simpledialog

			if fen_in := simpledialog.askstring(
				parent=root,
				title="Import FEN",
				prompt="\t"*8
			) or C.IMPORT_FEN_DEFAULT:
				self.coach.reset(fen=fen_in)

		# Refocus pygame window
		root.destroy()



class ButtonExport(Button):
	def __init__(self , *kw , coach):
		super().__init__(*kw)
		self.coach = coach

		self.image_path = C.DIR_ICONS + "\\btn_export.png"
		image_raw  = pygame.image.load(self.image_path)
		self.image = pygame.transform.rotozoom(
			image_raw,
			angle=90,
			scale=self.size[0]/image_raw.get_size()[0]
		)

		self.tooltip = "Export"

	def click(self):
		# Information
		title = self.coach.writers["TITLE"].text
		date  = self.coach.writers["DATE"].text
		white = self.coach.writers["WHITE"].text
		black = self.coach.writers["BLACK"].text

		### results
		result = None
		if self.coach.board.outcome[0] == "Checkmate":
			if self.coach.board.outcome[1] == "White":
				result = "1-0"
			else:
				result = "0-1"
		elif self.coach.board.outcome[0] == "Draw":
			result = ".5-.5"

		# File Handling
		filename = title + "__" + date
		gamedir  = C.DIR + "\\games\\" + filename + ".pgn"
		with open(gamedir,"w") as file:
			file.write("[Event \"" + title + "\"]\n")
			file.write("[Date \""  + date  + "\"]\n")
			file.write("[White \"" + white + "\"]\n")
			file.write("[Black \"" + black + "\"]\n")
			if result:
				file.write("[Result \"" + result + "\"]\n")

			for line in self.coach.export_PGN():
				file.write(line)

			if self.coach.board.outcome[1] in ("White","Black"):
				file.write("#")
			if result:
				file.write("\n" + result)

		print(filename + ".pgn exported!")



class ButtonCoords(Button):
	def __init__(self , *kw , board):
		super().__init__(*kw)
		self.board = board

		self.image_path = C.DIR_ICONS + "\\btn_coordinates.png"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path),
			self.size
		)

		self.tooltip = "Show coordinates"

	def click(self):
		self.active = not self.active

		self.board.show_coords = not self.board.show_coords



# TODO: FRESH MOVE HIGHLIGHT TOGGLER
class ButtonLegalMoves(Button):
	def __init__(self , *kw , board):
		super().__init__(*kw)
		self.board = board

		self.image_path = C.DIR_ICONS + "\\btn_legal_moves.png"
		image_raw  = pygame.image.load(self.image_path)
		self.image = pygame.transform.rotozoom(
			image_raw,
			angle=45,
			scale=self.size[0]/(image_raw.get_size()[0]*(2**.5))
		)

		self.tooltip = "Show legal moves"

	def click(self):
		self.active = not self.active

		self.board.show_legals = not self.board.show_legals



class ButtonReset(Button):
	def __init__(self , *kw , coach):
		super().__init__(*kw)
		self.coach = coach

		self.image_path = C.DIR_ICONS + "\\btn_reset.png"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path),
			self.size
		)

		self.tooltip = "Reset"

	def click(self):
		self.coach.reset()



class ButtonSpedometer(Button):
	def __init__(self , *kw , slider):
		super().__init__(*kw)
		self.slider = slider

		self.image_path = C.DIR_ICONS + "btn_spedometer" + str(int(self.slider.value))
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path+".png"),
			self.size
		)

		self.tooltip = "Animation speed"

	def click(self):
		pass

	def render(self):
		if pygame.mouse.get_pressed() and self.slider.hitbox.collidepoint(pygame.mouse.get_pos()):
			self.image_path = C.DIR_ICONS + "btn_spedometer" + str(int(self.slider.value))
			self.image      = pygame.transform.scale(
				pygame.image.load(self.image_path+".png"),
				self.size
			)

		super().render()



class Slider:
	def __init__(self , context , x , y , size , metric , domain , nparts):
		self.context = context
		self.x		 = x
		self.y		 = y
		self.size	 = size
		self.metric  = metric
		self.min_val = domain[0]
		self.max_val = domain[1]
		self.nparts	 = nparts

		# Mechanics
		self.ratio = (eval(self.metric) - self.min_val) / (self.max_val - self.min_val)
		self.value = self.min_val + self.ratio*(self.max_val - self.min_val)

		self.min_pos = 0.075*self.size[0]
		self.max_pos = 0.925*self.size[0]

		# Rendering
		self.trackbed = pygame.Surface(self.size,pygame.SRCALPHA)
		self.handle	  = pygame.Rect(
				self.min_pos + (self.max_pos - self.min_pos)*self.ratio - 5,
				(1/4)*self.size[1],
				10,
				(1/2)*self.size[1]
		)
		self.hitbox	  = pygame.Rect(
			self.x + self.min_pos - 5,
			self.y,
			self.max_pos - self.min_pos + 10,
			self.size[1]
		)


	def hold(self , x):
		# Mechanics
		self.ratio = round( (self.nparts-1) *
			(x - self.hitbox.left) / (self.hitbox.right - self.hitbox.left)
		) / (self.nparts-1)

		self.value = self.min_val + self.ratio*(self.max_val - self.min_val)

		self.handle.centerx = self.min_pos + self.ratio*(self.max_pos - self.min_pos)

		# Function
		exec(self.metric + " = 50/" + str(self.value))


	def render(self):
		# Railing
		### trackbed
		self.trackbed.fill(C.SLIDER_COLOUR)
		### track
		pygame.draw.line(
			self.trackbed,
			(0,0,0,15),
			( self.min_pos , self.size[1]/2 ),
			( self.max_pos , self.size[1]/2 )
		)
		### graduation
		for i in range(self.nparts):
			pygame.draw.line(
				self.trackbed,
				(0,0,0,1),
				( self.min_pos + (i/(self.nparts-1))*(self.max_pos - self.min_pos) , (3/7)*self.size[1] ),
				( self.min_pos + (i/(self.nparts-1))*(self.max_pos - self.min_pos) , (4/7)*self.size[1] )
			)

		# Handle
		pygame.draw.rect(
			self.trackbed,
			C.BANNER_COLOUR,
			self.handle
		)

		self.context.pane.blit(self.trackbed,(self.x,self.y))



class Dilemma(tk.Toplevel):
	def __init__(self , coach , message , option_left , option_right , title=None):
		tk.Toplevel.__init__(self)

		self.coach = coach
		self.text  = message
		self.left  = option_left
		self.right = option_right
		self.title(title or "")

		self.choice = None

		tk.Label(
			master=self,
			text=message
		).pack(padx=20,pady=10)
		tk.Button(
			master=self,
			text=option_left,
			command=self.click_left
		).pack(side="left",padx=20,pady=10)
		tk.Button(
			master=self,
			text=option_right,
			command=self.click_right
		).pack(side="right",padx=20,pady=10)

		self.geometry("+%d+%d" % (
			C.WINDOW_POS[0] + 500,
			C.WINDOW_POS[1]
		))


	def click_left(self):
		self.choice = self.left
		self.destroy()


	def click_right(self):
		self.choice = self.right
		self.destroy()



class Counter:
	def __init__(self , pane , title , text , font , x , y):
		self.pane 	 = pane
		self.title   = title
		self.text    = str(text)
		self.font    = font
		self.x       = x
		self.y       = y


	def render(self):
		sz = self.font.size(self.text)
		bg = pygame.Surface((
			sz[0] + 8,
			sz[1] + 5
		))
		bg.fill((0,0,0))

		# Text
		self.pane.blit(
			self.font.render(self.title , True , (255,255,255)),
			(
				self.x + (5*len(self.text)) + 20,
				self.y + 3
			)
		)

		# Number
		self.pane.blit(
			bg,
			(self.x,self.y)
		)
		self.pane.blit(
			self.font.render(
				self.text,
				True,
				(255,255,255)
			),
			(self.x+4 , self.y+3)
		)



class Arrow:
	def __init__(self , coach , base , roof):
		self.coach = coach
		self.base  = base
		self.roof  = roof

		# Archery basics (recalculated every .shoot() so board can be flipped)
		self.nock = None
		self.head = None

		# Maths
		self.midline = None
		self.centre  = None

		# Rendering
		self.sprite = None
		self.girth  = 25


	def __str__(self):
		return str(self.base) + "->" + str(self.roof)


	def shoot(self):
		self.nock = pygame.math.Vector2(self.base.rect.center)
		self.head = pygame.math.Vector2(self.roof.rect.center)

		self.midline = self.head - self.nock
		self.centre  = (self.head + self.nock)/2


		def draw_knight():
			width  = abs(self.midline.x) + C.TILE_WIDTH
			height = abs(self.midline.y) + C.TILE_HEIGHT

			upright = pygame.Surface(
				(width,height),
				pygame.SRCALPHA
			)

			# Draw as if upright ...
			### shafts
			pygame.draw.lines(
				upright,
				C.ARROW_COLOUR,
				closed=False,
				points=[
					(
						(5/6)*C.TILE_WIDTH,
						C.TILE_HEIGHT/2
					 ),
					(
						width - C.TILE_WIDTH/2,
						C.TILE_HEIGHT/2
					),
					(
						width - C.TILE_WIDTH/2,
						height - (5/6)*C.TILE_HEIGHT
					),
				],
				width=self.girth
			)
			### rounded corner
			pygame.draw.circle(
				upright,
				C.ARROW_COLOUR,
				(
					width - C.TILE_WIDTH/2,
					C.TILE_HEIGHT/2
				),
				self.girth/2
			)

			# ... then flip.
			if abs(self.midline.x) > abs(self.midline.y):
				pygame.draw.polygon(
					upright,
					C.ARROW_COLOUR,
					points=[
						(
							width - (3/4)*C.TILE_WIDTH,
							height - (5/6)*C.TILE_HEIGHT
						),
						(
							width - (1/4)*C.TILE_WIDTH,
							height - (5/6)*C.TILE_HEIGHT
						),
						(
							width - (1/2)*C.TILE_WIDTH,
							height - (1/2)*C.TILE_HEIGHT
						)
					]
				)

				return pygame.transform.flip(
					upright,
					self.midline.x < 0,
					self.midline.y < 0
				)

			else:
				pygame.draw.polygon(
					upright,
					C.ARROW_COLOUR,
					points=[
						(
							(5/6)*C.TILE_WIDTH,
							(3/4)*C.TILE_HEIGHT
						),
						(
							(5/6)*C.TILE_WIDTH,
							(1/4)*C.TILE_HEIGHT
						),
						(
							(1/2)*C.TILE_WIDTH,
							(1/2)*C.TILE_HEIGHT
						)

					]
				)

				return pygame.transform.flip(
					upright,
					self.midline.x > 0,
					self.midline.y > 0
				)


		def draw_direct():
			height = self.midline.magnitude()

			upright = pygame.Surface(
				(C.TILE_WIDTH,height),
				pygame.SRCALPHA
			)

			# Draw as if upright ...
			### shaft
			pygame.draw.line(
				upright,
				C.ARROW_COLOUR,
				(
					C.TILE_WIDTH/2,
					C.TILE_HEIGHT/3
				),
				(
					C.TILE_WIDTH/2,
					height - C.TILE_HEIGHT/3
				),
				self.girth
			)
			### arrowhead
			pygame.draw.polygon(
				upright,
				C.ARROW_COLOUR,
				points=[
					(
						(1/2)*C.TILE_WIDTH,
						0
					),
					(
						(1/4)*C.TILE_WIDTH,
						(1/3)*C.TILE_HEIGHT
					),
					(
						(3/4)*C.TILE_WIDTH,
						(1/3)*C.TILE_HEIGHT
					)
				]
			)

			# ... then rotate.
			return pygame.transform.rotate(
				upright,
				self.midline.angle_to((0,-1))
			)


		if abs(self.midline.elementwise()) in [
			(100,200),
			(200,100)
		]:
			self.sprite = draw_knight()
		else:
			self.sprite = draw_direct()

		self.coach.display.blit(
			self.sprite,
			self.sprite.get_rect(center=self.centre)
		)
