import time
import pygame

import tkinter as tk

from src.Constants import C,E





class Reader:
	def __init__(self , coach):
		self.coach 	= coach

		self.x = C.X_MARGIN
		self.y = C.Y_MARGIN + C.BUTTON_HEIGHT + C.TEXTBOX_HEIGHT + C.GRID_GAP

		# Interpreter
		self.movetext  = ''
		self.filepath  = ''
		self.catalogue = {}

		# Mechanics
		self.lineparts = []

		self.halfmove_offset = 0
		self.fullmove_offset = 0

		# Rendering
		self.columns = (
			(1/35)*C.TEXTBOX_WIDTH,
			(5/20)*C.TEXTBOX_WIDTH,
			(12.5/20)*C.TEXTBOX_WIDTH
		)

		self.first_line = 0

		self.head_font = pygame.font.SysFont("Consolas" , 13 , bold=True)
		self.text_font = pygame.font.SysFont("Consolas" , 13)

		self.rect = pygame.Rect(
			self.x,
			self.y + C.TEXTBOX_HEIGHT,
			C.TEXTBOX_WIDTH,
			(2/5)*C.BOARD_HEIGHT
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


	def imprint(self , part , floodlight=False):
		prose = self.text_font.render(
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

			return bg,prose
		else:
			return prose


	def update(self):
		self.lineparts = self.factorise(
			self.coach.board.movelog,
		)

		self.first_line = max(len(self.lineparts)-18 , 0)

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
		### head box
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
		### text box
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
				self.head_font.render(
					part[:30],				# Character limit of C.TEXTBOX_WIDTH
					True,
					(255,255,255)
				),
				(
					C.X_MARGIN + 5,
					C.Y_MARGIN + C.BUTTON_HEIGHT + C.GRID_GAP + i*C.TEXTBOX_HEIGHT + 3
				)
			)
		### movetext and floodlight
		for i,moveparts in enumerate(self.lineparts):
			if self.first_line <= i <= self.first_line + 20:
				for j,part in enumerate(moveparts):
					notation = self.imprint(
						part.rjust(4) if not j else part,
						(
							i == self.coach.board.movenum - (self.coach.board.ply == "w") - self.fullmove_offset - 1
							and
							j == 1 + (self.coach.board.ply == "w")
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


	def factorise(self , movelog):
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

		if self.halfmove_offset:
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



class Writer:
	def __init__(self , pane , x , y , width , pretext):
		self.pane    = pane
		self.x	     = x
		self.y	     = y
		self.width   = width
		self.pretext = pretext
		self.field   = ''

		self.active = False

		self.pre_font = pygame.font.SysFont("Consolas",13,italic=True)
		self.font     = pygame.font.SysFont("Consolas",13)

		self.rect   = pygame.Rect(
			self.x,
			self.y,
			self.width,
			C.TEXTBOX_HEIGHT
		)

	def render(self):
		pygame.draw.rect(
			self.pane,
			C.TEXTBOX_LIGHT if self.active else C.TEXTBOX_DARK,
			self.rect
		)

		dest = (
			self.rect.x + 5,
			self.rect.y + 0.15*C.TEXTBOX_HEIGHT
		)
		if self.field:
			self.pane.blit(
				self.font.render(self.field,True,(255,255,255)),
				dest
			)
		else:
			self.pane.blit(
				self.pre_font.render(self.pretext,True,(165,165,165)),
				dest
			)



class Counter:
	def __init__(self , pane , x , y , title , prefill=""):
		self.pane  = pane
		self.x     = x
		self.y     = y
		self.title = title
		self.field = prefill

		self.font  =  pygame.font.SysFont("Consolas",14,bold=True)

	def render(self):
		# Measurements
		sz = self.font.size(self.field)
		bg = pygame.Surface((
			sz[0] + 8,
			sz[1] + 5
		))
		bg.fill((0,0,0))

		# Field
		self.pane.blit(
			bg,
			(self.x,self.y)
		)
		self.pane.blit(
			self.font.render(self.field , True , (255,255,255)),
			(self.x+4 , self.y+3)
		)

		# Title
		self.pane.blit(
			self.font.render(self.title , True , (255,255,255)),
			(
				self.x + sz[0] + 15,
				self.y + 3
			)
		)



class Slider:
	all = []
	def __init__(self , display , x , y , size , metric , txform , domain , nrungs , trigger , vertical=False):
		Slider.all.append(self)
		self.display  = display
		self.x        = x
		self.y        = y
		self.size     = size
		self.metric   = metric
		self.txform   = txform               ### must be a format-ready string
		self.min_val  = domain[0]
		self.max_val  = domain[1]
		self.nrungs	  = nrungs
		self.trigger  = trigger
		self.vertical = vertical

		# Mechanics
		self.ratio = (eval(self.metric) - self.min_val) / (self.max_val - self.min_val)
		self.value = self.min_val + self.ratio*(self.max_val - self.min_val)

		self.min_pos = 0.075*self.size[1 if self.vertical else 0]
		self.max_pos = 0.925*self.size[1 if self.vertical else 0]

		# Rendering
		self.trackbed = pygame.Surface(self.size,pygame.SRCALPHA)

		if self.vertical:
			self.knob = pygame.Rect(
				self.size[0]/4,
				self.max_pos - self.ratio*(self.max_pos - self.min_pos) - 5,
				self.size[0]/2,
			10
			)
			self.rect = pygame.Rect(
				self.x,
				self.y + self.min_pos - 5,
				self.size[0],
				self.max_pos - self.min_pos + 10,
			)
		else:
			self.knob = pygame.Rect(
				self.min_pos + self.ratio*(self.max_pos - self.min_pos) - 5,
				self.size[1]/4,
				10,
				self.size[1]/2,
			)
			self.rect = pygame.Rect(
				self.x + self.min_pos - 5,
				self.y,
				self.max_pos - self.min_pos + 10,
				self.size[1]
			)


	def hold(self , pos):
		# Mechanics
		if self.vertical:
			self.ratio = round((self.nrungs-1) *
			    (pos[1] - self.rect.bottom) / (self.rect.top - self.rect.bottom)
			) / (self.nrungs-1)

			self.knob.centery = self.max_pos - self.ratio*(self.max_pos - self.min_pos)

		else:
			self.ratio = round((self.nrungs-1) *
			    (pos[0] - self.rect.left) / (self.rect.right - self.rect.left)
			) / (self.nrungs-1)

			self.knob.centerx = self.min_pos + self.ratio*(self.max_pos - self.min_pos)

		self.value = self.min_val + self.ratio*(self.max_val - self.min_val)

		# Function
		exec(
			self.metric + self.txform + str(self.value)
		)


	def render(self):
		self.trackbed.fill(C.SLIDER_COLOUR if self.trigger.active else (215,215,215,50))
		pygame.draw.rect(
			self.trackbed,
			C.BUTTON_BORDER,
			(0,0,*self.size),
			1
		)

		# Track & graduation
		if self.vertical:
			pygame.draw.line(
				self.trackbed,
				(0,0,0,1),
				(self.size[0]/2 , self.min_pos),
				(self.size[0]/2 , self.max_pos)
			)
			for i in range(self.nrungs):
				pygame.draw.line(
					self.trackbed,
					(0,0,0,1),
					( (4/9)*self.size[0]+1 , self.max_pos - (i/(self.nrungs-1))*(self.max_pos - self.min_pos) ),
					( (5/9)*self.size[0] , self.max_pos - (i/(self.nrungs-1))*(self.max_pos - self.min_pos) )
				)
		else:
			pygame.draw.line(
				self.trackbed,
				(0,0,0,5),
				(self.min_pos , self.size[1]/2),
				(self.max_pos , self.size[1]/2)
			)
			for i in range(self.nrungs):
				pygame.draw.line(
					self.trackbed,
					(0,0,0,1),
					( self.min_pos + (i/(self.nrungs-1))*(self.max_pos - self.min_pos) , (3/7)*self.size[1] ),
					( self.min_pos + (i/(self.nrungs-1))*(self.max_pos - self.min_pos) , (4/7)*self.size[1] )
				)

		# Handle
		pygame.draw.rect(
			self.trackbed,
			(75,75,75),
			self.knob
		)

		self.display.blit(self.trackbed, (self.x,self.y))


	def click(self):
		pass


	@property
	def value_nice(self):
		# Percentage
		# return f'{ 100 * round(self.ratio,4) :.0f}%'
		# (
		#
		# )

		# Integer
		return str(round(self.value))
		# (
		# 	0.85*C.BUTTON_WIDTH,
		# 	0.05*C.BUTTON_HEIGHT
		# )



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

		self.coach.screen.blit(
			self.sprite,
			self.sprite.get_rect(center=self.centre)
		)



# TODO: BUTTON IDEAS
#   1) force draws
#   2) top engine line(s) arrows
class Button:
	def __init__(self , display , x , y , size=C.BUTTON_SIZE , preactive=False):
		self.display = display
		self.x       = x
		self.y       = y
		self.size    = size
		self.active  = preactive

		self.colour = C.BUTTON_LIVE if self.active else C.BUTTON_DEAD

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
			self.display,
			self.colour,
			self.rect
		)
		self.display.blit(
			self.image,
			self.rect
		)

		# Tooltip
		if self.tooltip:
			mouse_pos = pygame.mouse.get_pos()
			if self.rect.collidepoint(mouse_pos):
				self.display.blit(
					self.font.render(
						self.tooltip,
						True,
						(0,0,0),
						(255,255,255,0)
					),
					(mouse_pos[0]+15 , mouse_pos[1]+10)
				)



class ButtonBot(Button):
	def __init__(self , *args , player , engine):
		super().__init__(*args)
		self.player = player
		self.engine = engine

		self.active = bool(self.engine.scheme[self.player == "BLACK"])

		self.image_path = C.DIR_ICONS + "bot_" + self.player.lower() + "_" + (
				self.engine.scheme[self.player == "BLACK"] or ""
		)
		self.image = pygame.transform.scale(
			pygame.image.load(self.image_path+".png"),
			self.size
		)

		self.options = [            ### NOT dropdown!!
			# ButtonOptionBot(
			# 	self.display,
			# 	self.x + 3*C.BUTTON_WIDTH + C.GRID_GAP/2,
			# 	self.y,
			# 	philosophy="STOCKFISH",
			# 	trigger=self
			# ),
			ButtonBotOption(
				self.display,
				self.x + 3*C.BUTTON_WIDTH + C.GRID_GAP/2,
				self.y,
				philosophy="HAL90",
				trigger=self
			),
			ButtonBotOption(
				self.display,
				self.x + 2*C.BUTTON_WIDTH + C.GRID_GAP/2,
				self.y,
				philosophy="Simple",
				trigger=self
			),
			ButtonBotOption(
				self.display,
				self.x + C.BUTTON_WIDTH + C.GRID_GAP/2,
				self.y,
				philosophy="Random",
				trigger=self
			),
		]
		### initial conditions
		self.colour = C.BUTTON_LIVE if self.active else C.BUTTON_IDLE
		for option in self.options:
			if self.engine.scheme[self.player == "BLACK"] == option.philosophy.upper():
				option.active = True
				option.colour = C.BUTTON_LIVE if option.active else C.BUTTON_DEAD

		self.slider = Slider(
			self.display,
			x=self.x,
			y=self.y + C.BUTTON_HEIGHT + C.GRID_GAP,
			size=(
				4*C.BUTTON_WIDTH + C.GRID_GAP/2,
				0.85*C.BUTTON_HEIGHT
			),
			metric="E.BOT_DEPTH_"+self.player.upper(),
			txform=" = ",
			domain=(1,4),
			nrungs=4,
			trigger=self,
		)

		self.font = pygame.font.SysFont("Consolas",13,bold=True)
		self.tooltip = self.player.title() + " bot"

	def click(self):
		pass

	def render(self):
		# Dropdown (always active)
		for option in self.options:
			option.render()

		# Myself
		super().render()

		# Slider
		if self.active:
			### show difficulty
			self.display.blit(
				self.font.render(
					self.slider.value_nice,
					True,
					(100,0,0)
				),
				(
					self.x + 0.75*C.BUTTON_WIDTH,
					self.y + 0.05*C.BUTTON_HEIGHT
				)
			)

		self.slider.render()



class ButtonBotOption(Button):
	def __init__(self , *args , philosophy , trigger):
		super().__init__(*args)
		self.philosophy = philosophy
		self.trigger 	= trigger

		self.engine = self.trigger.engine

		self.image_path = C.DIR_ICONS + "bot_" + self.trigger.player.lower() + "_" + self.philosophy.lower()
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path+".png"),
			self.size
		)

		self.tooltip = self.philosophy

	def click(self):
		# Mechanics
		for option in self.trigger.options:
			option.active = not option.active if option is self else False
			option.colour = C.BUTTON_LIVE if option.active else C.BUTTON_DEAD

		# Function
		incumbent = self.engine.scheme[self.trigger.player.upper() == "BLACK"]
		candidate = self.philosophy.upper()
		if candidate != incumbent:
			appointed = candidate
			self.trigger.active = True
			self.trigger.colour = C.BUTTON_LIVE
		else:
			appointed = None
			self.trigger.active = False
			self.trigger.colour = C.BUTTON_IDLE

		self.engine.scheme[self.trigger.player.upper() == "BLACK"] = appointed

		# Mechanics again
		self.trigger.image_path = C.DIR_ICONS + "bot_" + self.trigger.player.lower() + "_" + (
				appointed or ""
		)
		self.trigger.image = pygame.transform.scale(
			pygame.image.load(self.trigger.image_path+".png"),
			self.trigger.size
		)



