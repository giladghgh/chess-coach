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
		self.btn_show_analysis = ButtonShowSettings(
			self.coach,
			"SHOW_SETTINGS",
			C.SIDEBAR_X_MARGIN,
			C.SIDEBAR_Y_MARGIN,
			self
		)
		self.btn_shut = ButtonShut(
			self.coach,
			"SHUT_ANALYSIS",
			C.SIDEBAR_X_MARGIN + C.BUTTON_WIDTH + C.GRID_GAP + 0.05*C.BUTTON_WIDTH,
			C.SIDEBAR_Y_MARGIN + 0.05*C.BUTTON_HEIGHT,
			self,
			[0.9*L for L in C.BUTTON_SIZE]
		)
		self.btn_prev = ButtonPrevious(
			self.coach,
			"PREVIOUS",
			C.SIDEBAR_WIDTH - 2*C.SIDEBAR_X_MARGIN - 1.6*C.BUTTON_WIDTH,
			C.SIDEBAR_Y_MARGIN + 0.1*C.BUTTON_HEIGHT,
			self,
			[0.8*L for L in C.BUTTON_SIZE]
		)
		self.btn_next = ButtonNext(
			self.coach,
			"NEXT",
			C.SIDEBAR_WIDTH - 2*C.SIDEBAR_X_MARGIN - 0.8*C.BUTTON_WIDTH,
			C.SIDEBAR_Y_MARGIN + 0.1*C.BUTTON_HEIGHT,
			self,
			[0.8*L for L in C.BUTTON_SIZE]
		)
		self.buttons = [
			self.btn_shut,
			self.btn_show_analysis,
			self.btn_prev,
			self.btn_next,
		]

		# Counters
		self.ctr_fifty_move = Counter(
			self.coach,
			"Fifty Move Rule",
			0,
			self.font,
			C.SIDEBAR_X_MARGIN,
			self.banners["COUNTERS"].y + 25,
			self.pane
		)
		self.ctr_three_reps = Counter(
			self.coach,
			"Threefold Repetition Rule",
			1,
			self.font,
			C.SIDEBAR_X_MARGIN,
			self.banners["COUNTERS"].y + 55,
			self.pane
		)
		self.counters = [
			self.ctr_fifty_move,
			self.ctr_three_reps,
		]


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

		for button in self.buttons:
			button.render()

		for counter in self.counters:
			counter.render()
