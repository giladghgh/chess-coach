import pygame

from src.Elements import *





class Context:
	def __init__(self , coach):
		self.coach = coach

		self.show = False
		self.font = pygame.font.SysFont("Consolas",14,bold=True)
		self.pane = pygame.Surface(C.PANE_SIZE,pygame.SRCALPHA)

		self.colour = None
		self.rect   = pygame.Rect(
			0,
			0,
			C.X_MARGIN + C.TEXTBOX_WIDTH + C.X_MARGIN + C.GRID_GAP,
			C.BOARD_HEIGHT
		)

		self.banners = {}
		self.counters = {}
		self.writers = {}

		self.context_menu = {}
		self.buttons = {
			**self.context_menu,
		}

	def __repr__(self):
		return type(self).__name__

	def plug_in(self):
		index = self.coach.contexts.index(self)

		for context in self.coach.contexts:
			if context is self:
				self.context_menu["SHUT"] = ButtonContextShut(
					self.pane,
					C.X_MARGIN + index*(C.BUTTON_WIDTH + C.GRID_GAP),
					C.Y_MARGIN,
					coach=self.coach
				)
			else:
				context.context_menu[str(self).upper()] = ButtonContextOpen(
					context.pane,
					C.X_MARGIN + index*(C.BUTTON_WIDTH + C.GRID_GAP),
					C.Y_MARGIN,
					context=self,
					coach=context.coach
				)
			context.buttons.update(
				**context.context_menu,
			)

	def render(self):
		self.pane.fill((0,0,0,0))
		self.pane.fill(self.colour,self.rect)

		# Banners
		for subtitle,banner in self.banners.items():
			text = self.font.render(subtitle,True,C.BUTTON_IDLE)
			pygame.draw.rect(
				self.pane,
				C.BANNER_COLOUR,
				banner
			)
			self.pane.blit(text , text.get_rect(center=banner.center))

		# Elements
		for element in [
			*self.writers.values(),
			*self.counters.values(),
			*self.buttons.values(),
		]:
			element.render()

		self.coach.screen.blit(self.pane,(0,0))

	def collapse_dropdowns(self):
		for button in self.buttons.values():
			if button.dropdown:
				button.active = False

	def handle_click(self , event):
		hits = []

		# Buttons
		for button in self.buttons.values():
			if button.rect.collidepoint(event.pos):
				# button.click()
				hits.append(button)

			### dropdowns
			elif button.active:
				for option in button.dropdown:
					if option.rect.collidepoint(event.pos):
						# option.click()
						hits.append(option)
						break
					button.active = False

		# Writers
		for writer in self.writers.values():
			if writer.rect.collidepoint(event.pos):
				hits.append(writer)

		return hits

	def arrange(self , ban , col , row , shift=(0,0) , scale=(1,1)):
		return (
			self.banners[ban].x + shift[0] + scale[0]*(
					(col-1)*(C.BUTTON_WIDTH + 5*C.GRID_GAP)
			),
			self.banners[ban].y + shift[1] + scale[1]*(
					(row-1)*(C.BUTTON_HEIGHT + 3*C.GRID_GAP) + C.TEXTBOX_HEIGHT + C.GRID_GAP
			),
		)