class ButtonPieceStylist(Button):
	def __init__(self , *args , board):
		super().__init__(*args)
		self.board = board

		self.image_path = C.DIR_ICONS + "btn_ui_pstyle"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path+".png"),
			self.size
		)

		self.dropdown = [
			ButtonPieceStyleOption(
				self.display,
				self.x + 2*C.BUTTON_WIDTH + C.GRID_GAP/2,
				self.y + C.BUTTON_HEIGHT,
				style="8-Bit",
				trigger=self
			),
			ButtonPieceStyleOption(
				self.display,
				self.x + C.BUTTON_WIDTH + C.GRID_GAP/2,
				self.y + C.BUTTON_HEIGHT,
				style="FontAwesome",
				trigger=self
			),
			ButtonPieceStyleOption(
				self.display,
				self.x + 2*C.BUTTON_WIDTH + C.GRID_GAP/2,
				self.y,
				style="3D",
				trigger=self
			),
			ButtonPieceStyleOption(
				self.display,
				self.x + C.BUTTON_WIDTH + C.GRID_GAP/2,
				self.y,
				style="Classic",
				trigger=self
			),
		]
		### initial conditions
		for option in self.dropdown:
			if C.PIECE_STYLE == option.style.upper():
				option.active = True
				option.colour = C.BUTTON_LIVE

		self.tooltip = "Piece style"

	def click(self):
		self.active = not self.active

	def render(self):
		if self.active:
			self.colour = C.BUTTON_IDLE
			for option in self.dropdown:
				option.render()
		else:
			self.colour = C.BUTTON_DEAD

		super().render()



