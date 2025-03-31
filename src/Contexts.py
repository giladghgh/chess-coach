from datetime import datetime

from src.Elements import *





class Context:
	def __init__(self , coach):
		self.coach = coach

		self.show = False
		self.font = pygame.font.SysFont("Consolas",14,bold=True)
		self.pane = pygame.Surface(C.PANE_SIZE,pygame.SRCALPHA)

		# Rendering
		self.colour = None
		self.rect   = pygame.Rect(
			0,
			0,
			C.X_MARGIN + C.TEXTBOX_WIDTH + C.X_MARGIN + C.GRID_GAP,
			C.BOARD_HEIGHT
		)

		self.tab = ()

		self.hovering = None

		# Elements
		self.banners  = {}
		self.counters = {}
		self.writers  = {}

		self.buttons_nav = {}
		self.buttons = {
			**self.buttons_nav,
		}

		self.shapes   = {}

	def __repr__(self):
		return type(self).__name__


	def plug_in(self):
		index = self.coach.contexts.index(self)

		### populate other contexts with navigation buttons to this one.
		for context in self.coach.contexts:
			if context is self:
				self.buttons_nav["EXIT"] = ButtonContextExit(
					self.coach,
					self.pane,
					C.X_MARGIN + index*(C.BUTTON_WIDTH + C.GRID_GAP),
					C.Y_MARGIN
				)
			else:
				context.buttons_nav[str(self).upper()] = ButtonContextOpen(
					self.coach,
					context.pane,
					C.X_MARGIN + index*(C.BUTTON_WIDTH + C.GRID_GAP),
					C.Y_MARGIN,
					context=self
				)
			context.buttons.update(
				**context.buttons_nav,
			)


	def render(self):
		self.pane.fill((0,0,0,0))
		self.pane.fill(self.colour,self.rect)

		self.hovering = None

		# Title
		for i,char in enumerate(myself := str(self).upper()):
			self.pane.blit(
				self.font.render(char , True , [(4/5)*c for c in C.BANNER_COLOUR]),
				( C.X_MARGIN + (2/3)*(i/len(myself))*C.TEXTBOX_WIDTH + 40 , C.Y_MARGIN + C.BUTTON_HEIGHT + 2*C.GRID_GAP )
			)

		# Banners
		for subtitle,banner in self.banners.items():
			pygame.draw.rect(
				self.pane,
				C.BANNER_COLOUR,
				banner
			)
			self.pane.blit(
				text := self.font.render(subtitle,True,C.BUTTON_IDLE),
				text.get_rect(center=banner.center),
			)

		# Elements
		### shapes
		# for colour,x,y,w,h in self.shapes.values():
		# 	surf = pygame.Surface(
		# 		(w,h),
		# 		flags=pygame.SRCALPHA
		# 	)
		# 	surf.fill(colour)
		# 	self.pane.blit(surf,(x,y))

		### writers
		for writer in self.writers.values():
			writer.render()

			### hover mechanics
			if writer.active is not None:
				writer.paint()
				if writer.rect.collidepoint(self.coach.mouse_pos):
					self.hovering = writer

		### buttons
		for button in self.buttons.values():
			button.render()

			### hover mechanics
			if button.active is not None and button.rect.collidepoint(self.coach.mouse_pos):
				self.hovering = button
			else:
				button.paint()

			if button.dropdown and (button.dropdown.persist or button.dropdown.active):
				for option in button.dropdown:
					if option.active is not None and option.rect.collidepoint(self.coach.mouse_pos):
						self.hovering = option
					else:
						option.paint()

		### counters
		for counter in self.counters.values():
			counter.render()

		self.coach.screen.blit(self.pane,(0,0))


	def handle_click(self , event):
		clicks = []

		# Buttons
		for button in self.buttons.values():
			if button.rect.collidepoint(event.pos):
				clicks.append(button)

			elif button.dropdown and (button.dropdown.persist or button.dropdown.active):
				for option in button.dropdown:
					if option.rect.collidepoint(event.pos):
						clicks.append(option)
						break                                   ### so Sliders can be held
					button.active          = False              ### so opening one dropdown closes all others
					button.dropdown.active = False

		# Writers
		for writer in self.writers.values():
			if writer.rect.collidepoint(event.pos):
				clicks.append(writer)
			else:
				writer.kill()

		# Counters
		for counter in self.counters.values():
			if counter.bkgr.get_rect(topleft=(counter.x,counter.y)).collidepoint(event.pos):
				clicks.append(counter)

		return clicks


	def tidy(self):
		# Collapse dropdowns
		for button in self.buttons.values():
			if button.dropdown and not button.dropdown.persist:
				button.dropdown.active = False

		# Deactivate writers
		for writer in self.writers.values():
			writer.kill()


	def gridify(self , ban , col , row , shift=(0,0)):
		return (
			shift[0] + self.banners[ban].x + (
					(col-1)*(C.BUTTON_WIDTH + 5*C.GRID_GAP)
			),
			shift[1] + self.banners[ban].y + (
					(row-1)*(C.BUTTON_HEIGHT + 3*C.GRID_GAP) + C.TEXTBOX_HEIGHT + C.GRID_GAP
			),
		)



