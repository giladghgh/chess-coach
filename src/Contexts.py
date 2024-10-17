import pygame

from src.Elements import *





class Context:
	def __init__(self , coach):
		self.coach = coach

		self.show = False
		self.font = pygame.font.SysFont("Consolas",14,bold=True)
		self.pane = pygame.Surface(C.PANE_SIZE,pygame.SRCALPHA)

		self.colour = None

		self.rect = pygame.Rect(
			0,
			0,
			C.X_MARGIN + C.TEXTBOX_WIDTH + C.X_MARGIN + C.GRID_GAP,
			C.BOARD_HEIGHT
		)

		self.tab = (

		)

		self.banners = {}
		self.counters = {}
		self.writers = {}

		self.buttons_nav = {}
		self.buttons = {
			**self.buttons_nav,
		}

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
		]:
			element.render()

		### buttons
		hovering = None
		for button in self.buttons.values():
			button.render()

			### hover mechanics
			if button.dropdown:
				if button.rect.collidepoint(self.coach.mouse_pos):
					hovering = button
				else:
					button.colour = C.BUTTON_LOOM if button.active else C.BUTTON_IDLE
					for option in button.dropdown:
						if button.active and option.rect.collidepoint(self.coach.mouse_pos):
							hovering = option
						else:
							option.paint()
			else:
				if button.active is not None and button.rect.collidepoint(self.coach.mouse_pos):
					hovering = button
				else:
					button.paint()

		self.coach.screen.blit(self.pane,(0,0))

		return hovering


	def handle_click(self , event):
		hits = []

		# Buttons
		for button in self.buttons.values():
			if button.rect.collidepoint(event.pos):
				hits.append(button)

			### dropdowns
			elif button.active:
				for option in button.dropdown:
					if option.rect.collidepoint(event.pos):
						hits.append(option)
						break                       ### so Sliders can be held
					button.active = False           ### so opening one dropdown closes all others

		# Writers
		for writer in self.writers.values():
			if writer.rect.collidepoint(event.pos):
				hits.append(writer)
			else:
				writer.kill()

		return hits


	def tidy(self , and_exit=False):
		# Collapse dropdowns
		for button in self.buttons.values():
			if button.dropdown:
				button.active = False

		# Deactivate writers
		for writer in self.writers.values():
			writer.kill()

		# Leave graciously
		if and_exit:
			for context in self.coach.contexts:
				context.show = False


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
			"AUTO_PROMO" : ButtonAutoPromo(
				self.coach,
				self.pane,
				*self.arrange("GAMEPLAY",1,1)
			),
		}
		self.buttons_ui = {
			"B_STYLIST"	    : ButtonStyleBoard(
				self.coach,
				self.pane,
				*self.arrange("UI",2,1)
			),
			"LEGAL_MOVES"   : ButtonLegalMoves(
				self.coach,
				self.pane,
				*self.arrange("UI",1,1)
			),
			"P_STYLIST"		: ButtonStylePieces(
				self.coach,
				self.pane,
				*self.arrange("UI",2,2)
			),
			"COORDS"		: ButtonCoords(
				self.coach,
				self.pane,
				*self.arrange("UI",1,2)
			),
			"SPEDOMETER"	: ButtonSpedometer(
				self.coach,
				self.pane,
				*self.arrange("UI",2,3)
			),
			"FRESH_MOVES"	: ButtonFreshMoves(
				self.coach,
				self.pane,
				*self.arrange("UI",1,3)
			),
			"VOLUME"        : ButtonVolume(
				self.coach,
				self.pane,
				*self.arrange("UI",2,4)
			),
			"FLIP"		    : ButtonFlip(
				self.coach,
				self.pane,
				*self.arrange("UI",1,4)
			),
		}
		self.buttons_io = {
			"EXPORT"		: ButtonExport(
				self.coach,
				self.pane,
				*self.arrange("I/O",2,1)
			),
			"IMPORT"		: ButtonImport(
				self.coach,
				self.pane,
				*self.arrange("I/O",1,1)
			),
		}
		self.buttons.update(
			**self.buttons_gameplay,
			**self.buttons_ui,
			**self.buttons_io,
		)

		# Writers
		from datetime import datetime

		self.writers = {
			"EVENT" : Writer(
				self,
				C.X_MARGIN,
				self.buttons_io["EXPORT"].y + C.BUTTON_HEIGHT + 1*C.GRID_GAP,
				C.TEXTBOX_WIDTH,
				"Event"
			),
			"SITE" : Writer(
				self,
				C.X_MARGIN,
				self.buttons_io["EXPORT"].y + C.BUTTON_HEIGHT + 4*C.GRID_GAP,
				C.TEXTBOX_WIDTH,
				"Gilad's Bedroom, U.K."
			),
			"WHITE" : Writer(
				self,
				C.X_MARGIN,
				self.buttons_io["EXPORT"].y + C.BUTTON_HEIGHT + 7*C.GRID_GAP,
				(5.25/11)*C.TEXTBOX_WIDTH,
				"Jack White"
			),
			"BLACK" : Writer(
				self,
				C.X_MARGIN + (5.75/11)*C.TEXTBOX_WIDTH,
				self.buttons_io["EXPORT"].y + C.BUTTON_HEIGHT + 7*C.GRID_GAP,
				(5.25/11)*C.TEXTBOX_WIDTH,
				"Jack Black"
			),
			"DATE" : Writer(
				self,
				C.X_MARGIN,
				self.buttons_io["EXPORT"].y + C.BUTTON_HEIGHT + 10*C.GRID_GAP,
				(4/11)*C.TEXTBOX_WIDTH,
				datetime.today().strftime("%Y-%m-%d")
			),
			"ROUND" : Writer(
				self,
				C.X_MARGIN + (4.5/11)*C.TEXTBOX_WIDTH,
				self.buttons_io["EXPORT"].y + C.BUTTON_HEIGHT + 10*C.GRID_GAP,
				(3/11)*C.TEXTBOX_WIDTH,
				"Round"
			),
			"MODE" : Writer(
				self,
				C.X_MARGIN + (8/11)*C.TEXTBOX_WIDTH,
				self.buttons_io["EXPORT"].y + C.BUTTON_HEIGHT + 10*C.GRID_GAP,
				(3/11)*C.TEXTBOX_WIDTH,
				"LCP"
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
		# self.buttons_nav.update(
		#   **self.buttons_engine,
		# )



class Coaching(Context):
	def __init__(self , *args):
		super().__init__(*args)

		self.colour = C.BACKGR_COACHING

		# Banners
		self.banners = {
			"ALRIGHT LISTEN UP!"	: pygame.Rect(
				C.X_MARGIN,
				C.Y_MARGIN + 1*(C.BUTTON_HEIGHT + 3*C.GRID_GAP) + C.GRID_GAP,
				*C.TEXTBOX_SIZE
			),
		}

		# Buttons
		# self.buttons_drills = {
		#
		# }
		# self.buttons_nav.update(
		#   **self.buttons_drills,
		# )