class ButtonPieceStyleOption(Button):
	def __init__(self , *args , style , trigger):
		super().__init__(*args)
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
		for option in self.trigger.dropdown:
			option.active = option is self
			option.colour = C.BUTTON_LIVE if option is self else C.BUTTON_DEAD

		# Function
		C.PIECE_STYLE = self.style.upper()
		C.DIR_SET     = C.DIR_MEDIA + "sets\\" + C.PIECE_STYLE + "\\"
		for man in self.trigger.board.all_men():
			man.image_path = C.DIR_SET + man.colour + "_" + man.image_path.split("_")[-1]
			man.image = pygame.image.load(man.image_path)
			man.image = pygame.transform.scale(man.image,man.image_size)



class ButtonBoardStylist(Button):
	def __init__(self , *args , board):
		super().__init__(*args)
		self.board = board

		self.image_path = C.DIR_ICONS + "\\btn_ui_bstyle"
		image_raw  = pygame.image.load(self.image_path+".png")
		self.image = pygame.transform.rotozoom(
			image_raw,
			angle=90,
			scale=self.size[0]/image_raw.get_size()[0]
		)

		self.dropdown = [
			ButtonBoardStyleOption(
				self.display,
				self.x + C.BUTTON_WIDTH + C.GRID_GAP/2,
				self.y + C.BUTTON_HEIGHT,
				style="BLEAK",
				trigger=self,
			),
			ButtonBoardStyleOption(
				self.display,
				self.x + 2*C.BUTTON_WIDTH + C.GRID_GAP/2 - 1,      ### regular spacing shows a 1px gap???
				self.y,
				style="CHEAP",
				trigger=self,
			),
			ButtonBoardStyleOption(
				self.display,
				self.x + C.BUTTON_WIDTH + C.GRID_GAP/2,
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
			self.colour = C.BUTTON_IDLE
			for option in self.dropdown:
				option.render()
		else:
			self.colour = C.BUTTON_DEAD

		super().render()



class ButtonBoardStyleOption(Button):
	def __init__(self , *args , style , trigger):
		super().__init__(*args)
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
			option.colour = C.BUTTON_LIVE if option.active else C.BUTTON_DEAD

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
			self.display,
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
			self.display,
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
			self.display,
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
			self.display,
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
				self.display.blit(
					self.font.render(
						self.tooltip,
						False,
						(0,0,0),
						(255,255,255,0)
					),
					(mouse_pos[0]+15 , mouse_pos[1]+10)
				)



class ButtonContextOpen(Button):
	def __init__(self , *args , context , coach):
		super().__init__(*args)
		self.context = context
		self.coach   = coach

		self.image_path = C.DIR_ICONS + "\\context_" + str(self.context).lower()
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path+".png"),
			self.size
		)

		self.tooltip = str(self.context).title()

	def click(self):
		for context in self.coach.contexts:
			context.show = context is self.context