class Settings(Context):
	def __init__(self , *args):
		super().__init__(*args)

		self.colour = C.BACKGR_SETTINGS

		# Banners
		self.banners = {
			"GAMEPLAY"  : pygame.Rect(
				C.X_MARGIN,
				C.Y_MARGIN + 1*(C.BUTTON_HEIGHT + 3*C.GRID_GAP) + C.GRID_GAP,
				*C.TEXTBOX_SIZE
			),
			"INTERFACE"        : pygame.Rect(
				C.X_MARGIN,
				C.Y_MARGIN + 2.5*(C.BUTTON_HEIGHT + 3*C.GRID_GAP) + C.GRID_GAP,
				*C.TEXTBOX_SIZE
			),
			"FILE I/O"       : pygame.Rect(
				C.X_MARGIN,
				C.Y_MARGIN + 7*(C.BUTTON_HEIGHT + 3*C.GRID_GAP) + C.GRID_GAP,
				*C.TEXTBOX_SIZE
			),
		}

		# Writers
		self.writers = {
			"EVENT" : Writer(
				self,
				self.pane,
				C.X_MARGIN,
				self.gridify("FILE I/O",2,1)[1] + C.BUTTON_HEIGHT + 1*C.GRID_GAP,
				C.TEXTBOX_WIDTH,
				C.TEXTBOX_HEIGHT,
				"Event"
			),
			"SITE" : Writer(
				self,
				self.pane,
				C.X_MARGIN,
				self.gridify("FILE I/O",2,1)[1] + C.BUTTON_HEIGHT + 4*C.GRID_GAP,
				C.TEXTBOX_WIDTH,
				C.TEXTBOX_HEIGHT,
				"Gilad's Bedroom, U.K."
			),
			"WHITE" : Writer(
				self,
				self.pane,
				C.X_MARGIN,
				self.gridify("FILE I/O",2,1)[1] + C.BUTTON_HEIGHT + 7*C.GRID_GAP,
				(5.25/11)*C.TEXTBOX_WIDTH,
				C.TEXTBOX_HEIGHT,
				"Jack White"
			),
			"BLACK" : Writer(
				self,
				self.pane,
				C.X_MARGIN + (5.75/11)*C.TEXTBOX_WIDTH,
				self.gridify("FILE I/O",2,1)[1] + C.BUTTON_HEIGHT + 7*C.GRID_GAP,
				(5.25/11)*C.TEXTBOX_WIDTH,
				C.TEXTBOX_HEIGHT,
				"Jack Black"
			),
			"DATE" : Writer(
				self,
				self.pane,
				C.X_MARGIN,
				self.gridify("FILE I/O",2,1)[1] + C.BUTTON_HEIGHT + 10*C.GRID_GAP,
				(4/11)*C.TEXTBOX_WIDTH,
				C.TEXTBOX_HEIGHT,
				datetime.today().strftime("%Y-%m-%d")
			),
			"ROUND" : Writer(
				self,
				self.pane,
				C.X_MARGIN + (4.5/11)*C.TEXTBOX_WIDTH,
				self.gridify("FILE I/O",2,1)[1] + C.BUTTON_HEIGHT + 10*C.GRID_GAP,
				(3/11)*C.TEXTBOX_WIDTH,
				C.TEXTBOX_HEIGHT,
				"Round"
			),
			"MODE" : Writer(
				self,
				self.pane,
				C.X_MARGIN + (8/11)*C.TEXTBOX_WIDTH,
				self.gridify("FILE I/O",2,1)[1] + C.BUTTON_HEIGHT + 10*C.GRID_GAP,
				(3/11)*C.TEXTBOX_WIDTH,
				C.TEXTBOX_HEIGHT,
				"LCP"
			),
		}

		# Buttons
		self.buttons_gp = {
			"AUTO_PROMO" : ButtonAutoPromote(
				self.coach,
				self.pane,
				*self.gridify("GAMEPLAY",2,1)
			),
			"AUTO_DRAW" : ButtonAutoDraw(
				self.coach,
				self.pane,
				*self.gridify("GAMEPLAY",1,1)
			),
		}
		self.buttons_ui = {
			"B_STYLIST"	    : ButtonDesignBoard(
				self.coach,
				self.pane,
				*self.gridify("INTERFACE",2,1)
			),
			"LEGAL_MOVES"   : ButtonLegalMoves(
				self.coach,
				self.pane,
				*self.gridify("INTERFACE",1,1)
			),
			"P_STYLIST"		: ButtonDesignPieces(
				self.coach,
				self.pane,
				*self.gridify("INTERFACE",2,2)
			),
			"COORDS"		: ButtonCoords(
				self.coach,
				self.pane,
				*self.gridify("INTERFACE",1,2)
			),
			"SPEDOMETER"	: ButtonSpedometer(
				self.coach,
				self.pane,
				*self.gridify("INTERFACE",2,3)
			),
			"FRESH_MOVES"	: ButtonFreshMoves(
				self.coach,
				self.pane,
				*self.gridify("INTERFACE",1,3)
			),
			"VOLUME"        : ButtonVolume(
				self.coach,
				self.pane,
				*self.gridify("INTERFACE",2,4)
			),
			"FLIP"		    : ButtonFlip(
				self.coach,
				self.pane,
				*self.gridify("INTERFACE",1,4)
			),
		}
		self.buttons_io = {
			"EXPORT"		: ButtonExport(
				self.coach,
				self.pane,
				*self.gridify("FILE I/O",2,1)
			),
			"IMPORT"		: ButtonImport(
				self.coach,
				self.pane,
				*self.gridify("FILE I/O",1,1)
			),
		}
		self.buttons.update(
			**self.buttons_gp,
			**self.buttons_ui,
			**self.buttons_io,
		)



