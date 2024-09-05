import time
import pygame

import tkinter as tk

from src.Constants import C





class Writer:
	def __init__(self , coach , font , y_offset , pretext=''):
		self.coach    = coach
		self.font 	  = font
		self.text     = pretext
		self.y_offset = y_offset

		self.active = False
		self.rect   = pygame.Rect(
			C.SIDEBAR_X_MARGIN,
			self.y_offset,
			C.TEXTBOX_WIDTH,
			C.TEXTBOX_HEIGHT
		)

	def render(self):
		pygame.draw.rect(
			self.coach.display,
			C.TEXTBOX_LIGHT if self.active else C.TEXTBOX_DARK,
			self.rect
		)
		self.coach.display.blit(
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
	def __init__(self , coach , height , y_offset):
		self.coach 	  = coach
		self.height   = height
		self.y_offset = y_offset

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
			C.SIDEBAR_X_MARGIN,
			self.y_offset + C.TEXTBOX_HEIGHT,
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
			self.coach.black_first
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
			self.coach.display,
			(50,50,50),
			pygame.Rect(
				C.SIDEBAR_X_MARGIN,
				self.y_offset - C.TEXTBOX_HEIGHT,
				C.TEXTBOX_WIDTH,
				2*C.TEXTBOX_HEIGHT + 3
			)
		)

		### movetext
		pygame.draw.rect(
			self.coach.display,
			(80,80,80),
			self.rect
		)

		# Texts
		### double-decker title
		titleparts = self.coach.board.opening.split(": ")[:2]
		for i,part in enumerate(titleparts):
			if len(titleparts) > i+1:
				part += ","

			self.coach.display.blit(
				self.title_font.render(
					part[:30],				# Character limit based on C.TEXTBOX_WIDTH
					True,
					(255,255,255)
				),
				(
					C.SIDEBAR_X_MARGIN + 7.5,
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
						self.coach.display.blit(
							notation[0],
							(
								position[0] - 4,
								position[1] - 2
							)
						)
						self.coach.display.blit(notation[1],position)
					else:
						self.coach.display.blit(notation,position)


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
	def __init__(self , coach , name , x , y , context=None , size=C.BUTTON_SIZE , preactive=False):
		self.coach   = coach
		self.name    = name
		self.x       = x
		self.y       = y
		if context is not None:
			self.context = context
			self.pane 	 = context.pane
		else:
			self.context = coach
			self.pane 	 = coach.display
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
				self.coach.display.blit(            # must blit from coach not pane so it renders above other buttons and board.
					self.font.render(
						self.tooltip,
						False,
						(0,0,0),
						(255,255,255,0)
					),
					(mouse_pos[0]+15 , mouse_pos[1]+10)
				)



class ButtonBot(Button):
	def __init__(self , *kw , player):
		super().__init__(*kw)
		self.player = player

		self.image_path = C.DIR_ICONS + "btn_" + self.name.lower()
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path+".png"),
			self.size
		)

		self.dropdown = [
			ButtonBotOption(
				self.coach,
				"MATERIALISTIC",
				self.x + C.BUTTON_WIDTH,
				self.y + C.BUTTON_HEIGHT + 5,
				self.context,
				trigger=self
			),
			ButtonBotOption(
				self.coach,
				"POSITIONAL",
				self.x,
				self.y + 2*C.BUTTON_HEIGHT + 5,
				self.context,
				trigger=self
			),
			ButtonBotOption(
				self.coach,
				"RANDOM",
				self.x,
				self.y + C.BUTTON_HEIGHT + 5,
				self.context,
				trigger=self
			),
			# ButtonBotOption(
			# 	self.player,
			# 	self.coach,
			# 	"BASIC",
			# 	self.x + 105,
			# 	self.y + 50,
			# 	self.pane
			# )
		]
		### initial conditions
		for option in self.dropdown:
			if self.coach.engine.player_scheme[self.player=="BLACK"] == option.name.upper():
				option.active = True

		self.tooltip = self.player.title() + " bot"

	def click(self):
		self.active = not self.active
		# for button in self.context.buttons:
		# 	if button.active and button.dropdown and button is not self:
		# 		button.active = False

	def render(self):
		super().render()
		if self.active:
			for option in self.dropdown:
				option.render()