class ButtonContextShut(Button):
	def __init__(self , *args , coach):
		super().__init__(*args)
		self.coach = coach

		self.scale = 0.85

		self.x   += (1-self.scale)*C.BUTTON_WIDTH/2
		self.y   += (1-self.scale)*C.BUTTON_HEIGHT/2
		self.size = [self.scale*l for l in C.BUTTON_SIZE]
		self.rect = pygame.Rect(
			self.x,
			self.y,
			*self.size
		)

		self.colour = (85,75,75)

		self.image_path = C.DIR_ICONS + "btn_shut"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path+".png"),
			self.size
		)

		self.tooltip = "Exit"

	def click(self):
		for context in self.coach.contexts:
			context.show = False



class ToggleTray(Button):
	def __init__(self , *args , coach):
		super().__init__(*args)
		self.coach = coach

		self.cache = None

		self.backgr = pygame.Rect(
			self.x,
			self.y,
			self.size[0]/2,
			self.size[1]
		)

		self.image_path = C.DIR_ICONS + "btn_tray_open.png"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path),
			self.size
		)

		self.tooltip = "Tray open"


	def click(self):
		self.active = not self.active

		if self.active:
			self.colour  = C.BUTTON_LIVE
			self.tooltip = "Tray open"

			self.image_path = C.DIR_ICONS + "btn_tray_open.png"
			self.image      = pygame.transform.scale(
				pygame.image.load(self.image_path),
				self.size
			)

			self.cache , self.coach.tray = self.coach.tray , self.cache
			self.coach.screen = pygame.display.set_mode(C.WINDOW_SIZE)

		else:
			self.colour  = C.BUTTON_DEAD
			self.tooltip = "Tray shut"

			self.image_path = C.DIR_ICONS + "btn_tray_shut.png"
			self.image      = pygame.transform.scale(
				pygame.image.load(self.image_path),
				self.size
			)

			self.cache , self.coach.tray = self.coach.tray , self.cache
			self.coach.screen = pygame.display.set_mode((C.SIDEBAR_WIDTH + C.BOARD_WIDTH , C.BOARD_HEIGHT))



	def render(self):
		pygame.draw.rect(
			self.display,
			self.colour,
			self.backgr
		)
		self.display.blit(
			self.image,
			self.rect
		)

		# Tooltip
		if self.tooltip:
			mouse_pos = pygame.mouse.get_pos()
			if self.rect.collidepoint(mouse_pos):
				self.display.blit(
					self.font.render(
						self.tooltip,
						True,
						(0,0,0),
						(255,255,255,0)
					),
					(mouse_pos[0]+15 , mouse_pos[1]+10)
				)



class ButtonPrevious(Button):
	def __init__(self , *args , coach):
		super().__init__(*args)
		self.coach = coach

		self.image_path = C.DIR_ICONS + "\\btn_prev.png"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path),
			self.size
		)

		self.tooltip = "Previous"

	def click(self):
		# print("--- PREV ---")
		# print(self.coach.board.this_move)
		# print(self.coach.board.last_move if self.coach.board.last_move else "-")
		# print(self.coach.board.halfmovenum,self.coach.board.movenum,self.coach.board.movelog)
		# print("------------")

		if self.coach.board.halfmovenum > 1:
			last_move = self.coach.board.movelog[self.coach.board.halfmovenum - 2]
			if self.coach.board.halfmovenum > 2:
				past_move = self.coach.board.movelog[self.coach.board.halfmovenum - 3]
			else:
				past_move = None

			# Board mechanics
			self.coach.board.halfmovenum -= 1
			self.coach.import_FEN(last_move.fen)
			self.coach.board.this_move = last_move
			self.coach.board.last_move = past_move

			# Move mechanics
			unmove = last_move.rewind()

			cache = self.coach.board.tile(unmove.target).occupant
			cache.position = unmove.target.position
			self.coach.board.tile(unmove.target).occupant = None

			unmove.animate()

			self.coach.board.tile(unmove.target).occupant = cache

			# Calibrate
			self.coach.board.calibrate()

		# print(self.coach.board.this_move)
		# print(self.coach.board.last_move if self.coach.board.last_move else "-")
		# print(self.coach.board.halfmovenum,self.coach.board.movenum,self.coach.board.movelog)
		# print("------------")
		# print()



