import pygame
import re

from data.Constants import C
from data.ECOdata import ECOdata



class Writer:
	all = []
	def __init__(self , coach , font_base , pretext='' , y_offset=0):
		Writer.all.append(self)
		self.coach     = coach
		self.font_base = font_base
		self.text      = pretext
		self.y_offset  = y_offset

		self.active    = False
		self.rect = pygame.Rect(
			C.TEXTBOX_X_OFFSET,
			self.y_offset,
			C.TEXTBOX_WIDTH,
			C.TEXTBOX_HEIGHT
		)


	def render(self , display):
		pygame.draw.rect(
			display,
			C.TEXTBOX_LIGHT if self.active else C.TEXTBOX_DARK,
			self.rect
		)
		display.blit(
			self.surf,
			(
				self.rect.x + 5,
				self.rect.y + 0.15*C.TEXTBOX_HEIGHT
			)
		)

	# Auto-updating surface property for easy rendering
	@property
	def surf(self):
		return self.font_base.render(
			self.text,
			True,
			(255,255,255)
		)



class Reader:
	all = []
	def __init__(self , coach , font_base , spacing_factor=15):
		Reader.all.append(self)
		self.coach     = coach
		self.font_base = font_base
		self.spacing_f = spacing_factor

		self.first_line = 0
		self.movetext   = []

		self.rect = pygame.Rect(
			C.TEXTBOX_X_OFFSET,
			50,
			C.TEXTBOX_WIDTH,
			200
		)


	def update(self , new_text):
		self.movetext = []
		for line in re.split(r"\s(?=\d\d?\d?\.)" , new_text):
			parts = line.strip().split(" ")
			# parts = ["1.", "d4", "c5"]
			parts[0] = parts[0].rjust(4)
			parts[1] = parts[1].ljust(7)

			self.movetext.append(" ".join(parts))

		self.first_line = max(len(self.movetext)-12 , 0)


	def scroll(self , nudge):
		self.first_line -= nudge

		final_line = len(self.movetext) - 3
		if len(self.movetext) <= 3:
			self.first_line = 0
		else:
			self.first_line = 0 if self.first_line < 0 else final_line if self.first_line > final_line else self.first_line


	def surf(self , line):
		return self.font_base.render(
			line,
			True,
			(255,255,255)
		)


	def render(self , display):
		# Movetext box
		pygame.draw.rect(
			display,
			C.TILE_DARK,
			self.rect
		)

		# Title box
		pygame.draw.rect(
			display,
			[c/3 for c in C.TILE_LIGHT],
			pygame.Rect(
				C.TEXTBOX_X_OFFSET,
				30,
				C.TEXTBOX_WIDTH,
				C.TEXTBOX_HEIGHT + 3
			)
		)

		# Multiline movetext
		for i,line in enumerate(self.movetext):
			if self.first_line <= i <= self.first_line + 12:
				display.blit(
					self.surf(line),
					(
						5 + self.rect.x,
						5 + self.rect.y - (15*self.first_line) + (15*i)
					)
				)



class Button:
	all = []
	def __init__(self , coach , action , x , y , context=None , size=C.BUTTON_SIZE , colour=C.BUTTON_COLOUR):
		Button.all.append(self)
		self.coach   = coach
		self.action  = action
		self.x       = x
		self.y       = y
		self.context = context
		self.size    = size
		self.colour  = colour

		self.active = False

		self.rect = pygame.Rect(
			self.x,
			self.y,
			*C.BUTTON_SIZE,
		)

		self.image_path = C.DIR_MEDIA + "/Icons/" + self.action.lower() + ".png"
		self.image = pygame.transform.scale(
			pygame.image.load(self.image_path).convert_alpha(),
			self.size
		)

	def click(self):
		self.active = not self.active

		if "SETTINGS" in self.action:
			if self.action.endswith("SHOW"):
				self.coach.settings.showing = True
			elif self.action.endswith("HIDE"):
				self.coach.settings.showing = False

		elif "STYLE" in self.action:
			if self.coach.settings.ddn_style.showing or self.action.endswith("_"):
				self.coach.settings.ddn_style.showing = not self.coach.settings.ddn_style.showing

				if not self.action.endswith("_"):
					C.PIECE_STYLE = self.action.split("_")[-1].title()
					C.DIR_SETS    = C.DIR_MEDIA + "\\Sets\\" + C.PIECE_STYLE + "\\"

					for tile in self.coach.board.all_tiles:
						if tile.occupant:
							if tile.occupant.creed:
								squish = (-15,-15) if C.PIECE_STYLE in ("3D",) else (-20,-20)
							else:
								squish = (-35,-35)
							image_size = [sum(l) for l in zip(C.TILE_SIZE,squish)]

							tile.occupant.image_path = C.DIR_SETS + tile.occupant.colour + "_" + tile.occupant.image_path.split("_")[-1]
							tile.occupant.image = pygame.image.load(tile.occupant.image_path)
							tile.occupant.image = pygame.transform.scale(tile.occupant.image , image_size)
							tile.render()

		elif "BOT_" in self.action:
			ddn = self.coach.settings.ddn_bot_white if "WHITE" in self.action else self.coach.settings.ddn_bot_black
			if ddn.showing or self.action.endswith("_"):
				ddn.showing = not ddn.showing

				if not self.action.endswith("_"):
					self.colour = (100,110,100) if self.active else C.BUTTON_COLOUR

					scheme = self.coach.engine.player_scheme["BLACK" in self.action]
					choice = self.action.split("_")[-1].title()
					self.coach.engine.player_scheme["BLACK" in self.action] = choice if scheme != choice else None
					print(self.coach.engine.player_scheme)

		elif "ECO" in self.action:
			self.coach.board_export_FEN()
			# if self.active:
			# 	self.colour = (100,110,100)
			# 	self.coach.eco = ECOdata(self.coach, C.DIR + "/ECO Catalogue.xlsm")
			# 	print("ECO loaded!")
			# else:
			# 	self.colour = C.BUTTON_COLOUR
			# 	self.coach.eco = None
			# 	print("ECO unloaded!")

		elif "FLIP" in self.action:
			self.coach.board_import_FEN("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBN b KQkq e3 3 2")
			#self.coach.board_flip()

		elif "EXPORT" in self.action:
			self.coach.board_export()

		elif "IMPORT" in self.action:
			from tkinter import Tk,filedialog
			base = Tk()
			base.withdraw()
			self.coach.board_import_PGN(filename=filedialog.askopenfilename(parent=base , title="Select PGN file"))


	def render(self , display):
		image_rect = self.image.get_rect(center=self.rect.center)

		pygame.draw.rect(
			display,
			self.colour,
			image_rect
		)
		display.blit(
			self.image,
			image_rect
		)

		# Piece style button tooltip:
		if "STYLE" in self.action and not self.action.endswith("_"):
			mouse_pos = pygame.mouse.get_pos()
			if self.rect.collidepoint(mouse_pos):
				display.blit(
					self.coach.reader_font.render(
						self.action.split("_")[-1].title() + " set",
						False,
						(0,0,0),
						(255,255,255,0)
					),
					(mouse_pos[0]+13 , mouse_pos[1]+10)
				)


class Dropdown:
	all = []
	def __init__(self , coach , trigger , options):
		Dropdown.all.append(self)
		self.coach   = coach
		self.trigger = trigger
		self.options = options

		self.showing = False
		self.choice  = None


	def render(self , display):
		if self.showing:
			for item in self.options:
				item.render(display)