class ButtonBotOption(Button):
	def __init__(self , *kw , trigger):
		super().__init__(*kw)
		self.trigger = trigger

		self.image_path = self.trigger.image_path + self.name.lower()
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path+".png"),
			self.size
		)

		self.tooltip = self.name.title()

	def click(self):
		# Board Mechanics
		self.trigger.active = False

		### single-select voluntary dropdown
		for option in self.trigger.dropdown:
			option.active = not option.active if option is self else False
			option.colour = C.BUTTON_COLOUR_ACTIVE if option.active else C.BUTTON_COLOUR_NEUTRAL

		# Function
		# scheme = self.coach.engine.player_scheme[self.trigger.player.upper() == "BLACK"]
		# choice = self.name.upper()
		# self.coach.engine.player_scheme[self.trigger.player.upper() == "BLACK"] = choice if scheme != choice else None



class ButtonPieceStylist(Button):
	def __init__(self , *kw):
		super().__init__(*kw)

		self.image_path = C.DIR_ICONS + "btn_" + self.name.lower()
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path+".png"),
			self.size
		)

		self.dropdown = [
			ButtonPieceStyleOption(
				self.coach,
				"3D",
				self.x + C.BUTTON_WIDTH + 55,
				self.y,
				self.context,
				trigger=self
			),
			ButtonPieceStyleOption(
				self.coach,
				"Classic",
				self.x + C.BUTTON_WIDTH + 5,
				self.y,
				self.context,
				trigger=self
			),
			ButtonPieceStyleOption(
				self.coach,
				"FontAwesome",
				self.x + C.BUTTON_WIDTH + 5,
				self.y + 50,
				self.context,
				trigger=self
			),
			ButtonPieceStyleOption(
				self.coach,
				"8-Bit",
				self.x + C.BUTTON_WIDTH + 55,
				self.y + 50,
				self.context,
				trigger=self
			),
		]
		### initial conditions
		for option in self.dropdown:
			if C.PIECE_STYLE == option.name.upper():
				option.active = True
				option.colour = C.BUTTON_COLOUR_ACTIVE

		self.tooltip = "Piece style"

	def click(self):
		self.active = not self.active
		# for button in self.context.buttons:
		# 	if button.active and button.dropdown and button is not self:
		# 		button.active = False

	def render(self):
		super().render()
		if self.active:
			for option in self.dropdown:
				option.render()



class ButtonPieceStyleOption(Button):
	def __init__(self , *kw , trigger):
		super().__init__(*kw)
		self.trigger = trigger

		self.image_path = self.trigger.image_path + self.name.lower()
		self.image = pygame.transform.scale(
			pygame.image.load(self.image_path+".png"),
			self.size
		)

		self.tooltip = self.name + " set"

	def click(self):
		# Board Mechanics
		self.trigger.active = False

		### single-select mandatory dropdown
		if (style := self.name.upper()) == C.PIECE_STYLE:
			return

		for option in self.trigger.dropdown:
			option.active = not option.active if option is self else False
			option.colour = C.BUTTON_COLOUR_ACTIVE if option.active else C.BUTTON_COLOUR_NEUTRAL

		# Function
		C.PIECE_STYLE = style
		C.DIR_SETS    = C.DIR_MEDIA + "\\sets\\" + C.PIECE_STYLE + "\\"
		for tile in self.coach.board.all_tiles:
			if tile.occupant:
				### scaling
				squish = -35
				if tile.occupant.creed:
					squish += 10
				if self.name == "8-Bit":
					squish -= 10

				image_size = [L+squish for L in C.TILE_SIZE]

				### applying
				tile.occupant.image_path = C.DIR_SETS + tile.occupant.colour + "_" + tile.occupant.image_path.split("_")[-1]
				tile.occupant.image = pygame.image.load(tile.occupant.image_path)
				tile.occupant.image = pygame.transform.scale(tile.occupant.image , image_size)
				tile.render()