class ButtonNext(Button):
	def __init__(self , *args , coach):
		super().__init__(*args)
		self.coach = coach

		self.image_path = C.DIR_ICONS + "\\btn_next.png"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path),
			self.size
		)

		self.tooltip = "Next"

	def click(self):
		# print("--- NEXT ---")
		# print(self.coach.board.this_move)
		# print(self.coach.board.last_move if self.coach.board.last_move else "-")
		# print(self.coach.board.halfmovenum,self.coach.board.movenum,self.coach.board.movelog)
		# print("---      ---")

		if self.coach.board.halfmovenum < len(self.coach.board.movelog):
			next_move = self.coach.board.movelog[self.coach.board.halfmovenum]
			this_move = self.coach.board.movelog[self.coach.board.halfmovenum - 1]

			# Board mechanics
			self.coach.board.halfmovenum += 1
			self.coach.import_FEN(next_move.fen)
			self.coach.board.this_move = next_move
			self.coach.board.last_move = this_move

			# Move mechanics
			cache = self.coach.board.tile(this_move.target).occupant
			cache.position = this_move.target.position
			if this_move.ep:
				self.coach.board.tile(this_move.target).occupant = None
				self.coach.board.tile(this_move.ep).occupant 	= this_move.capture
			else:
				self.coach.board.tile(this_move.target).occupant = this_move.capture

			this_move.animate()

			self.coach.board.tile(this_move.target).occupant = cache
			if this_move.ep:
				self.coach.board.tile(this_move.ep).occupant = None

			# Calibrate
			self.coach.board.calibrate()

		# print(self.coach.board.this_move)
		# print(self.coach.board.last_move if self.coach.board.last_move else "-")
		# print(self.coach.board.halfmovenum,self.coach.board.movenum,self.coach.board.movelog)
		# print("------------")
		# print()



class ButtonECOI(Button):
	def __init__(self , *args , reader):
		super().__init__(*args)
		self.reader = reader

		self.image_path = C.DIR_ICONS + "\\btn_ui_ecoi.png"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path),
			self.size
		)

		self.tooltip = "Interpret opening"

	def click(self):
		if self.active:
			self.active = False
			self.colour = C.BUTTON_LIVE if self.active else C.BUTTON_DEAD

			self.reader.unload()

		else:
			self.active = True
			self.colour = C.BUTTON_LIVE if self.active else C.BUTTON_DEAD

			self.reader.load()
			self.reader.update()



class ButtonImport(Button):
	def __init__(self , *args , coach):
		super().__init__(*args)
		self.coach = coach

		self.image_path = C.DIR_ICONS + "\\btn_import.png"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path),
			self.size
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

		# PGN
		if D.choice == "PGN":
			from tkinter import filedialog

			if filename := filedialog.askopenfilename(
				parent=root,
				title="Import PGN"
			):
				self.coach.reset()
				self.coach.import_PGN(filename)

		# FEN
		elif D.choice == "FEN":
			from tkinter import simpledialog

			if fen_in := simpledialog.askstring(
				parent=root,
				title="Import FEN",
				prompt="\t"*8
			) or C.IMPORT_FEN_DEFAULT:

				print(fen_in)

				### import/export movenum correction:
				self.coach.reader.fullmove_offset = int(fen_in.split()[5])

				self.coach.reset(fen=fen_in)

		# Refocus pygame window
		root.destroy()



class ButtonExport(Button):
	def __init__(self , *args , coach):
		super().__init__(*args)
		self.coach = coach

		self.image_path = C.DIR_ICONS + "\\btn_export.png"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path),
			self.size
		)

		self.tooltip = "Export"

	def click(self):
		self.coach.engine.play_simple()

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
		# 	result = "½-½"
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
		# 	if self.coach.board.outcome[1] in ("White", "Black"):
		# 		file.write("#")
		# 	if result:
		# 		file.write("\n" + result)
		#
		# print(filename + ".pgn exported!")



class ButtonFlip(Button):
	def __init__(self , *args , coach):
		super().__init__(*args)
		self.coach = coach

		self.image_path = C.DIR_ICONS + "\\btn_ui_flip.png"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path),
			self.size
		)

		self.tooltip = "Flip board"

	def click(self):
		C.BOARD_FLIPPED = not C.BOARD_FLIPPED

		# Collateral flips
		w_bot = self.coach.buttons["BOT_WHITE"]
		b_bot = self.coach.buttons["BOT_BLACK"]

		w_clock = self.coach.clock.whiteface
		b_clock = self.coach.clock.blackface

		w_graves = self.coach.graveyard.w_rect
		b_graves = self.coach.graveyard.b_rect
		w_plaque = self.coach.graveyard.w_plaque
		b_plaque = self.coach.graveyard.b_plaque

		for a,b in zip(
			[ w_bot , w_bot.slider , *w_bot.options , w_clock , w_clock.timer , w_graves , w_plaque ],
			[ b_bot , b_bot.slider , *b_bot.options , b_clock , b_clock.timer , b_graves , b_plaque ],
		):
			a.x , b.x = a.x , a.x
			a.y , b.y = b.y , a.y

			try:
				a.rect , b.rect = b.rect , a.rect
			except AttributeError:
				pass



