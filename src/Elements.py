import pygame

import tkinter as tk

from src.Constants import C,E





class Reader:
	def __init__(self , coach):
		self.coach 	= coach

		self.x = C.X_MARGIN
		self.y = C.Y_MARGIN + C.BUTTON_HEIGHT + C.TEXTBOX_HEIGHT + C.GRID_GAP

		self.catalogue = {}

		self.lineparts = []
		self.movetext  = ''

		self.halfmove_offset = 0
		self.fullmove_offset = 0

		# Rendering
		self.columns = (
			(1/35)*C.TEXTBOX_WIDTH,
			(5/20)*C.TEXTBOX_WIDTH,
			(12.5/20)*C.TEXTBOX_WIDTH
		)

		self.first_line = 0
		self.height     = (2/5)*C.BOARD_HEIGHT

		self.head_font = pygame.font.SysFont("Consolas" , 13 , bold=True)
		self.text_font = pygame.font.SysFont("Consolas" , 13)

		self.rect = pygame.Rect(
			self.x,
			self.y + C.TEXTBOX_HEIGHT,
			C.TEXTBOX_WIDTH,
			self.height
		)

		# Mechanics
		self.load()

	def unload(self):
		self.catalogue.clear()

	def load(self , filepath=C.DIR+"\\data\\openings\\catalogue.tsv"):
		import csv

		with open(filepath,"r") as file:
			for row in csv.reader(file,delimiter="\t"):
				if self.movetext in row[2]:
					self.catalogue[ row[2] ] = row[1]

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

	def render(self):
		# Boxes
		### title box
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
		titleparts = self.coach.board.opening.split(": ")   ### my version of the data doesn't include subvariants, so max 1 ":"
		for i,part in enumerate(titleparts):
			if len(titleparts) > i+1:
				part += ","

			self.coach.pane.blit(
				self.head_font.render(
					part[:30],				                ### character limit for C.TEXTBOX_WIDTH
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
			if self.first_line <= i <= self.first_line + 17:
				for j,part in enumerate(moveparts):
					notation = self.imprint(
						part.rjust(4) if not j else part,
						(
							i == self.coach.board.movenum - (self.coach.board.ply == "w") - self.fullmove_offset
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

	def update(self):
		### .lineparts shows entire movelog
		self.lineparts = self.factorise(self.coach.board.movelog)

		self.first_line = max(len(self.lineparts)-18 , 0)

		### .movetext (for ECOI, Board.opening, etc.) respects turn controls
		self.movetext = " ".join(
			[" ".join(line) for line in self.factorise(
				self.coach.board.movelog[:self.coach.board.halfmovenum]
			)]
		)

		update = ""
		if self.movetext:
			try:
				update = self.catalogue[self.movetext]
			except KeyError:
				pass

		### idle movetext
		# elif self.coach.buttons_turns["ECOInterpreter"].active:
		# 	### full ellipsis during turn controls (only relevant at turn 0 if dreaming, or before first tick if not)
		# 	update = "..." if len(self.coach.board.movelog) > 1 else "."

		self.coach.board.opening = update or self.coach.board.opening

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
	def __init__(self , context , display , x , y , w , h , pretext=None):
		self.context = context
		self.display = display
		self.x	     = x
		self.y	     = y
		self.w       = w
		self.h       = h
		self.pretext = pretext

		self.field   = ''

		self.active = False
		self.colour = C.TEXTBOX_LIGHT if self.active else C.TEXTBOX_DARK

		self.pre_font = pygame.font.SysFont("Consolas",13,italic=True)
		self.font     = pygame.font.SysFont("Consolas",13)

		self.rect   = pygame.Rect(
			self.x,
			self.y,
			self.w,
			self.h
		)

	def render(self):
		pygame.draw.rect(
			self.display,
			self.colour,
			self.rect
		)

		if self.field:
			font , colour = self.font , (255,255,255)
		else:
			font , colour = self.pre_font , (185,185,185)

		self.display.blit(
			font.render(self.text,True,colour),
			(
				self.rect.x + 5,
				self.rect.y + 0.15*C.TEXTBOX_HEIGHT
			)
		)

	def click(self):
		for writer in self.context.writers.values():
			writer.active = not self.active if writer is self else False
			writer.colour = C.TEXTBOX_LIGHT if writer.active else C.TEXTBOX_DARK

	def type(self , event):
		if event.key == pygame.K_BACKSPACE:
			if self.field:
				self.field = self.field[:-1]
			else:
				self.kill()
		elif event.key == pygame.K_RETURN:
			self.kill()
		else:
			self.field += event.unicode

	def kill(self):
		self.active = False
		self.colour = C.TEXTBOX_LIGHT if self.active else C.TEXTBOX_DARK

	def paint(self):
		self.colour = C.TEXTBOX_LOOM if self.active else C.TEXTBOX_DARK

	@property
	def text(self):
		return self.field or self.pretext



class Counter:
	def __init__(self , context , x , y , label , polarise=False):
		self.context  = context
		self.x        = x
		self.y        = y
		self.label    = label
		self.polarise = polarise

		self.value = None if self.polarise else 0

		self.coach = self.context.coach
		self.pane  = self.context.pane

		self.font = pygame.font.SysFont("Consolas",14,bold=True)
		self.size = self.font.size(self.field)
		self.bg   = pygame.Surface((
			self.size[0] + 8,
			self.size[1] + 5
		))

	def render(self):
		# Calculate
		self.size = self.font.size(self.field)
		self.bg = pygame.Surface((
			self.size[0] + 13,
			self.size[1] + 5
		))
		# self.bkgr.fill((82,82,88) if self.value is None else (0,0,0))

		# Metric
		### panel
		self.pane.blit(self.bg , (self.x,self.y))

		### field
		if self.polarise:
			self.pane.blit(
				self.font.render(self.field[0] , True , (255,255,255)),
				(self.x + 4 , self.y + 3)
			)
			self.pane.blit(
				self.font.render(self.field[1:] , True , (255,255,255)),
				(self.x + 16 , self.y + 3)
			)
		else:
			self.pane.blit(
				self.font.render(self.field , True , (255,255,255)),
				(self.x + 6 , self.y + 3)
			)

		# Label
		self.pane.blit(
			self.font.render(self.label , True , (255,255,255)),
			(
				self.x + self.size[0] + 20,
				self.y + 3
			)
		)

	def click(self):
		pass

	@property
	def field(self):
		if self.value is None:
			return " -.--"

		if self.polarise:
			sign = "±"
			if float(self.value) > 0:
				sign = "+"
			elif float(self.value) < 0:
				sign = "-"
			return sign + f'{abs(self.value):.2f}'

		elif int(self.value) == self.value:
			return str(self.value)

		else:
			print("WHAT AM I")



class Slider:
	all = []
	def __init__(self , display , x , y , size , metric , txform , domain , nrungs , trigger , vertical=False):
		Slider.all.append(self)
		self.display  = display
		self.x        = x
		self.y        = y
		self.size     = size
		self.metric   = metric
		self.txform   = txform			### must be a format-ready string
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

		self.active = None

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
			self.ratio = round(
				(self.nrungs-1) * (pos[1] - self.rect.bottom)
				/
				(self.rect.top - self.rect.bottom)
			) / (self.nrungs-1)

			self.knob.centery = self.max_pos - self.ratio*(self.max_pos - self.min_pos)

		else:
			self.ratio = round(
				(self.nrungs-1) * (pos[0] - self.rect.left)
				/
				(self.rect.right - self.rect.left)
			) / (self.nrungs-1)

			self.knob.centerx = self.min_pos + self.ratio*(self.max_pos - self.min_pos)

		self.value = self.min_val + self.ratio*(self.max_val - self.min_val)

		# Function
		exec(
			self.metric + self.txform + str(self.value)
		)


	def render(self):
		self.trackbed.fill(C.SLIDER_COLOUR_LIVE if self.trigger.active else C.SLIDER_COLOUR_DEAD)
		pygame.draw.rect(
			self.trackbed,
			(0,0,0,15),
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

		self.display.blit(self.trackbed,(self.x,self.y))


	def paint(self):
		pass


	def click(self):
		pass


	@property
	def value_nice(self):
		return str(round(self.value))



class Dropdown:
	def __init__(self , options , trigger , persist=False):
		self.options = options
		if all([self.options[0].trigger == item.trigger for item in self.options]):
			self.trigger = trigger
		else:
			raise Exception("All dropdown options must have identical .trigger and .persist!")
		self.persist = persist
		self.active  = persist

		self.i = 0
		self.I = len(self.options)

	def __iter__(self):
		yield from self.options

	def __getitem__(self , index):
		return self.options[index]

	def __setitem__(self , index , value):
		self.options[index] = value

	def render(self):
		if self.persist or self.active:
			for option in self.options:
				option.render()

	@property
	def actives(self):
		return [item.active for item in self.options]



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


	def draw(self):
		self.shoot()


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



# TODO: MORE ELEMENTS
#   1) top engine line(s) arrows
class Button:
	def __init__(self , coach , display , x , y , size=C.BUTTON_SIZE):
		self.coach   = coach
		self.display = display
		self.x       = x
		self.y       = y
		self.size    = size

		self.dropdown = []

		self.COLOUR_LIVE = C.BUTTON_LIVE
		self.COLOUR_LOOM = C.BUTTON_LOOM
		self.COLOUR_IDLE = C.BUTTON_IDLE
		self.COLOUR_LOCK = C.BUTTON_LOCK

		self.active = False
		self.colour = C.BUTTON_IDLE

		self.font = pygame.font.SysFont("Consolas",12)
		self.rect = pygame.Rect(
			self.x,
			self.y,
			*self.size,
		)

		self.tooltip = None
		self.image   = None


	def __repr__(self):
		return type(self).__name__


	def click(self):
		pass


	def render(self):
		# Myself
		pygame.draw.rect(       ### background
			self.display,
			self.colour,
			self.rect
		)
		self.display.blit(      ### icon
			self.image,
			self.rect
		)

		# Hover action
		self.render_tooltip()


	def render_tooltip(self , shift=(0,0)):
		if self.rect.collidepoint(local_pos := (
			self.coach.mouse_pos[0] + shift[0],
			self.coach.mouse_pos[1] + shift[1],
		)):
			tltp_width = self.font.size(self.tooltip)[0]
			self.display.blit(
				self.font.render(
					self.tooltip,
					True,
					(0,0,0),
					(255,255,255,0)
				),
				(
					local_pos[0] + 15,
					local_pos[1] + 10
				) if local_pos[0] + tltp_width < self.coach.current_w + shift[0] else (      ### overflow (no clue why this works)
					local_pos[0] - 5 - tltp_width,
					local_pos[1] + 10
				)
			)


	def paint(self):
		self.colour = {
			None  : self.COLOUR_LOCK,
			False : self.COLOUR_IDLE,
			True  : self.COLOUR_LOOM,
		}[self.dropdown.active] if self.dropdown else {
			None  : self.COLOUR_LOCK,
			False : self.COLOUR_IDLE,
			True  : self.COLOUR_LIVE
		}[self.active]



class ButtonBot(Button):
	def __init__(self , *args , player):
		super().__init__(*args)
		self.player  = player
		self.persist = True         ### all ButtonBots are persistent

		self.engine = self.coach.engine
		self.scheme = self.engine.schema[self.player == "BLACK"]

		self.slider = Slider(
			self.display,
			x=self.x,
			y=self.y + C.BUTTON_HEIGHT + C.GRID_GAP,
			size=(
				C.TEXTBOX_WIDTH,
				0.85*C.BUTTON_HEIGHT
			),
			metric="E.BOT_DEPTH_"+self.player.upper(),
			txform=" = ",
			domain=(1,4),
			nrungs=4,
			trigger=self,
		)

		self.dropdown = Dropdown(       ### excludes Slider
			options=[
				ButtonBotOption(
					self.coach,
					self.display,
					(
						self.x + C.TEXTBOX_WIDTH - 1*C.BUTTON_WIDTH
					) if self.persist else (
						self.x + C.GRID_GAP/2 + 3*C.BUTTON_WIDTH
					),
					self.y,
					philosophy="Stockfish",
					trigger=self
				),
				ButtonBotOption(
					self.coach,
					self.display,
					(
						self.x + C.TEXTBOX_WIDTH - 2*C.BUTTON_WIDTH
					) if self.persist else (
						self.x + C.GRID_GAP/2 + 2*C.BUTTON_WIDTH
					),
					self.y,
					philosophy="HAL9",
					trigger=self
				),
				ButtonBotOption(
					self.coach,
					self.display,
					(
						self.x + C.TEXTBOX_WIDTH - 3*C.BUTTON_WIDTH
					) if self.persist else (
						self.x + C.GRID_GAP/2 + 1*C.BUTTON_WIDTH
					),
					self.y,
					philosophy="Random",
					trigger=self
				),
			],
			trigger=self,
			persist=True
		)
		### initial conditions
		self.active = (None,True)[bool(self.scheme)]
		for option in self.dropdown:
			option.active = self.scheme == option.philosophy.upper()

		self.tooltip = self.player.title() + " bot"
		self.image   = pygame.transform.scale(
			pygame.image.load(
				C.DIR_ICONS + "\\bots\\bot_" + self.player.lower() + "_" + (self.scheme or "") + ".png"
			),
			self.size
		)

	def click(self):
		pass

	def render(self):
		# Dropdown
		self.dropdown.render()

		# Slider
		self.slider.render()

		# Myself
		self.colour = self.COLOUR_LIVE if self.active else self.COLOUR_LOOM
		super().render()



class ButtonBotOption(Button):
	def __init__(self , *args , philosophy , trigger):
		super().__init__(*args)
		self.philosophy = philosophy
		self.trigger 	= trigger
		self.player     = trigger.player

		self.engine = self.trigger.engine

		self.tooltip = self.philosophy
		self.image   = pygame.transform.scale(
			pygame.image.load(
				C.DIR_ICONS + "\\bots\\bot_" + self.player.lower() + "_" + self.philosophy.lower() + ".png"
			),
			self.size
		)

	def click(self):
		# Function
		incumbent = self.engine.schema[self.player.upper() == "BLACK"]
		candidate = self.philosophy.upper()

		appointed = candidate if candidate != incumbent else None

		### apply
		self.engine.schema[self.player.upper() == "BLACK"] = appointed

		### import foreign(s)
		match appointed:
			case "STOCKFISH":
				self.engine.load_stockfish()

		# Mechanics
		for trigger in [
			self.coach.buttons_bots["BOT_" + self.player],
			self.coach.analysis.buttons_bots["BOT_" + self.player],
		]:
			trigger.active = (None,True)[bool(appointed)]
			for option in trigger.dropdown:
				option.active = (False,not option.active)[self.philosophy == option.philosophy]

			trigger.paint()

			trigger.image  = pygame.transform.scale(
				pygame.image.load(
					C.DIR_ICONS + "\\bots\\bot_" + self.player.lower() + "_" + (
						appointed or ""
					) + ".png"
				),
				self.trigger.size
			)



class ButtonDesignPieces(Button):
	def __init__(self , *args):
		super().__init__(*args)

		self.board = self.coach.board

		self.dropdown = Dropdown(
			options=[
				ButtonDesignPiecesOption(
					self.coach,
					self.display,
					self.x + C.BUTTON_WIDTH + C.GRID_GAP/2,
					self.y + 2*C.BUTTON_HEIGHT,
					style="Chess.com",
					trigger=self
				),
				ButtonDesignPiecesOption(
					self.coach,
					self.display,
					self.x + 2*C.BUTTON_WIDTH + C.GRID_GAP/2,
					self.y + C.BUTTON_HEIGHT,
					style="8-Bit",
					trigger=self
				),
				ButtonDesignPiecesOption(
					self.coach,
					self.display,
					self.x + C.BUTTON_WIDTH + C.GRID_GAP/2,
					self.y + C.BUTTON_HEIGHT,
					style="FontAwesome",
					trigger=self
				),
				ButtonDesignPiecesOption(
					self.coach,
					self.display,
					self.x + 2*C.BUTTON_WIDTH + C.GRID_GAP/2,
					self.y,
					style="3D",
					trigger=self
				),
				ButtonDesignPiecesOption(
					self.coach,
					self.display,
					self.x + C.BUTTON_WIDTH + C.GRID_GAP/2,
					self.y,
					style="Classic",
					trigger=self
				),
			],
			trigger=self
		)
		### initial conditions
		for option in self.dropdown:
			option.active        = C.PIECE_DESIGN == option.style.upper()

		self.tooltip = "Piece design"
		self.image   = pygame.transform.scale(
			pygame.image.load(C.DIR_ICONS + "\\ui\\btn_design_pieces.png"),
			self.size
		)

	def click(self):
		self.active          = not self.active
		self.dropdown.active = self.active


	def render(self):
		if self.active:
			self.dropdown.render()

		super().render()



class ButtonDesignPiecesOption(Button):
	def __init__(self , *args , style , trigger):
		super().__init__(*args)
		self.style	 = style
		self.trigger = trigger

		self.tooltip = self.style + " set"
		self.image   = pygame.transform.scale(
			pygame.image.load(C.DIR_ICONS + "\\ui\\btn_pstyle_" + self.style.lower() + ".png"),
			self.size
		)

	def click(self):
		# Mechanics
		self.trigger.active          = False
		self.trigger.dropdown.active = False

		### single-select mandatory dropdown
		for option in self.trigger.dropdown:
			option.active = option is self

		# Function
		C.PIECE_DESIGN = self.style.upper()
		C.DIR_SET     = C.DIR_MEDIA + "sets\\" + C.PIECE_DESIGN + "\\"
		for man in self.trigger.board.all_men():
			man.image = pygame.transform.scale(
				pygame.image.load(
					C.DIR_SET + man.colour + (man.creed or "pawn")[0].lower() + ".png"
				),
				man.image_size
			)



class ButtonDesignBoard(Button):
	def __init__(self , *args):
		super().__init__(*args)

		self.board = self.coach.board

		self.dropdown = Dropdown(
			options=[
				ButtonDesignBoardOption(
					self.coach,
					self.display,
					self.x + 1*C.BUTTON_WIDTH + C.GRID_GAP/2,
					self.y + C.BUTTON_HEIGHT,
					style="BLEAK",
					trigger=self,
				),
				ButtonDesignBoardOption(
					self.coach,
					self.display,
					self.x + 2*C.BUTTON_WIDTH + C.GRID_GAP/2 - 1,      ### idiopathic 1px gap
					self.y,
					style="CHEAP",
					trigger=self,
				),
				ButtonDesignBoardOption(
					self.coach,
					self.display,
					self.x + 1*C.BUTTON_WIDTH + C.GRID_GAP/2,
					self.y,
					style="BROWN",
					trigger=self,
				),
			],
			trigger=self
		)

		self.tooltip = "Board design"
		self.image   = pygame.transform.scale(
			pygame.image.load(C.DIR_ICONS + "\\ui\\btn_design_board.png"),
			self.size
		)

	def click(self):
		self.active          = not self.active
		self.dropdown.active = self.active

	def render(self):
		if self.active:
			self.dropdown.render()

		super().render()



class ButtonDesignBoardOption(Button):
	def __init__(self , *args , style , trigger):
		super().__init__(*args)
		self.style 	 = eval("C.BOARD_DESIGN_" + style)
		self.trigger = trigger

		self.tooltip = style.title() + " board"

	def click(self):
		# Mechanics
		self.trigger.active          = False
		self.trigger.dropdown.active = False

		### single-select mandatory dropdown
		if self.style == C.BOARD_DESIGN:
			return

		for option in self.trigger.dropdown:
			option.active = not option.active if option is self else False

		# Function
		C.BOARD_DESIGN = self.style
		for tile in self.trigger.board.all_tiles:
			if (tile.f + tile.r) % 2 == 1:
				tile.rgb_basic = C.BOARD_DESIGN[0]
				tile.rgb_fresh = C.BOARD_DESIGN[1]
			else:
				tile.rgb_basic = C.BOARD_DESIGN[2]
				tile.rgb_fresh = C.BOARD_DESIGN[3]

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
	def __init__(self , *args , context):
		super().__init__(*args)
		self.context = context

		self.COLOUR_IDLE = [int(CC/0.85) for CC in self.context.colour]

		self.tooltip = str(self.context).title()
		self.image   = pygame.transform.scale(
			pygame.image.load(C.DIR_ICONS + "\\context_" + str(self.context).lower() + ".png"),
			self.size
		)

	def click(self):
		for context in self.coach.contexts:
			context.show = context is self.context



class ButtonContextExit(Button):
	def __init__(self , *args):
		super().__init__(*args)

		self.scale = 0.85

		self.x   += (1-self.scale)*C.BUTTON_WIDTH/2
		self.y   += (1-self.scale)*C.BUTTON_HEIGHT/2
		self.size = [self.scale*l for l in C.BUTTON_SIZE]
		self.rect = pygame.Rect(
			self.x,
			self.y + 1,
			*self.size
		)

		self.tooltip = "Exit"
		self.image   = pygame.transform.scale(
			pygame.image.load(C.DIR_ICONS + "btn_exit.png"),
			self.size
		)

	def click(self):
		for context in self.coach.contexts:
			context.show = False

	def paint(self):
		self.colour = (85,75,75)



class ButtonPrevious(Button):
	def __init__(self , *args):
		super().__init__(*args)

		self.tooltip = "Previous"
		self.image   = pygame.transform.scale(
			pygame.image.load(C.DIR_ICONS + "\\btn_prev.png"),
			self.size
		)

	def click(self):
		# print("--- PREV ---")
		# print(self.coach.board.this_move)
		# print(self.coach.board.last_move if self.coach.board.last_move else "-")
		# print(self.coach.board.halfmovenum,self.coach.board.movenum,self.coach.board.movelog)
		# print("------------")

		if self.coach.board.halfmovenum > 1:
			board = self.coach.board

			last_move = board.movelog[board.halfmovenum - 2]
			if board.halfmovenum > 2:
				past_move = board.movelog[board.halfmovenum - 3]
			else:
				past_move = None

			# Board mechanics
			board.halfmovenum -= 1
			self.coach.import_FEN(last_move.fen)
			board.this_move = last_move
			board.last_move = past_move

			# Move mechanics
			unmove = last_move.rewind()               ### realistically only ever click()'ed AFTER turnover

			cache          = board.tile(unmove.target).occupant
			cache.position = unmove.target.position
			self.coach.board.tile(unmove.target).occupant = None

			unmove.animate()

			board.tile(unmove.target).occupant = cache

			# Calibrate
			board.calibrate()

			### clock
			self.coach.clock.jibe()


		# print(self.coach.board.this_move)
		# print(self.coach.board.last_move if self.coach.board.last_move else "-")
		# print(self.coach.board.halfmovenum,self.coach.board.movenum,self.coach.board.movelog)
		# print("------------")
		# print()



class ButtonNext(Button):
	def __init__(self , *args):
		super().__init__(*args)

		self.tooltip = "Next"
		self.image   = pygame.transform.scale(
			pygame.image.load(C.DIR_ICONS + "\\btn_next.png"),
			self.size
		)

	def click(self):
		# print("--- NEXT ---")
		# print(self.coach.board.this_move)
		# print(self.coach.board.last_move if self.coach.board.last_move else "-")
		# print(self.coach.board.halfmovenum,self.coach.board.movenum,self.coach.board.movelog)
		# print("---      ---")

		if self.coach.board.halfmovenum < len(self.coach.board.movelog):
			board = self.coach.board

			next_move = board.movelog[board.halfmovenum]
			this_move = board.movelog[board.halfmovenum - 1]

			# Board mechanics
			board.halfmovenum += 1
			self.coach.import_FEN(next_move.fen)
			board.this_move = next_move
			board.last_move = this_move

			# Move mechanics
			cache          = board.tile(this_move.target).occupant
			cache.position = this_move.target.position
			if this_move.ep:
				board.tile(this_move.target).occupant = None
				board.tile(this_move.ep).occupant 	  = this_move.capture
			else:
				board.tile(this_move.target).occupant = this_move.capture

			this_move.animate()

			board.tile(this_move.target).occupant = cache
			if this_move.ep:
				board.tile(this_move.ep).occupant = None

			# Calibrate
			board.calibrate()

			### clock
			self.coach.clock.jibe(
				resume=board.halfmovenum == len(board.movelog)
			)


		# print(self.coach.board.this_move)
		# print(self.coach.board.last_move if self.coach.board.last_move else "-")
		# print(self.coach.board.halfmovenum,self.coach.board.movenum,self.coach.board.movelog)
		# print("------------")
		# print()



class ButtonBoardReset(Button):
	def __init__(self , *args):
		super().__init__(*args)

		self.sound_game_reset = pygame.mixer.Sound(C.DIR_SOUNDS + "\\game_reset.wav")

		self.tooltip = "Reset"
		self.image   = pygame.transform.scale(
			pygame.image.load(C.DIR_ICONS + "\\btn_reset.png"),
			self.size
		)

	def click(self):
		self.coach.reset()

		self.sound_game_reset.play()



class ButtonECOInterpreter(Button):
	def __init__(self , *args):
		super().__init__(*args)

		self.active = True

		self.tooltip = "Interpret opening"
		self.image   = pygame.transform.scale(
			pygame.image.load(C.DIR_ICONS + "\\ui\\btn_eco_interpreter.png"),
			self.size
		)

	def click(self):
		self.active = not self.active
		self.paint()

		if self.active:
			self.coach.reader.load()
			self.coach.reader.update()

		else:
			self.coach.reader.unload()



class ButtonTopLine(Button):
	def __init__(self , *args , i):
		super().__init__(*args)

		self.i = i

		self.movetext = f'Line {i}'

	def click(self):
		print(f'top line {self.i}')

	def render(self):
		surf = pygame.Surface(
			(C.TEXTBOX_WIDTH , C.TEXTBOX_HEIGHT + 1),
			flags=pygame.SRCALPHA
		)
		surf.fill( (60,60,70,100) )
		self.display.blit(surf,(self.x,self.y))



class ButtonImport(Button):
	def __init__(self , *args):
		super().__init__(*args)

		self.tooltip = "Import"
		self.image   = pygame.transform.scale(
			pygame.image.load(C.DIR_ICONS + "\\btn_import.png"),
			self.size
		)

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
				self.coach.settings.show = False

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
	def __init__(self , *args):
		super().__init__(*args)

		self.tooltip = "Export"
		self.image   = pygame.transform.scale(
			pygame.image.load(C.DIR_ICONS + "\\btn_export.png"),
			self.size
		)

	def click(self):
		# Tags
		writers = self.coach.settings.writers

		### seven tag roster
		tags = {
			"Event" : writers["EVENT"].text,
			"Site"  : writers["SITE"].text,
			"Date"  : writers["DATE"].text,
			"Round" : writers["ROUND"].text,
			"White" : writers["WHITE"].text,
			"Black" : writers["BLACK"].text,
		}

		### are there truly any winners in chess?
		if self.coach.board.outcome[0] == "Checkmate":
			if self.coach.board.outcome[1] == "White":
				tags["Result"] = "1-0"
			else:
				tags["Result"] = "0-1"
		elif self.coach.board.outcome[0] == "Draw":
			tags["Result"] = "½-½"
		else:
			tags["Result"] = "*"    ### ongoing


		### Mode : OTB / ICS / LCP
		tags["Mode"] = "LCP"        ### Local Chess Platform


		##### ⚠⚠ MALPRACTICE ⚠⚠ #####
		self.coach.tags = tags
		###################################

		# Write
		filename = tags["Event"] + "__" + tags["Date"]
		with open(C.DIR + "\\games\\" + filename + ".pgn" , "w") as file:
			### tags
			for tag,val in tags.items():
				file.write("[" + tag + " \"" + val + "\"]\n")

			### movetext
			for line in self.coach.export_PGN():
				file.write(line)

			if self.coach.board.outcome[1] in ("White","Black"):
				file.write("#")
			file.write("\n" + tags["Result"])

		print(filename + ".pgn exported!")



class ButtonFlip(Button):
	def __init__(self , *args):
		super().__init__(*args)

		self.tooltip = "Flip board"
		self.image   = pygame.transform.scale(
			pygame.image.load(C.DIR_ICONS + "\\ui\\btn_flip.png"),
			self.size
		)

	def click(self):
		if C.BOARD_FLIPPED:
			C.BOARD_FLIPPED = False
			self.coach.board.sound_flipA.play()
		else:
			C.BOARD_FLIPPED = True
			self.coach.board.sound_flipB.play()

		# Definitions
		### bots
		w_c_bot = self.coach.buttons["BOT_WHITE"]
		b_c_bot = self.coach.buttons["BOT_BLACK"]

		w_a_bot = self.coach.analysis.buttons_bots["BOT_WHITE"]
		b_a_bot = self.coach.analysis.buttons_bots["BOT_BLACK"]

		### clocks
		w_clock = self.coach.clock.whiteface
		b_clock = self.coach.clock.blackface
		w_clock_elems = [
			w_clock.timer,
			w_clock.resetter,
		]
		b_clock_elems = [
			b_clock.timer,
			b_clock.resetter,
		]

		### graves
		w_graves = self.coach.graveyard.w_rect
		b_graves = self.coach.graveyard.b_rect
		w_plaque = self.coach.graveyard.w_plaque
		b_plaque = self.coach.graveyard.b_plaque

		### gauge
		w_gauge = self.coach.gauge.w_rect
		b_gauge = self.coach.gauge.b_rect

		# Mechanics
		### specialist
		w_gauge.y = b_gauge.h - w_gauge.y
		b_gauge.y = w_gauge.h - b_gauge.y

		### generic
		for w,b in zip(
			[ w_c_bot , *w_c_bot.dropdown , w_a_bot , *w_a_bot.dropdown , w_clock , *w_clock_elems , w_graves , w_plaque ],
			[ b_c_bot , *b_c_bot.dropdown , b_a_bot , *b_a_bot.dropdown , b_clock , *b_clock_elems , b_graves , b_plaque ],
		):
			w.y , b.y = b.y , w.y

			try:
				w.rect , b.rect = b.rect , w.rect
			except AttributeError:
				pass



class ButtonFreshMoves(Button):
	def __init__(self , *args):
		super().__init__(*args)
		self.active = C.SHOW_MOVE_FRESH

		self.tooltip = "Show recent moves"
		self.image   = pygame.transform.scale(
			pygame.image.load(C.DIR_ICONS + "\\ui\\btn_fresh_moves.png"),
			self.size
		)

	def click(self):
		self.active = not self.active
		self.paint()

		C.SHOW_MOVE_FRESH = not C.SHOW_MOVE_FRESH



class ButtonLegalMoves(Button):
	def __init__(self , *args):
		super().__init__(*args)
		self.active = C.SHOW_MOVE_LEGAL

		self.tooltip = "Show legal moves"
		self.image   = pygame.transform.rotozoom(
			image_raw := pygame.image.load(C.DIR_ICONS + "\\ui\\btn_legal_moves.png"),
			angle=45,
			scale=self.size[0]/(image_raw.get_size()[0]*(2**.5))
		)

	def click(self):
		self.active = not self.active
		self.paint()

		C.SHOW_MOVE_LEGAL = not C.SHOW_MOVE_LEGAL



class ButtonCoords(Button):
	def __init__(self , *args):
		super().__init__(*args)
		self.active = C.SHOW_TILE_COORD

		self.tooltip = "Show coordinates"
		self.image   = pygame.transform.scale(
			pygame.image.load(C.DIR_ICONS + "\\ui\\btn_coordinates.png"),
			self.size
		)

	def click(self):
		self.active = not self.active
		self.paint()

		C.SHOW_TILE_COORD = not C.SHOW_TILE_COORD



class ButtonSpedometer(Button):
	def __init__(self , *args):
		super().__init__(*args)

		self.slider = Slider(
			self.display,
			x=self.x + 1.085*C.BUTTON_WIDTH + C.GRID_GAP,      ### idiopathic 1.085
			y=self.y - C.BUTTON_HEIGHT,
			size=(
				0.85*C.BUTTON_WIDTH,
				3*C.BUTTON_HEIGHT,
			),
			metric="C.GAME_SPEED",
			txform=" = 50/",
			domain=(1,10),
			nrungs=10,
			trigger=self,
			vertical=True
		)
		self.dropdown = Dropdown(
			options=[self.slider,],
			trigger=self
		)

		self.tooltip = "Animation speed"
		self.image   = pygame.transform.scale(
			pygame.image.load(C.DIR_ICONS + "\\ui\\btn_spedometer" + str(int(C.GAME_SPEED)) + ".png"),
			self.size
		)

	def click(self):
		self.active          = not self.active
		self.dropdown.active = self.active
		self.slider.active   = self.active

	def render(self):
		if self.active:
			self.dropdown.render()

		# Slider changes trigger image
		if pygame.mouse.get_pressed() and (slider := self.dropdown[0]).rect.collidepoint(self.coach.mouse_pos):
			self.image = pygame.transform.scale(
				pygame.image.load(C.DIR_ICONS + "\\ui\\btn_spedometer" + str(int(slider.value)) + ".png"),
				self.size
			)

		super().render()



class ButtonVolume(Button):
	def __init__(self , *args):
		super().__init__(*args)

		self.vol_max = 3

		self.slider = Slider(
			self.display,
			x=self.x + 1.085*C.BUTTON_WIDTH + C.GRID_GAP,      ### .085 looks best even tho it's not actually centered
			y=self.y - C.BUTTON_HEIGHT,
			size=(
				0.85*C.BUTTON_WIDTH,
				3*C.BUTTON_HEIGHT,
			),
			metric="C.GAME_VOLUME",
			txform=" = ",
			domain=(0,self.vol_max),
			nrungs=1+self.vol_max,
			trigger=self,
			vertical=True
		)
		self.dropdown = Dropdown(
			options=[self.slider,],
			trigger=self
		)

		self.tooltip = "Volume"
		self.image   = pygame.transform.scale(
			pygame.image.load(C.DIR_ICONS + "\\ui\\btn_volume" + str(int(self.slider.value)) + ".png"),
			self.size
		)

	def click(self):
		# Mechanics
		self.active          = not self.active
		self.dropdown.active = self.active
		self.slider.active   = self.active

		# Function
		self.apply()

	def apply(self):
		vol = C.GAME_VOLUME / self.vol_max

		### music
		pygame.mixer.music.set_volume(vol)

		### sounds
		for sound in (
				### ### Coach
				self.coach.sound_game_start,
				self.coach.sound_game_end,
				self.coach.sound_whistle_start,
				self.coach.sound_whistle_stop,
				### ### Board
				self.coach.board.sound_clean,
				self.coach.board.sound_flipA,
				self.coach.board.sound_flipB,
				self.coach.board.sound_check,
				self.coach.board.sound_void,
		):
			sound.set_volume(vol)

	def render(self):
		# Slider
		if self.active:
			self.dropdown.render()

		# Slider changes trigger image
		if pygame.mouse.get_pressed() and self.slider.rect.collidepoint(pygame.mouse.get_pos()):
			self.image = pygame.transform.scale(
				pygame.image.load(C.DIR_ICONS + "\\ui\\btn_volume" + str(int(self.slider.value))  + ".png"),
				self.size
			)

		super().render()



class ButtonAutoPromote(Button):
	def __init__(self , *args):
		super().__init__(*args)

		self.names = {
			"Q"  : "Queen",
			"R"  : "Rook",
			"B"  : "Bishop",
			"N"  : "Knight",
			None : "Pawn",
		}

		self.dropdown = Dropdown(
			options=[
				ButtonAutoPromoteOption(
					self.coach,
					self.display,
					self.x + 2*C.BUTTON_WIDTH + C.GRID_GAP/2,
					self.y + C.BUTTON_HEIGHT,
					creed="N",
					trigger=self
				),
				ButtonAutoPromoteOption(
					self.coach,
					self.display,
					self.x + C.BUTTON_WIDTH + C.GRID_GAP/2,
					self.y + C.BUTTON_HEIGHT,
					creed="B",
					trigger=self
				),
				ButtonAutoPromoteOption(
					self.coach,
					self.display,
					self.x + 2*C.BUTTON_WIDTH + C.GRID_GAP/2,
					self.y,
					creed="R",
					trigger=self
				),
				ButtonAutoPromoteOption(
					self.coach,
					self.display,
					self.x + C.BUTTON_WIDTH + C.GRID_GAP/2,
					self.y,
					creed="Q",
					trigger=self
				),
			],
			trigger=self
		)
		### initial conditions
		for option in self.dropdown:
			option.active = option.creed.upper() == C.AUTO_PROMO

		self.tooltip = ("Auto-" + self.names[C.AUTO_PROMO]) if C.AUTO_PROMO else "Ask to promote"
		self.image   = pygame.transform.scale(
			pygame.image.load(C.DIR_SETS + "promo_" + (self.names[C.AUTO_PROMO].lower() or "pawn") + ".png"),
			self.size
		)

	def click(self):
		self.dropdown.active = not self.dropdown.active

	def render(self):
		if self.dropdown.active:
			self.dropdown.render()

		super().render()

	def paint(self):
		if bool(C.AUTO_PROMO):
			self.colour = self.COLOUR_LIVE
		elif self.dropdown.active:
			self.colour = self.COLOUR_LOOM
		else:
			self.colour = self.COLOUR_IDLE



class ButtonAutoPromoteOption(Button):
	def __init__(self , *args , creed , trigger):
		super().__init__(*args)
		self.creed   = creed
		self.trigger = trigger

		self.name = self.trigger.names[self.creed]

		self.tooltip = self.name.title()
		self.image   = pygame.transform.scale(
			pygame.image.load(C.DIR_SETS + "agnostic_" + self.name.lower() + ".png"),
			self.size
		)

	def click(self):
		# Mechanics
		self.trigger.dropdown.active = False

		### single-select voluntary dropdown
		for option in self.trigger.dropdown:
			option.active = not self.active if option is self else False

		# Function
		C.AUTO_PROMO = None if self.creed.upper() == C.AUTO_PROMO else self.creed.upper()

		# Mechanics again
		self.trigger.active = bool(C.AUTO_PROMO)
		self.trigger.paint()

		if self.trigger.active:
			image_dir            = C.DIR_SETS + "promo_" + self.name.lower()
			self.trigger.tooltip = "Auto-" + self.name.title()
		else:
			image_dir            = C.DIR_SETS + "promo_pawn"
			self.trigger.tooltip = "Ask to promote"

		self.trigger.image = pygame.transform.scale(
			pygame.image.load(image_dir+".png"),
			self.trigger.size
		)



class ButtonAutoDraw(Button):
	def __init__(self , *args):
		super().__init__(*args)
		self.active = C.AUTO_DRAW

		self.tooltip = "Auto-draw"
		self.image   = pygame.transform.scale(
			pygame.image.load(C.DIR_ICONS + "\\ui\\btn_auto_draw.png"),
			self.size
		)

		self.active = True

	def click(self):
		self.active = not self.active
		self.paint()

		C.AUTO_DRAW = not C.AUTO_DRAW



class ButtonDrills(Button):
	def __init__(self , *args):
		super().__init__(*args)

		self.dropdown = Dropdown(
			options=[
				ButtonDrillOption(
					self.coach,
					self.display,
					self.x + 2*C.BUTTON_WIDTH + C.GRID_GAP/2,
					self.y,
					course="endgames",
					trigger=self
				),
				ButtonDrillOption(
					self.coach,
					self.display,
					self.x + C.BUTTON_WIDTH + C.GRID_GAP/2,
					self.y,
					course="openings",
					trigger=self
				),
			],
			trigger=self
		)

		self.tooltip = "Drills"
		self.image = pygame.transform.scale(
			pygame.image.load(C.DIR_ICONS + "btn_drills.png"),
			self.size
		)

	def click(self):
		self.active          = not self.active
		self.dropdown.active = self.active

	def render(self):
		# Dropdown
		if self.dropdown.active:
			self.dropdown.render()

		# Myself
		if self.active:
			self.colour = C.BUTTON_LIVE
		elif self.rect.collidepoint(self.coach.mouse_pos) or self.dropdown.active:
			self.colour = C.BUTTON_LOOM
		else:
			self.colour = C.BUTTON_IDLE
		super().render()



class ButtonDrillOption(Button):
	def __init__(self , *args , course , trigger):
		super().__init__(*args)
		self.course  = course
		self.trigger = trigger

		self.tooltip = self.course.title()
		self.image   = pygame.transform.scale(
			pygame.image.load(C.DIR_ICONS + "drill_" + self.course.lower() + ".png"),
			self.size
		)

	def click(self):
		# Mechanics
		self.trigger.dropdown.active = False

		### single-select voluntary dropdown
		for option in self.trigger.dropdown:
			option.active = not self.active if option is self else False

		# Function
		if self.course.upper() == self.coach.coaching.drilling:
			self.coach.coaching.drilling = None
			self.coach.sound_whistle_stop.play()
		else:
			self.coach.coaching.drilling = self.course.upper()
			self.coach.sound_whistle_start.play()

		# Mechanics again
		self.trigger.active = bool(self.coach.coaching.drilling)
		self.trigger.paint()

		if self.trigger.active:
			image_dir            = C.DIR_ICONS + "drill_" + self.course.lower()
			self.trigger.tooltip = self.course.title()[:-1] + " drills!"
		else:
			image_dir            = C.DIR_ICONS + "btn_drills"
			self.trigger.tooltip = "At ease"

		self.trigger.image = pygame.transform.scale(
			pygame.image.load(image_dir + ".png"),
			self.trigger.size
		)



class ButtonToggleTray(Button):
	def __init__(self , *args):
		super().__init__(*args)

		self.active = True

		self.tooltip = "Tray open"
		self.image   = pygame.transform.scale(
			pygame.image.load(C.DIR_ICONS + "ui\\btn_tray_open.png"),
			self.size
		)


	def render(self):
		# Draw
		self.display.blit(self.image,self.rect)

		# Hover Mechanics
		if self.rect.collidepoint((
			self.coach.mouse_pos[0] - C.TRAY_OFFSET,
			self.coach.mouse_pos[1],
		)):
			### tooltip
			self.render_tooltip(shift=(-C.TRAY_OFFSET,0))

			### cursor
			return self


	def click(self):
		self.active = not self.active

		if self.active:
			self.tooltip = "Shut tray"
			self.image   = pygame.transform.scale(
				pygame.image.load(C.DIR_ICONS + "ui\\btn_tray_open.png"),
				self.size
			)

			self.coach.screen    = pygame.display.set_mode(C.WINDOW_SIZE)
			self.coach.current_w = pygame.display.Info().current_w

		else:
			self.tooltip = "Open tray"
			self.image   = pygame.transform.scale(
				pygame.image.load(C.DIR_ICONS + "ui\\btn_tray_shut.png"),
				self.size
			)

			self.coach.screen    = pygame.display.set_mode((C.PANE_WIDTH + C.GAUGE_WIDTH + C.BOARD_WIDTH + C.GRAVE_WIDTH , C.WINDOW_HEIGHT))
			self.coach.current_w = pygame.display.Info().current_w



class ButtonClock(Button):
	def __init__(self , *args , clock , player):
		super().__init__(*args)
		self.clock  = clock
		self.player = player
		self.p      = player[0].lower()

		# Mechanics
		starter = (C.TIME_STARTER_WHITE,C.TIME_STARTER_BLACK)[self.p == "b"]
		self.start_str = ":".join(str(s) for s in starter)
		self.start_num = 60*(60*starter[0] + starter[1]) + starter[2]
		self.bonus = (C.TIME_BONUS_WHITE,C.TIME_BONUS_BLACK)[self.p == "b"]

		# Interface
		### HH:MM:SS or MM:SS
		hour_plus = self.start_num + self.bonus >= 60*60

		self.timer = Timer(
			self.display,
			x=(self.x - C.BUTTON_WIDTH) if hour_plus else self.x - C.BUTTON_WIDTH/2,
			y=(
				self.y - (5/6)*C.BUTTON_HEIGHT - 2*C.GRID_GAP,
				self.y + C.BUTTON_HEIGHT + 2*C.GRID_GAP
			)[self.p == "b"],
			size=(3*C.BUTTON_WIDTH , (5/6)*C.BUTTON_HEIGHT) if hour_plus else (2*C.BUTTON_WIDTH , (5/6)*C.BUTTON_HEIGHT),
			start=self.start_num,
			bonus=self.bonus,
			trigger=self
		)
		self.setter = ButtonClockSet(
			self.coach,
			self.display,
			self.x - C.BUTTON_WIDTH - C.GRID_GAP,
			self.timer.y + 3,
			[2*L/3 for L in C.BUTTON_SIZE],
			timer=self.timer
		)
		self.resetter = ButtonClockReset(
			self.coach,
			self.display,
			self.x + 1.5*C.BUTTON_WIDTH,
			self.timer.y + 3,
			[2*L/3 for L in C.BUTTON_SIZE],
			timer=self.timer
		)

		self.active  = None
		self.tooltip = self.player.title() + " timer"

		self.image_a  = pygame.transform.scale(pygame.image.load(C.DIR_ICONS + "\\clock\\clock_" + self.player.lower() + "-a.png"),self.size)
		self.image_ba = pygame.transform.scale(pygame.image.load(C.DIR_ICONS + "\\clock\\clock_" + self.player.lower() + "-ba.png"),self.size)
		self.image_bb = pygame.transform.scale(pygame.image.load(C.DIR_ICONS + "\\clock\\clock_" + self.player.lower() + "-bb.png"),self.size)
		self.image_c  = pygame.transform.scale(pygame.image.load(C.DIR_ICONS + "\\clock\\clock_" + self.player.lower() + "-c.png"),self.size)


	def reset(self):
		self.timer.reset()


	def render(self):
		# Button
		pygame.draw.rect(
			self.display,
			self.colour,
			self.rect
		)
		self.display.blit(
			(self.image_ba if self.timer.active else self.image_bb) if self.active else (self.image_c if self.active is None else self.image_a),
			self.rect
		)

		# Elements
		self.timer.render()
		self.resetter.render()

		# Hover action
		if self.rect.collidepoint(
			self.coach.mouse_pos[0] - C.TRAY_OFFSET,
			self.coach.mouse_pos[1],
		):
			### tooltip
			self.render_tooltip(shift=(-C.TRAY_OFFSET,0))

			### cursor
			return self
		else:
			self.paint()


	def click(self):
		board = self.clock.coach.board
		white = self.clock.whiteface
		black = self.clock.blackface

		### linked
		if self.clock.linklock.linked:
			white.active = black.active = not self.active
			white.colour = black.colour = C.BUTTON_LIVE

			if self.active:
				if board.ply == "w":
					white.timer.play()
					black.timer.wait()
				else:
					white.timer.wait()
					black.timer.play()

			else:
				white.timer.stop()
				black.timer.stop()

		### unlinked
		else:
			self.active = not self.active
			self.colour = C.BUTTON_LIVE

			if self.active:
				if self.p == board.ply:
					self.timer.play()
				else:
					self.timer.wait()

			else:
				self.timer.stop()

		### sound
		self.clock.sound_clock_click.play()



class ButtonClockLinkLock(Button):
	def __init__(self , *args , clock):
		super().__init__(*args)
		self.clock = clock

		self.w = self.clock.whiteface
		self.b = self.clock.blackface

		self.linked = True
		self.locked = True

		self.states = None
		self.state  = None


	def reset(self):
		self.states = self.toggle_states()
		self.click()


	def render(self):
		self.display.blit(self.image,self.rect)
		self.render_tooltip(shift=(-C.TRAY_OFFSET,0))


	def click(self):
		self.state = next(self.states)
		self.apply()


	def apply(self):
		self.tooltip = self.state.title()
		self.image   = pygame.transform.scale(
			pygame.image.load(C.DIR_ICONS + "\\clock\\btn_linklock-" + self.state.lower() + ".png"),
			self.size
		)
		self.image.set_alpha(200)

		match self.state:
			case "LOCKED":          ### LOCKED implies LINKED
				self.locked = True
				self.linked = True

				self.w.active = self.b.active = None
				self.w.colour = self.b.colour = C.BUTTON_LOCK

				self.w.timer.stop()
				self.b.timer.stop()

			case "UNLOCKED":
				self.locked = False

				self.w.active = self.b.active = False
				self.w.colour = self.b.colour = C.BUTTON_IDLE

			case "UNLINKED":
				self.linked = False


	@staticmethod
	def toggle_states():
		while True:
			for state in (
				"LOCKED",
				"UNLOCKED",
				"UNLINKED",
			):
				yield state



class ButtonClockReset(Button):
	def __init__(self , *args , timer):
		super().__init__(*args)
		self.timer = timer

		self.trigger = self.timer.trigger

		self.tooltip = "Reset clock"
		self.image   = pygame.transform.scale(
			pygame.image.load(C.DIR_ICONS + "clock\\btn_clock_reset.png"),
			self.size
		)


	def click(self):
		self.timer.reset()

		if self.trigger.active and self.timer.active:
			self.timer.play()
		elif self.trigger.active:
			self.timer.wait()
		elif self.trigger.active is None:
			self.timer.stop()


	def render(self):
		self.display.blit(self.image,self.rect)
		self.render_tooltip(shift=(-C.TRAY_OFFSET,0))



class ButtonClockSet(Button):
	def __init__(self , *args , timer):
		super().__init__(*args)
		self.timer = timer

		self.trigger = self.timer.trigger

		self.tooltip = "Set clock"
		self.image   = pygame.transform.scale(
			pygame.image.load(C.DIR_ICONS + "clock\\btn_clock_set.png"),
			self.size
		)


	def click(self):
		print("testing123testing")


	def render(self):
		self.display.blit(self.image,self.rect)
		self.render_tooltip(shift=(-C.TRAY_OFFSET,0))



class Timer:
	def __init__(self , display , x , y , size , start , bonus , trigger):
		self.display = display
		self.x       = x
		self.y       = y
		self.size    = size
		self.start   = 100*start
		self.bonus   = 100*bonus
		self.trigger = trigger

		self.elapsed = 0

		# Mechanics
		self.time = self.start + self.bonus
		self.TICK = pygame.event.Event(pygame.event.custom_type(),player=self.trigger.player)

		self.scramble        = None
		self.scramble_toggle = None

		### alerts
		# self.beep()
		# self.buzz()
		# self.bang()

		# Interface
		self.body_colour = C.TIMER_DEAD
		self.text_colour = C.TIMER_IDLE
		self.case_colour = C.TIMER_CASE_LIVE if self.active else C.TIMER_CASE_IDLE

		self.font = pygame.font.SysFont("Consolas",28)
		self.text = self.trigger.clock.read(self.time)

		self.frame = pygame.Surface(self.size,pygame.SRCALPHA)
		self.case  = pygame.Rect(0,0,*self.size)
		self.body  = pygame.Rect(
			0.06*self.size[0],
			0.09*self.size[1],
			0.88*self.size[0],
			0.85*self.size[1]
		)


	def reset(self):
		pygame.time.set_timer(self.TICK,0)

		self.time = self.start + self.bonus
		self.text = self.trigger.clock.read(self.time)

		self.scramble        = self.time <= 10          ### 00:00:11 -> 10:00
		self.scramble_toggle = not self.time % 50

		self.stop()


	def render(self):
		self.frame.fill((0,0,0,0))
		if self.text.count(":") == 2:            ### redefined at render to respect turn control
			self.x    = self.trigger.x - C.BUTTON_WIDTH
			self.size = (
				3*C.BUTTON_WIDTH,
				(5/6)*C.BUTTON_HEIGHT
			)
		else:
			self.x    = self.trigger.x - C.BUTTON_WIDTH/2
			self.size = (
				2*C.BUTTON_WIDTH,
				(5/6)*C.BUTTON_HEIGHT
			)

		self.case = pygame.Rect(0,0,*self.size)
		self.body = pygame.Rect(
			0.06*self.size[0],
			0.09*self.size[1],
			0.88*self.size[0],
			0.85*self.size[1]
		)

		# Case & body
		pygame.draw.rect(
			self.frame,
			self.case_colour,
			self.case,
			border_radius=8
		)
		pygame.draw.rect(
			self.frame,
			self.body_colour,
			self.body,
			border_radius=5
		)

		# Text
		reading = self.font.render(self.text,True,self.text_colour)
		self.frame.blit(
			reading,
			reading.get_rect(center=[self.size[0]/2 , 2+self.size[1]/2])
		)

		self.display.blit(self.frame , (self.x,self.y))


	def tick(self):
		self.elapsed += 1

		self.time -= 1
		self.text  = self.trigger.clock.read(self.time,self.scramble)

		if self.scramble and not (self.time % 50):
			self.scramble_toggle = not self.scramble_toggle
			self.body_colour = (
				C.TIMER_SCRAMBLE,
				C.TIMER_LIVE,
			)[self.scramble_toggle]


	def play(self):
		pygame.time.set_timer(self.TICK,10)
		self.text_colour = (255,255,255)
		self.body_colour = C.TIMER_LIVE
		self.case_colour = C.TIMER_CASE_LIVE

	def wait(self):
		pygame.time.set_timer(self.TICK,0)
		self.text_colour = (255,255,255)
		self.body_colour = C.TIMER_IDLE
		self.case_colour = C.TIMER_CASE_LIVE if self.active else C.TIMER_CASE_IDLE

	def stop(self):
		pygame.time.set_timer(self.TICK,0)
		self.text_colour = C.TIMER_IDLE
		self.body_colour = C.TIMER_DEAD
		self.case_colour = C.TIMER_CASE_IDLE


	@property
	def time_elapsed(self):
		return self.start + self.bonus*(self.trigger.clock.coach.board.movenum + 1) - self.time

	@property
	def active(self):
		return self.trigger.clock.coach.board.ply == self.trigger.p



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

		# Rendering
		self.h = 2*C.TILE_HEIGHT

		self.w_afterlife = pygame.Surface((C.GAUGE_WIDTH + C.GRAVE_WIDTH, self.h),pygame.SRCALPHA)
		self.b_afterlife = pygame.Surface((C.GAUGE_WIDTH + C.GRAVE_WIDTH, self.h),pygame.SRCALPHA)

		self.w_rect = pygame.Rect(
			C.TRAY_GAP,
			0,
			C.GRAVE_WIDTH,
			self.h
		)
		self.b_rect = pygame.Rect(
			C.TRAY_GAP,
			C.WINDOW_HEIGHT - self.h,
			C.GRAVE_WIDTH,
			self.h
		)

		# Plaque
		self.mat_bal = 0
		self.w_plaque = pygame.Rect(
			self.w_rect.left + C.GAUGE_WIDTH + C.GRID_GAP,
			self.h + C.GRID_GAP,
			0,0						### auto sizes with text
		)
		self.b_plaque = pygame.Rect(
			self.w_rect.left + C.GAUGE_WIDTH + C.GRID_GAP,
			C.WINDOW_HEIGHT - self.h - self.font.size("-")[1] - C.GRID_GAP,
			0,0
		)


	def render(self):
		for is_white,graveyard,afterlife in [
			(True  , self.whites , self.w_afterlife),
			(False , self.blacks , self.b_afterlife),
		]:
			r = 0
			afterlife.fill( (30,25,25,115) if is_white else (75,70,70,115) , (C.GAUGE_WIDTH/2,0,C.GAUGE_WIDTH/2 + C.GRAVE_WIDTH,self.h) )
			for graves in graveyard.values():
				for c,fallen in enumerate(graves):
					if c < 4:
						afterlife.blit(
							pygame.transform.scale(fallen.image , [L/4 for L in C.TILE_SIZE]),
							(
								(20 +  8*c),
								( 8 + 35*r) if is_white else (self.h - 35*(r+1)),
							)
						)
					else:
						if c == 4:      ### nudge the rest
							r += 0.25

						afterlife.blit(
							pygame.transform.scale(fallen.image , (25,25)),
							(
								(25 +  8*(c-4)),
								(10 + 35*r) if is_white else (self.h - 35*(r+1)),
							)
						)
				r += 1

		self.coach.tray.blits([
			(self.w_afterlife,self.w_rect),
			(self.b_afterlife,self.b_rect),
		])

		# Material balance
		if self.mat_bal:
			self.coach.tray.blit(
				self.font.render("+"+str(abs(self.mat_bal)) , True , (185,185,185)),
				self.w_plaque if self.mat_bal < 0 else self.b_plaque
			)


	def bury(self , fallen):
		if fallen.colour == "w":
			self.whites[fallen.creed].append(fallen)
			self.mat_bal -= E.SCOREBOARD_MATERIAL[fallen.creed or "P"]
		else:
			self.blacks[fallen.creed].append(fallen)
			self.mat_bal += E.SCOREBOARD_MATERIAL[fallen.creed or "P"]


	def update(self):
		self.mat_bal = 0
		for graveyard in (self.whites,self.blacks):
			for creed,graves in graveyard.items():
				graveyard[creed].clear()

		for move in self.coach.board.movelog[:self.coach.board.halfmovenum - 1]:
			if move.capture:
				self.bury(move.capture)



class Gauge:
	def __init__(self , coach):
		self.coach = coach

		# Mechanics
		self.active = True

		self.emax = 15
		self.eval = 0

		# Interface
		self.font  = pygame.font.SysFont("Consolas",15)
		self.label = None

		self.bg_rect = pygame.Rect(C.TRAY_GAP,0,C.GAUGE_WIDTH,C.WINDOW_HEIGHT)
		self.w_rect  = pygame.Rect(
			C.TRAY_GAP,
			C.WINDOW_HEIGHT/2,
			C.GAUGE_WIDTH,
			C.WINDOW_HEIGHT/2,
		)
		self.b_rect  = pygame.Rect(
			C.TRAY_GAP,
			C.WINDOW_HEIGHT/2,
			C.GAUGE_WIDTH,
			C.WINDOW_HEIGHT/2,
		)

		self.bg_bar = pygame.Surface(self.bg_rect.size,pygame.SRCALPHA)
		self.w_bar  = None
		self.b_bar  = None


	def render(self):
		# Bars
		if self.active:
			self.coach.tray.blits([
				(self.w_bar,self.w_rect),
				(self.b_bar,self.b_rect),
			])
		else:
			self.bg_bar.fill((*C.BACKGR_GRAVE,135))
			self.coach.tray.blit(self.bg_bar,self.bg_rect)

		# Label
		if self.bg_rect.collidepoint(
			self.coach.mouse_pos[0] - C.TRAY_OFFSET,
			self.coach.mouse_pos[1]
		):
			if self.active:
				label_size = self.font.size(self.label)
				self.coach.tray.blit(
					self.font.render(self.label , True , (0,0,0) , (200,200,200)),
					(
						C.TRAY_GAP + C.GAUGE_WIDTH/2 - label_size[0]/2,
						C.WINDOW_HEIGHT/2 - label_size[1]/2
					)
				)

			### cursor
			return self


	def click(self):
		self.active = not self.active

		if self.active:
			self.bg_rect.w *= 2
		else:
			self.bg_rect.w /= 2


	def update(self):
		# Evaluate
		# print(self.coach.engine.stockfish.get_best_move())
		self.eval = self.coach.engine.evaluate()

		# Update engines
		### HAL9
		self.coach.analysis.counters["EVAL_HAL9"].value = None

		### stockfish
		if self.coach.engine.stockfish:
			self.coach.engine.stockfish.set_fen_position(self.coach.board.this_move.fen)
			match (score := self.coach.engine.stockfish.get_evaluation())["type"]:
				case "cp":
					self.coach.analysis.counters["EVAL_STOCKFISH"].value = score["value"]/100
				case "mate":
					self.coach.analysis.counters["EVAL_STOCKFISH"].value = self.emax if score["value"]>0 else -self.emax
		else:
			self.coach.analysis.counters["EVAL_STOCKFISH"].value = None

		# Update meter
		### mechanics
		self.w_rect.h = (1 + self.eval/self.emax)*C.WINDOW_HEIGHT/2
		self.b_rect.h = C.WINDOW_HEIGHT - self.w_rect.h

		if C.BOARD_FLIPPED:
			self.w_rect.y = 0
			self.b_rect.y = self.w_rect.h
		else:
			self.w_rect.y = self.b_rect.h
			self.b_rect.y = 0

		### visuals
		self.w_bar = pygame.Surface(self.w_rect.size)
		self.b_bar = pygame.Surface(self.b_rect.size)
		self.w_bar.fill((255,255,255))
		self.b_bar.fill((  0,  0,  0))

		### label
		if self.eval > 0:
			self.label = "+"
		elif self.eval < 0:
			self.label = "-"
		else:
			self.label = "±"
		self.label += f'{abs(self.eval):.2f}'