# TODO: ADD WALNUT BOARD STYLE (USES IMAGES)
class ButtonBoardStylist(Button):
	def __init__(self , *kw):
		super().__init__(*kw)

		self.image_path = C.DIR_ICONS + "\\btn_bstyle_"
		image_raw  = pygame.image.load(self.image_path+".png")
		self.image = pygame.transform.rotozoom(
			image_raw,
			angle=90,
			scale=self.size[0]/image_raw.get_size()[0]
		)

		self.dropdown = [
			ButtonBoardStyleOption(
				self.coach,
				"HAZEL",
				self.x + C.BUTTON_WIDTH + 5,
				self.y,
				self.context,
				trigger=self,
				style=C.BOARD_STYLE_HAZEL,
		),
			ButtonBoardStyleOption(
				self.coach,
				"BLEAK",
				self.x + C.BUTTON_WIDTH + 5,
				self.y + 50,
				self.context,
				trigger=self,
				style=C.BOARD_STYLE_BLEAK,
			),
			ButtonBoardStyleOption(
				self.coach,
				"CHEAP",
				self.x + 2*C.BUTTON_WIDTH + 4,
				self.y,
				self.context,
				trigger=self,
				style=C.BOARD_STYLE_CHEAP,
			),
		]

		self.tooltip  = "Board style"

	def click(self):
		self.active = not self.active
		# for button in self.context.buttons:
		# 	if button.active and button.dropdown and button is not self:
		# 		button.active = False

	def render(self):
		super().render()
		if self.active:
			for option in self.dropdown:
				option.render()



class ButtonBoardStyleOption(Button):
	def __init__(self , *kw , trigger , style):
		super().__init__(*kw)
		self.trigger = trigger
		self.style   = style

		self.tooltip = self.name.title() + " board"

	def click(self):
		# Board Mechanics
		self.trigger.active = False

		### single-select mandatory dropdown
		if self.style == C.BOARD_STYLE:
			return

		for option in self.trigger.dropdown:
			option.active = not option.active if option is self else False
			option.colour = C.BUTTON_COLOUR_ACTIVE if option.active else C.BUTTON_COLOUR_NEUTRAL

		# Function
		C.BOARD_STYLE = self.style
		for tile in self.coach.board.all_tiles:
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
				self.coach.display.blit(            # must blit from coach so it renders above other buttons and the board.
					self.font.render(
						self.tooltip,
						False,
						(0,0,0),
						(255,255,255,0)
					),
					(mouse_pos[0]+15 , mouse_pos[1]+10)
				)



class ButtonShowSettings(Button):
	def __init__(self , *kw):
		super().__init__(*kw)

		self.image_path = C.DIR_ICONS + "\\btn_show_settings.png"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path),
			self.size
		)

		self.tooltip = "Settings"

	def click(self):
		self.coach.analysis.show = False
		self.coach.settings.show = True



class ButtonShowAnalysis(Button):
	def __init__(self , *kw):
		super().__init__(*kw)

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
	def __init__(self , *kw):
		super().__init__(*kw)
		self.colour = (85,75,75)

		self.image_path = C.DIR_ICONS + "\\btn_shut.png"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path),
			self.size
		)

		self.tooltip = "Close"

	def click(self):
		self.context.show = False