class Analysis(Context):
	def __init__(self , *args):
		super().__init__(*args)

		self.colour = C.BACKGR_ANALYSIS

		# Banners
		self.banners = {
			"TOP LINES"	    : pygame.Rect(
				C.X_MARGIN,
				C.Y_MARGIN + 1*(C.BUTTON_HEIGHT + 3*C.GRID_GAP) + C.GRID_GAP,
				*C.TEXTBOX_SIZE
			),
			"EVALUATION"    : pygame.Rect(
				C.X_MARGIN,
				C.Y_MARGIN + 2.75*(C.BUTTON_HEIGHT + 3*C.GRID_GAP) + C.GRID_GAP,
				*C.TEXTBOX_SIZE
			),
			"DRAW CRITERIA" : pygame.Rect(
				C.X_MARGIN,
				C.Y_MARGIN + 7*(C.BUTTON_HEIGHT + 3*C.GRID_GAP) + C.GRID_GAP,
				*C.TEXTBOX_SIZE
			),
		}

		# Counters
		self.counters = {
			### drawers
			"RULECOUNT_FIFTYMOVES"	: Counter(
				self,
				self.banners["DRAW CRITERIA"].left,
				self.banners["DRAW CRITERIA"].bottom + 1*C.GRID_GAP,
				"Fifty Move Rule"
			),
			"RULECOUNT_THREEREPS"   : Counter(
				self,
				self.banners["DRAW CRITERIA"].left,
				self.banners["DRAW CRITERIA"].bottom + 4*C.GRID_GAP,
				"Threefold Repetition Rule"
			),
			### evaluators
			"SCORE_HAL90"       : Counter(
				self,
				self.banners["EVALUATION"].left,
				self.banners["EVALUATION"].bottom + 1*C.GRID_GAP,
				"HAL90",
				polarise=True
			),
			"SCORE_STOCKFISH"   : Counter(
				self,
				self.banners["EVALUATION"].left,
				self.banners["EVALUATION"].bottom + 4*C.GRID_GAP,
				"Stockfish",
				polarise=True
			),
			### line display
			"TOPLINE1"  : Counter(
				self,
				self.banners["TOP LINES"].left,
				self.banners["TOP LINES"].bottom + 1*C.GRID_GAP,
				"L1",
				polarise=True
			),
			"TOPLINE2"  : Counter(
				self,
				self.banners["TOP LINES"].left,
				self.banners["TOP LINES"].bottom + 4*C.GRID_GAP,
				"L2",
				polarise=True
			),
			"TOPLINE3"  : Counter(
				self,
				self.banners["TOP LINES"].left,
				self.banners["TOP LINES"].bottom + 7*C.GRID_GAP,
				"L3",
				polarise=True
			)
		}

		# Buttons
		self.buttons_topl = {
			f'TOPLINE{i}' : ButtonTopLine(
				self.coach,
				self.pane,
				self.counters[f'TOPLINE{i}'].x,
				self.counters[f'TOPLINE{i}'].y,
				(
					C.TEXTBOX_WIDTH - self.counters[f'TOPLINE{i}'].size[0],
					C.TEXTBOX_HEIGHT + 1
				),
				i=i
			)
			for i in range(1,4)
		}
		self.buttons_bots = {
			"BOT_WHITE"	: ButtonBot(
				self.coach,
				self.pane,
				*self.gridify("EVALUATION",2,1,shift=(0,C.BUTTON_HEIGHT+2*C.GRID_GAP)),
				player="WHITE",
				persist=False
			),
			"BOT_BLACK"	: ButtonBot(
				self.coach,
				self.pane,
				*self.gridify("EVALUATION",1,1,shift=(0,C.BUTTON_HEIGHT+2*C.GRID_GAP)),
				player="BLACK",
				persist=False
			),
		}
		self.buttons.update(
			**self.buttons_topl,
			**self.buttons_bots,
		)

		# Shapes
		# self.shapes = {
		# 	"TOPLINE1_LABEL"    : (
		# 		(*C.TEXTBOX_LOOM,100),
		# 		self.counters["TOPLINE1"].x + self.counters["TOPLINE1"].size[0],
		# 		self.counters["TOPLINE1"].y,
		# 		C.TEXTBOX_WIDTH - self.counters["TOPLINE1"].size[0],
		# 		C.TEXTBOX_HEIGHT + 1,
		# 	),
		# 	"TOPLINE2_LABEL"    : (
		# 		(*C.TEXTBOX_LOOM,100),
		# 		self.counters["TOPLINE2"].x + self.counters["TOPLINE2"].size[0],
		# 		self.counters["TOPLINE2"].y,
		# 		C.TEXTBOX_WIDTH - self.counters["TOPLINE1"].size[0],
		# 		C.TEXTBOX_HEIGHT + 1,
		# 	),
		# 	"TOPLINE3_LABEL"    : (
		# 		(*C.TEXTBOX_LOOM,100),
		# 		self.counters["TOPLINE3"].x + self.counters["TOPLINE3"].size[0],
		# 		self.counters["TOPLINE3"].y,
		# 		C.TEXTBOX_WIDTH - self.counters["TOPLINE3"].size[0],
		# 		C.TEXTBOX_HEIGHT + 1,
		# 	),
		# }