class ButtonFreshMoves(Button):
	def __init__(self , *args , board):
		super().__init__(*args)
		self.board = board

		self.image_path = C.DIR_ICONS + "\\btn_ui_fresh_moves.png"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path),
			self.size
		)

		self.tooltip = "Show recent moves"

	def click(self):
		self.active = not self.active
		self.colour = C.BUTTON_LIVE if self.active else C.BUTTON_DEAD

		C.SHOW_MOVE_FRESH = not C.SHOW_MOVE_FRESH



class ButtonLegalMoves(Button):
	def __init__(self , *args , board):
		super().__init__(*args)
		self.board = board

		self.image_path = C.DIR_ICONS + "\\btn_ui_legal_moves.png"
		image_raw  = pygame.image.load(self.image_path)
		self.image = pygame.transform.rotozoom(
			image_raw,
			angle=45,
			scale=self.size[0]/(image_raw.get_size()[0]*(2**.5))
		)

		self.tooltip = "Show legal moves"

	def click(self):
		self.active = not self.active
		self.colour = C.BUTTON_LIVE if self.active else C.BUTTON_DEAD

		C.SHOW_MOVE_LEGAL = not C.SHOW_MOVE_LEGAL



class ButtonCoords(Button):
	def __init__(self , *args , board):
		super().__init__(*args)
		self.board = board

		self.image_path = C.DIR_ICONS + "\\btn_ui_coordinates.png"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path),
			self.size
		)

		self.tooltip = "Show coordinates"

	def click(self):
		self.active = not self.active
		self.colour = C.BUTTON_LIVE if self.active else C.BUTTON_DEAD

		C.SHOW_TILE_COORD = not C.SHOW_TILE_COORD



class ButtonReset(Button):
	def __init__(self , *args , coach):
		super().__init__(*args)
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
	def __init__(self , *args):
		super().__init__(*args)
		self.image_path = C.DIR_ICONS + "btn_ui_spedometer" + str(int(C.MOVE_SPEED))
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path+".png"),
			self.size
		)

		self.dropdown = [
			Slider(
				self.display,
				x=self.x + 1.085*C.BUTTON_WIDTH + C.GRID_GAP,      ### .085 looks best even tho it's not actually centered
				y=self.y - C.BUTTON_HEIGHT,
				size=(
					0.85*C.BUTTON_WIDTH,
					3*C.BUTTON_HEIGHT,
				),
				metric="C.MOVE_SPEED",
				txform=" = 50/",
				domain=(1,10),
				nrungs=10,
				trigger=self,
				vertical=True
			),
		]

		self.tooltip = "Animation speed"

	def click(self):
		self.active = not self.active

	def render(self):
		# Slider is in dropdown
		if self.active:
			self.colour = C.BUTTON_IDLE
			for option in self.dropdown:
				option.render()
		else:
			self.colour = C.BUTTON_DEAD

		# Slider changes trigger image
		if pygame.mouse.get_pressed() and (slider := self.dropdown[0]).rect.collidepoint(pygame.mouse.get_pos()):
			self.image_path = C.DIR_ICONS + "btn_ui_spedometer" + str(int(slider.value))
			self.image      = pygame.transform.scale(
				pygame.image.load(self.image_path+".png"),
				self.size
			)

		super().render()



class ButtonAutoPromo(Button):
	def __init__(self , *args):
		super().__init__(*args)

		self.names = {
			"Q"  : "Queen",
			"R"  : "Rook",
			"B"  : "Bishop",
			"N"  : "Knight",
		}

		self.image_path = C.DIR_SETS + "promo_" + (self.names[C.AUTO_PROMOTE].lower() or "pawn")
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path+".png"),
			self.size
		)

		self.dropdown = [
			ButtonOptionAutoPromo(
				self.display,
				self.x + 2*C.BUTTON_WIDTH + C.GRID_GAP/2,
				self.y + C.BUTTON_HEIGHT,
				creed="N",
				trigger=self
			),
			ButtonOptionAutoPromo(
				self.display,
				self.x + C.BUTTON_WIDTH + C.GRID_GAP/2,
				self.y + C.BUTTON_HEIGHT,
				creed="B",
				trigger=self
			),
			ButtonOptionAutoPromo(
				self.display,
				self.x + 2*C.BUTTON_WIDTH + C.GRID_GAP/2,
				self.y,
				creed="R",
				trigger=self
			),
			ButtonOptionAutoPromo(
				self.display,
				self.x + C.BUTTON_WIDTH + C.GRID_GAP/2,
				self.y,
				creed="Q",
				trigger=self
			),
		]
		### initial conditions
		for option in self.dropdown:
			if option.creed.upper() == C.AUTO_PROMOTE:
				option.active = True
				option.colour = C.BUTTON_LIVE

		if C.AUTO_PROMOTE:
			self.tooltip = "Auto-" + self.names[C.AUTO_PROMOTE]
		else:
			self.tooltip = "Ask to promote"

	def click(self):
		self.active = not self.active

	def render(self):
		if self.active:
			self.colour = C.BUTTON_IDLE
			for option in self.dropdown:
				option.render()
		else:
			self.colour = C.BUTTON_DEAD

		if C.AUTO_PROMOTE:
			self.colour = C.BUTTON_LIVE

		super().render()