class ButtonPrevious(Button):
	def __init__(self , *kw):
		super().__init__(*kw)

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

			# Movetext
			self.coach.reader.update()

			# Statistics
			self.coach.board.refresh_stats()

		# print(self.coach.board.this_move.id if self.coach.board.this_move else "")
		# print(self.coach.board.last_move.id if self.coach.board.last_move else "")
		# print(self.coach.board.halfmovenum,[m.id for m in self.coach.board.movelog])
		# print("------------")
		# print()



class ButtonNext(Button):
	def __init__(self , *kw):
		super().__init__(*kw)

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

			# Movetext
			self.coach.reader.update()

			# Statistics
			self.coach.board.refresh_stats()

		# print(self.coach.board.this_move.id if self.coach.board.this_move else "")
		# print(self.coach.board.last_move.id if self.coach.board.last_move else "")
		# print(self.coach.board.halfmovenum,[m.id for m in self.coach.board.movelog])
		# print("------------")
		# print()



class ButtonECOI(Button):
	def __init__(self , *kw):
		super().__init__(*kw)

		self.image_path = C.DIR_ICONS + "\\btn_ecoi.png"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path),
			self.size
		)

		self.tooltip = "ECO Interpreter active!" if self.active else "Interpret opening"

	def click(self):
		if self.active:
			self.active  = False
			self.colour  = C.BUTTON_COLOUR_NEUTRAL
			self.tooltip = "Interpret opening"

			self.coach.reader.unload()
		else:
			self.active  = True
			self.colour  = C.BUTTON_COLOUR_ACTIVE
			self.tooltip = "ECO Interpreter active!"

			self.coach.reader.load()




class ButtonFlip(Button):
	def __init__(self , *kw):
		super().__init__(*kw)

		self.image_path = C.DIR_ICONS + "\\btn_flip.png"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path),
			self.size
		)

		self.tooltip = "Flip board"

	def click(self):
		self.coach.flipped = not self.coach.flipped



class ButtonImport(Button):
	def __init__(self , *kw):
		super().__init__(*kw)

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
	def __init__(self , *kw):
		super().__init__(*kw)

		self.image_path = C.DIR_ICONS + "\\btn_export.png"
		image_raw  = pygame.image.load(self.image_path)
		self.image = pygame.transform.rotozoom(
			image_raw,
			angle=90,
			scale=self.size[0]/image_raw.get_size()[0]
		)

		self.tooltip = "Export"

	def click(self):
		print("--")
		print(self.coach.reader.movetext)
		print("--")
		# # Information
		# title = self.coach.writers["TITLE"].text
		# date  = self.coach.writers["DATE"].text
		# white = self.coach.writers["WHITE"].text
		# black = self.coach.writers["BLACK"].text
		#
		# ### results
		# result = None
		# if self.coach.board.outcome[0] == "Checkmate":
		# 	if self.coach.board.outcome[1] == "White":
		# 		result = "1-0"
		# 	else:
		# 		result = "0-1"
		# elif self.coach.board.outcome[0] == "Draw":
		# 	result = ".5-.5"
		#
		# # File Handling
		# filename = title + "__" + date
		# gamedir  = C.DIR + "\\games\\" + filename + ".pgn"
		# with open(gamedir,"w") as file:
		# 	file.write("[Event \"" + title + "\"]\n")
		# 	file.write("[Date \""  + date  + "\"]\n")
		# 	file.write("[White \"" + white + "\"]\n")
		# 	file.write("[Black \"" + black + "\"]\n")
		# 	if result:
		# 		file.write("[Result \"" + result + "\"]\n")
		#
		# 	for line in self.coach.export_PGN():
		# 		file.write(line)
		#
		# 	if self.coach.board.outcome[1] in ("White","Black"):
		# 		file.write("#")
		# 	if result:
		# 		file.write("\n" + result)
		#
		# print(filename + ".pgn exported!")