class Coaching(Context):
	def __init__(self , *args):
		super().__init__(*args)

		self.colour = C.BACKGR_COACHING

		self.drilling = None

		# Banners
		self.banners = {
			"ALRIGHT LISTEN UP!"    : pygame.Rect(
				C.X_MARGIN,
				C.Y_MARGIN + 1*(C.BUTTON_HEIGHT + 3*C.GRID_GAP) + C.GRID_GAP,
				*C.TEXTBOX_SIZE
			),
			"BASIC TRAINING"        : pygame.Rect(
				C.X_MARGIN,
				C.Y_MARGIN + 4*(C.BUTTON_HEIGHT + 3*C.GRID_GAP) + C.GRID_GAP,
				*C.TEXTBOX_SIZE
			),
			"SPECIALIST TRAINING"        : pygame.Rect(
				C.X_MARGIN,
				C.Y_MARGIN + 6*(C.BUTTON_HEIGHT + 3*C.GRID_GAP) + C.GRID_GAP,
				*C.TEXTBOX_SIZE
			),
		}

		# Buttons
		self.buttons_drills = {
			"DRILLS"    : ButtonDrills(
				self.coach,
				self.pane,
				*self.gridify("BASIC TRAINING",1,1)
			),
		}
		self.buttons.update(
			**self.buttons_drills,
		)