class ButtonOptionAutoPromo(Button):
	def __init__(self , *args , creed , trigger):
		super().__init__(*args)
		self.creed   = creed
		self.trigger = trigger

		self.name = self.trigger.names[self.creed]

		self.image_path = C.DIR_SETS + "agnostic_" + self.name.lower()
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path+".png"),
			self.size
		)

		self.tooltip = self.name.title()

	def click(self):
		# Mechanics
		self.trigger.active = False

		### single-select voluntary dropdown
		for option in self.trigger.dropdown:
			option.active = not option.active if option is self else False
			option.colour = C.BUTTON_LIVE if option.active else C.BUTTON_DEAD

		# Function
		C.AUTO_PROMOTE = None if self.creed.upper() == C.AUTO_PROMOTE else self.creed.upper()

		# Mechanics again
		if C.AUTO_PROMOTE:
			self.trigger.image_path = C.DIR_SETS + "promo_" + self.name.lower()
			self.tooltip = "Auto-" + self.name.title()
		else:
			self.trigger.image_path = C.DIR_SETS + "promo_pawn"
			self.tooltip = "Ask to promote"

		self.trigger.image = pygame.transform.scale(
			pygame.image.load(self.trigger.image_path+".png"),
			self.trigger.size
		)



class ButtonClockFace(Button):
	def __init__(self , *args , player , clock):
		super().__init__(*args)
		self.player = player
		self.clock  = clock

		self.image_path = C.DIR_ICONS + "btn_clock_" + self.player.lower() + ".png"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path),
			self.size
		)

		self.timer = Timer(
			self.display,
			self.x - C.BUTTON_WIDTH/2,
			(
				self.y - (5/6)*C.BUTTON_HEIGHT - 2*C.GRID_GAP,
				self.y + C.BUTTON_HEIGHT + 2*C.GRID_GAP
			)[self.player=="BLACK"],
			self.player,
			90,0,
			trigger=self
		)

		self.tooltip = self.player.title() + " clock"


	def click(self):
		if self.clock.link.active:
			ply_is_white = self.clock.coach.board.ply == "w"

			white = self.clock.whiteface
			black = self.clock.blackface

			white.active = black.active = not white.active

			if white.active and black.active:
				white.colour = black.colour = C.BUTTON_LIVE

				white.timer.colour = C.TIMER_LIVE if ply_is_white else C.TIMER_IDLE
				black.timer.colour = C.TIMER_IDLE if ply_is_white else C.TIMER_LIVE

			else:
				white.colour       = black.colour       = C.BUTTON_DEAD
				white.timer.colour = black.timer.colour = C.TIMER_DEAD

		else:
			self.active = not self.active

			if self.active:
				self.colour       = C.BUTTON_LIVE
				self.timer.colour = C.TIMER_LIVE if self.player[0].lower() == self.clock.coach.board.ply else C.TIMER_IDLE
			else:
				self.colour       = C.BUTTON_DEAD
				self.timer.colour = C.TIMER_DEAD

		# Commence move when activating clock
		if self.active:
			this_move = self.clock.coach.board.this_move
			this_move.commence = this_move.commence or (
				self.clock.whiteface.timer.time,
				self.clock.blackface.timer.time,
			)[self.player=="BLACK"]


	def render(self):
		# Button
		pygame.draw.rect(
			self.display,
			self.colour,
			self.rect
		)
		self.display.blit(
			self.image,
			self.rect
		)

		# Timer
		self.timer.render()

		# Tooltip
		mouse_pos = pygame.mouse.get_pos()
		local_pos = (
			mouse_pos[0] + C.TRAY_PAD - C.SIDEBAR_WIDTH - C.BOARD_WIDTH,
			mouse_pos[1],
		)
		if self.rect.collidepoint(local_pos):
			tltip_pos = (
				local_pos[0] + (15 if local_pos[0] < 0.588*C.TRAY_WIDTH else -7.3*len(self.tooltip)),
				local_pos[1] + 10
			)
			self.display.blit(
				self.font.render(
					self.tooltip,
					True,
					(0,0,0),
					(255,255,255,0)
				),
				tltip_pos
			)



class ButtonClockLink(Button):
	def __init__(self , *args , clock):
		super().__init__(*args)
		self.clock = clock

		self.image_path = C.DIR_ICONS + "\\btn_link.png"
		self.image      = pygame.transform.scale(
			pygame.image.load(self.image_path),
			self.size
		)

		self.tooltip = "Link"

	def click(self):
		self.active = not self.active
		self.colour = C.BUTTON_LIVE if self.active else C.BUTTON_DEAD

		self.clock.blackface.active = self.clock.whiteface.active
		self.clock.blackface.colour = self.clock.whiteface.colour

	def render(self):
		# Button
		pygame.draw.rect(
			self.display,
			self.colour,
			self.rect
		)
		self.display.blit(
			self.image,
			self.rect
		)

		# Tooltip
		mouse_pos = pygame.mouse.get_pos()
		local_pos = (
			mouse_pos[0] + C.TRAY_PAD - C.SIDEBAR_WIDTH - C.BOARD_WIDTH,
			mouse_pos[1],
		)
		if self.rect.collidepoint(local_pos):
			self.display.blit(
				self.font.render(
					self.tooltip,
					True,
					(0,0,0),
					(255,255,255,0)
				),
				(local_pos[0]+15,local_pos[1]+10)
			)



