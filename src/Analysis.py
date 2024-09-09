import pygame

from src.Constants import C
from src.Elements import *





class Analysis:
	def __init__(self , coach):
		self.coach = coach

		self.show = False
		self.font = pygame.font.SysFont("Consolas",14,bold=True)
		self.pane = pygame.Surface(C.PANE_SIZE,pygame.SRCALPHA)

		# Banners
		self.banners = {
			"DRAW CRITERIA"	: pygame.Rect(
				C.SIDEBAR_X_MARGIN,
				125,
				C.SIDEBAR_WIDTH - 3*C.SIDEBAR_X_MARGIN,
				C.TEXTBOX_HEIGHT
			),
			"EVALUATION"	: pygame.Rect(
				C.SIDEBAR_X_MARGIN,
				125 + 11*C.GRID_GAP,
				C.SIDEBAR_WIDTH - 3*C.SIDEBAR_X_MARGIN,
				C.TEXTBOX_HEIGHT
			)
		}

		# Buttons
		self.buttons = {
			### header
			"NEXT"				: ButtonNext(
				self.pane,
				C.SIDEBAR_WIDTH - 2*C.SIDEBAR_X_MARGIN - 0.8*C.BUTTON_WIDTH,
				C.SIDEBAR_Y_MARGIN + 0.1*C.BUTTON_HEIGHT,
				[0.8*L for L in C.BUTTON_SIZE],
				coach=self.coach
			),
			"PREV"				: ButtonPrevious(
				self.pane,
				C.SIDEBAR_WIDTH - 2*C.SIDEBAR_X_MARGIN - 1.6*C.BUTTON_WIDTH,
				C.SIDEBAR_Y_MARGIN + 0.1*C.BUTTON_HEIGHT,
				[0.8*L for L in C.BUTTON_SIZE],
				coach=self.coach
			),
			"SHUT"				: ButtonShut(
				self.pane,
				C.SIDEBAR_X_MARGIN + 1.075*C.BUTTON_WIDTH + C.GRID_GAP,
				C.SIDEBAR_Y_MARGIN + 0.075*C.BUTTON_HEIGHT,
				[0.85*L for L in C.BUTTON_SIZE],
				coach=self.coach
			),
			"SHOW_SETTINGS"		: ButtonShowSettings(
				self.pane,
				C.SIDEBAR_X_MARGIN,
				C.SIDEBAR_Y_MARGIN,
				coach=self.coach
			),
		}

		# Counters
		self.counters = {
			### header
			"RULE_FIFTYMOVES"	: Counter(
				self.pane,
				"Fifty Move Rule",
				0,
				self.font,
				self.banners["DRAW CRITERIA"].left,
				self.banners["DRAW CRITERIA"].bottom + C.GRID_GAP,
			),
			"RULE_THREEREPS"	: Counter(
				self.pane,
				"Threefold Repetition Rule",
				1,
				self.font,
				self.banners["DRAW CRITERIA"].left,
				self.banners["DRAW CRITERIA"].bottom + 4*C.GRID_GAP,
			),
			### evaluation
			# "SCORE_SIMPLE"				: Counter(
			# 	self.pane,
			# 	"Simple",
			# 	0,
			# 	self.font,
			# 	self.banners["EVALUATION"].left,
			# 	self.banners["EVALUATION"].bottom + C.GRID_GAP,
			# ),
			# "SCORE_STOCKFISH"			: Counter(
			# 	self.pane,
			# 	"Stockfish",
			# 	0,
			# 	self.font,
			# 	self.banners["EVALUATION"].left,
			# 	self.banners["EVALUATION"].bottom + 4*C.GRID_GAP,
			# )
		}


	def render(self):
		self.pane.fill((0,0,0,0))
		self.pane.fill(C.BACKGR_COLOUR_SETTINGS , (0,0,C.SIDEBAR_WIDTH,C.BOARD_HEIGHT))

		for subtitle,banner in self.banners.items():
			text = self.font.render(subtitle,True,C.BUTTON_COLOUR_NEUTRAL)
			pygame.draw.rect(
				self.pane,
				C.BANNER_COLOUR,
				banner
			)
			self.pane.blit(text , text.get_rect(center=banner.center))

		for button in self.buttons.values():
			button.render()
			if not button.dropdown and button is not self.buttons["SHUT"]:
				button.colour = C.BUTTON_COLOUR_ACTIVE if button.active else C.BUTTON_COLOUR_NEUTRAL

		for counter in self.counters.values():
			counter.render()