class Settings(Context):
	def __init__(self , *args):
		super().__init__(*args)

		from datetime import datetime

		self.colour = C.BACKGR_SETTINGS

		# Banners
		self.banners = {
			"GAMEPLAY"  : pygame.Rect(
				C.X_MARGIN,
				C.Y_MARGIN + 1*(C.BUTTON_HEIGHT + 3*C.GRID_GAP) + C.GRID_GAP,
				*C.TEXTBOX_SIZE
			),
			"UI"        : pygame.Rect(
				C.X_MARGIN,
				C.Y_MARGIN + 2.5*(C.BUTTON_HEIGHT + 3*C.GRID_GAP) + C.GRID_GAP,
				*C.TEXTBOX_SIZE
			),
			"I/O"       : pygame.Rect(
				C.X_MARGIN,
				C.Y_MARGIN + 7*(C.BUTTON_HEIGHT + 3*C.GRID_GAP) + C.GRID_GAP,
				*C.TEXTBOX_SIZE
			),
		}

		# Buttons
		self.buttons_gameplay = {
			"FLIP"		 : ButtonFlip(
				self.pane,
				*self.arrange("GAMEPLAY",2,1),
				coach=self.coach
			),
			"AUTO_PROMO" : ButtonAutoPromo(
				self.pane,
				*self.arrange("GAMEPLAY",1,1)
			),
		}
		self.buttons_ui = {
			"B_STYLIST"	    : ButtonBoardStylist(
				self.pane,
				*self.arrange("UI",2,1),
				board=self.coach.board
			),
			"ECOInterpreter": ButtonECOInterpreter(
				self.pane,
				*self.arrange("UI",1,1),
				C.BUTTON_SIZE,
				True,
				coach=self.coach
			),
			"P_STYLIST"		: ButtonPieceStylist(
				self.pane,
				*self.arrange("UI",2,2),
				board=self.coach.board
			),
			"LEGAL_MOVES"   : ButtonLegalMoves(
				self.pane,
				*self.arrange("UI",1,2),
				C.BUTTON_SIZE,
				True,
				board=self.coach.board
			),
			"SPEDOMETER"	: ButtonSpedometer(
				self.pane,
				*self.arrange("UI",2,3),
			),
			"COORDS"		: ButtonCoords(
				self.pane,
				*self.arrange("UI",1,3),
				board=self.coach.board
			),
			"FRESH_MOVES"	: ButtonFreshMoves(
				self.pane,
				*self.arrange("UI",1,4),
				C.BUTTON_SIZE,
				True,
				board=self.coach.board
			),
		}
		self.buttons_io = {
			"EXPORT"		: ButtonExport(
				self.pane,
				*self.arrange("I/O",1,1),
				coach=self.coach
			),
			"IMPORT"		: ButtonImport(
				self.pane,
				*self.arrange("I/O",1,2 , shift=(0,C.GRID_GAP)),
				coach=self.coach
			),
		}
		self.buttons.update(
			**self.buttons_gameplay,
			**self.buttons_ui,
			**self.buttons_io,
		)

		# Writers
		self.writers = {
			"TITLE" : Writer(
				self.pane,
				C.X_MARGIN + C.BUTTON_WIDTH + C.GRID_GAP,
				self.banners["I/O"].bottom + 1*C.GRID_GAP,
				C.TEXTBOX_WIDTH - C.BUTTON_WIDTH - C.GRID_GAP,
				"Title"
			),
			"DATE"  : Writer(
				self.pane,
				C.X_MARGIN + C.BUTTON_WIDTH + C.GRID_GAP,
				self.banners["I/O"].bottom + 4*C.GRID_GAP,
				C.TEXTBOX_WIDTH - C.BUTTON_WIDTH - C.GRID_GAP,
				datetime.today().strftime("%Y-%m-%d")
			),
			"WHITE" : Writer(
				self.pane,
				C.X_MARGIN + C.BUTTON_WIDTH + C.GRID_GAP,
				self.banners["I/O"].bottom + 7*C.GRID_GAP,
				(5/11)*(C.TEXTBOX_WIDTH - C.BUTTON_WIDTH - C.GRID_GAP),
				"White"
			),
			"BLACK" : Writer(
				self.pane,
				C.X_MARGIN + C.BUTTON_WIDTH + (3/8)*C.TEXTBOX_WIDTH + 1.5*C.GRID_GAP,
				self.banners["I/O"].bottom + 7*C.GRID_GAP,
				(5/11)*(C.TEXTBOX_WIDTH - C.BUTTON_WIDTH - C.GRID_GAP),
				"Black"
			),
		}



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
				C.Y_MARGIN + 2.5*(C.BUTTON_HEIGHT + 3*C.GRID_GAP) + C.GRID_GAP,
				*C.TEXTBOX_SIZE
			),
			"DRAW CRITERIA"       : pygame.Rect(
				C.X_MARGIN,
				C.Y_MARGIN + 8*(C.BUTTON_HEIGHT + 3*C.GRID_GAP) + C.GRID_GAP,
				*C.TEXTBOX_SIZE
			),
		}

		# Counters
		self.counters = {
			### drawers
			"RULECOUNT_FIFTYMOVES"	: Counter(
				self.pane,
				self.banners["DRAW CRITERIA"].left,
				self.banners["DRAW CRITERIA"].bottom + C.GRID_GAP,
				"Fifty Move Rule",
				"0"
			),
			"RULECOUNT_THREEREPS"	: Counter(
				self.pane,
				self.banners["DRAW CRITERIA"].left,
				self.banners["DRAW CRITERIA"].bottom + 4*C.GRID_GAP,
				"Threefold Repetition Rule",
				"1"
			),
			### evaluation
			"SCORE_SIMPLE"	        : Counter(
				self.pane,
				self.banners["EVALUATION"].left,
				self.banners["EVALUATION"].bottom + C.GRID_GAP,
				"Simple",
				"0.00"
			),
			"SCORE_STOCKFISH"       : Counter(
				self.pane,
				self.banners["EVALUATION"].left,
				self.banners["EVALUATION"].bottom + 4*C.GRID_GAP,
				"Stockfish",
				"0.00"
			),
		}

		# Buttons
		# self.buttons_engine = {
		#
		# }
		# self.context_menu.update(
		#   **self.buttons_engine,
		# )



class Coaching(Context):
	def __init__(self , *args):
		super().__init__(*args)

		self.colour = C.BACKGR_COACHING

		# Banners
		self.banners = {
			"ALRIGHT LISTEN UP..."	: pygame.Rect(
				C.X_MARGIN,
				C.Y_MARGIN + 1*(C.BUTTON_HEIGHT + 3*C.GRID_GAP) + C.GRID_GAP,
				*C.TEXTBOX_SIZE
			),
		}

		# Buttons
		# self.buttons_drill = {
		#
		# }
		# self.context_menu.update(
		#   **self.buttons_drill,
		# )