# TODO: ADD SCRAMBLE MODE FOR t<10
class Timer:
	def __init__(self , display , x , y , player , start , bonus , trigger):
		self.display = display
		self.x       = x
		self.y       = y
		self.player  = player
		self.start   = start
		self.bonus   = bonus
		self.time    = 60*start + bonus
		self.trigger = trigger

		self.colour = C.TIMER_DEAD
		self.size   = (
			(9/4)*C.BUTTON_WIDTH,
			(5/6)*C.BUTTON_HEIGHT,
		)

		self.font = pygame.font.SysFont("Consolas",28)

		self.frame = pygame.Surface(self.size,pygame.SRCALPHA)
		self.body  = pygame.Rect(0,0,*self.size)
		self.face  = pygame.Rect(
			0.06*self.body.width,
			0.075*self.body.height,
			0.88*self.body.width,
			0.85*self.body.height,
		).move(1,1)                     ### corrections needed for some reason...


	def render(self):
		self.frame.fill((0,0,0,0))

		pygame.draw.rect(
			self.frame,
			(150,150,150),
			self.body,
			border_radius=8
		)
		pygame.draw.rect(
			self.frame,
			self.colour,
			self.face,
			border_radius=5
		)

		### time
		read = self.font.render(self.reading,True,(255,255,255))
		read.set_alpha(215)
		self.frame.blit(
			read,
			read.get_rect(center=[self.size[0]/2 , 2.5+self.size[1]/2])
		)

		self.display.blit(self.frame , (self.x-6,self.y-2))         ### pygame .scale() needs correcting... not sure why


	@property
	def reading(self):
		mins,secs = divmod(self.time,60)
		return  str(mins).zfill(2) + ":" + str(secs).zfill(2)



class Graveyard:
	def __init__(self , coach):
		self.coach = coach

		self.font = pygame.font.SysFont("Consolas",12)

		self.whites = {
			""  : [],
			"N" : [],
			"B" : [],
			"R" : [],
			"Q" : [],
		}
		self.blacks = {
			""  : [],
			"N" : [],
			"B" : [],
			"R" : [],
			"Q" : [],
		}

		# Shrines
		self.w_shrine = pygame.Surface((1.5*C.BUTTON_WIDTH , 1.5*C.TILE_HEIGHT),pygame.SRCALPHA)
		self.b_shrine = pygame.Surface((1.5*C.BUTTON_WIDTH , 1.5*C.TILE_HEIGHT),pygame.SRCALPHA)

		self.w_rect = pygame.Rect(
			C.TRAY_PAD,
			0,
			C.BUTTON_WIDTH,
			1.5*C.TILE_HEIGHT
		)
		self.b_rect = pygame.Rect(
			C.TRAY_PAD,
			6.5*C.TILE_HEIGHT,
			C.BUTTON_WIDTH,
			1.5*C.TILE_HEIGHT
		)

		# Plaque
		self.mat_val = 0
		self.w_plaque = pygame.Rect(
			C.TRAY_PAD + C.GRID_GAP,
			1.5*C.TILE_HEIGHT + C.GRID_GAP,
			25,
			9                       ### approx height of Consolas at size 12
		)
		self.b_plaque = pygame.Rect(
			C.TRAY_PAD + C.GRID_GAP,
			6.5*C.TILE_HEIGHT - 9 - C.GRID_GAP,
			25,
			9
		)


	def render(self):
		# Shrines
		self.w_shrine.fill((30,25,25,115) , (0,0,C.BUTTON_WIDTH,1.5*C.TILE_HEIGHT))
		self.b_shrine.fill((75,70,70,115) , (0,0,C.BUTTON_WIDTH,1.5*C.TILE_HEIGHT))

		for graveyard,shrine in [
			(self.whites , self.w_shrine),
			(self.blacks , self.b_shrine)
		]:
			r = 0
			for creed,graves in graveyard.items():
				if graves:
					for c,grave in enumerate(graves):
						shrine.blit(
							pygame.transform.scale(
								pygame.image.load(grave.image_path),
								(25,25)
							),
							(
								(5 +  8*c),
								(8 + 25*r),
							)
						)
					r += 1

		self.coach.tray.blits([
			(self.w_shrine,self.w_rect),
			(self.b_shrine,self.b_rect),
		])

		# Material balance
		if self.mat_val > 0:
			self.coach.tray.blit(
				self.font.render("+"+str(abs(self.mat_val)) , True , (185,185,185)),
				self.b_plaque
			)
		elif self.mat_val < 0:
			self.coach.tray.blit(
				self.font.render("+"+str(abs(self.mat_val)) , True , (185,185,185)),
				self.w_plaque
			)


	def bury(self , fallen):
		if fallen.colour == "w":
			self.whites[fallen.creed].append(fallen)
			self.mat_val -= E.SCOREBOARD_MATERIAL[fallen.creed or "P"]
		else:
			self.blacks[fallen.creed].append(fallen)
			self.mat_val += E.SCOREBOARD_MATERIAL[fallen.creed or "P"]


	def update(self):
		self.mat_val = 0
		for graveyard in (self.whites,self.blacks):
			for creed,graves in graveyard.items():
				graveyard[creed].clear()

		for move in self.coach.board.movelog[:self.coach.board.halfmovenum - 1]:
			if move.capture:
				self.bury(move.capture)
