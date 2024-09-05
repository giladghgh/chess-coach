import pygame

from src.Constants import C
from src.Elements import *





class Analysis:
	def __init__(self , coach):
		self.coach = coach

		self.show = False
		self.font = pygame.font.SysFont("Consolas",14,bold=True)
		self.pane = pygame.Surface((C.SIDEBAR_WIDTH,C.BOARD_HEIGHT))

		# Banners
		self.banners = {
			"COUNTERS"		: pygame.Rect(
				C.SIDEBAR_X_MARGIN,
				125,
				C.SIDEBAR_WIDTH - 3*C.SIDEBAR_X_MARGIN,
				C.TEXTBOX_HEIGHT
			),
			"EVALUATION"	: pygame.Rect(
				C.SIDEBAR_X_MARGIN,
				265,
				C.SIDEBAR_WIDTH - 3*C.SIDEBAR_X_MARGIN,
				C.TEXTBOX_HEIGHT
			)
		}

		# Buttons
		self.buttons = {
			### header
			"NEXT"				: ButtonNext(
				self.coach,
				"NEXT",
				C.SIDEBAR_WIDTH - 2*C.SIDEBAR_X_MARGIN - 0.8*C.BUTTON_WIDTH,
				C.SIDEBAR_Y_MARGIN + 0.1*C.BUTTON_HEIGHT,
				self,
				[0.8*L for L in C.BUTTON_SIZE]
			),
			"PREV"				: ButtonPrevious(
				self.coach,
				"PREVIOUS",
				C.SIDEBAR_WIDTH - 2*C.SIDEBAR_X_MARGIN - 1.6*C.BUTTON_WIDTH,
				C.SIDEBAR_Y_MARGIN + 0.1*C.BUTTON_HEIGHT,
				self,
				[0.8*L for L in C.BUTTON_SIZE]
			),
			"SHOW_ANALYSIS"		: ButtonShowAnalysis(
				self.coach,
				"SHOW_ANALYSIS",
				C.SIDEBAR_X_MARGIN + C.BUTTON_WIDTH + C.GRID_GAP,
				C.SIDEBAR_Y_MARGIN,
				self
			),
			"SHUT_SETTINGS"		: ButtonShut(
				self.coach,
				"SHUT_SETTINGS",
				C.SIDEBAR_X_MARGIN + 0.05*C.BUTTON_WIDTH,
				C.SIDEBAR_Y_MARGIN + 0.05*C.BUTTON_HEIGHT,
				self,
				[0.9*L for L in C.BUTTON_SIZE]
			),
		}

		# Counters
		self.counters = {
			"RULE_FIFTYMOVES"	: Counter(
				self.coach,
				"Fifty Move Rule",
				0,
				self.font,
				C.SIDEBAR_X_MARGIN,
				self.banners["COUNTERS"].y + 25,
				self.pane
			),
			"RULE_THREEREPS"	: Counter(
				self.coach,
				"Threefold Repetition Rule",
				1,
				self.font,
				C.SIDEBAR_X_MARGIN,
				self.banners["COUNTERS"].y + 55,
				self.pane
			),
		}


	def render(self):
		self.coach.display.blit(self.pane,(0,0))
		self.pane.fill(C.BACKGR_COLOUR_SETTINGS)

		for subtitle,banner in self.banners.items():
			text = self.font.render(subtitle,True,C.BUTTON_COLOUR_NEUTRAL)
			pygame.draw.rect(
				self.pane,
				(75,75,75),
				banner
			)
			self.pane.blit(text , text.get_rect(center=banner.center))

		for button in self.buttons.values():
			button.render()

		for counter in self.counters.values():
			counter.render()