class ButtonCoords(Button):
	def __init__(self , *kw):
		super().__init__(*kw)

		self.image_path = C.DIR_ICONS + "\\btn_coordinates.png"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path),
			self.size
		)

		self.tooltip = "Show coordinates"

	def click(self):
		self.active = not self.active
		self.colour = C.BUTTON_COLOUR_ACTIVE if self.active else C.BUTTON_COLOUR_NEUTRAL

		self.coach.board.show_coords = not self.coach.board.show_coords



class ButtonLegalMoves(Button):
	def __init__(self , *kw):
		super().__init__(*kw)

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
		self.colour = C.BUTTON_COLOUR_ACTIVE if self.active else C.BUTTON_COLOUR_NEUTRAL

		self.coach.board.show_legals = not self.coach.board.show_legals



class ButtonReset(Button):
	def __init__(self , *kw):
		super().__init__(*kw)

		self.image_path = C.DIR_ICONS + "\\btn_reset.png"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path),
			self.size
		)

		self.tooltip = "Reset"

	def click(self):
		if len(self.coach.board.movelog) > 1:
			self.coach.reset()



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
	def __init__(self , coach , title , text , font , x , y , context=None):
		self.coach   = coach
		self.title   = title
		self.text    = str(text)
		self.font    = font
		self.x       = x
		self.y       = y
		self.context = context


	def render(self):
		sz = self.font.size(self.text)
		bg = pygame.Surface((
			sz[0] + 8,
			sz[1] + 5
		))
		bg.fill((0,0,0))

		# Text
		self.coach.display.blit(
			self.font.render(self.title , True , (255,255,255)),
			(
				self.x + (5*len(self.text)) + 20,
				self.y + 3
			)
		)

		# Number
		self.coach.display.blit(
			bg,
			(self.x,self.y)
		)
		self.coach.display.blit(
			self.font.render(
				self.text,
				True,
				(255,255,255)
			),
			(self.x+4 , self.y+3)
		)



class Arrow:
	def __init__(self , coach , base , roof , girth=25):
		self.coach = coach
		self.girth = girth
		self.base  = base
		self.roof  = roof

		# Archery basics (needs to be recalculated every .shoot() so board can be flipped)
		self.nock = None
		self.head = None

		# Maths
		self.midline = None
		self.centre  = None

		# Rendering
		self.sprite = None


	def __str__(self):
		return str(self.base) + "->" + str(self.roof)


	def shoot(self):
		self.nock = pygame.math.Vector2(self.base.rect.center)
		self.head = pygame.math.Vector2(self.roof.rect.center)

		self.midline = self.head - self.nock
		self.centre  = (self.head + self.nock)/2

		if abs(self.midline.elementwise()) in [
			(100,200),
			(200,100)
		]:
			self.draw_knight()
		else:
			self.draw_direct()

		self.coach.display.blit(
			self.sprite,
			self.sprite.get_rect(center=self.centre)
		)


	def draw_knight(self):
		width  = abs(self.midline.x) + C.TILE_WIDTH
		height = abs(self.midline.y) + C.TILE_HEIGHT

		self.sprite = pygame.Surface(
			(width,height),
			pygame.SRCALPHA
		)

		# Draw as if upright ...
		### shafts
		pygame.draw.lines(
			self.sprite,
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
			self.sprite,
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
				self.sprite,
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

			self.sprite = pygame.transform.flip(
				self.sprite,
				self.midline.x < 0,
				self.midline.y < 0
			)

		else:
			pygame.draw.polygon(
				self.sprite,
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

			self.sprite = pygame.transform.flip(
				self.sprite,
				self.midline.x > 0,
				self.midline.y > 0
			)


	def draw_direct(self):
		height = self.midline.magnitude()

		self.sprite = pygame.Surface(
			(C.TILE_WIDTH,height),
			pygame.SRCALPHA
		)

		# Draw as if upright ...
		### shaft
		pygame.draw.line(
			self.sprite,
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
			self.sprite,
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
		self.sprite = pygame.transform.rotate(
			self.sprite,
			self.midline.angle_to((0,-1))
		)
