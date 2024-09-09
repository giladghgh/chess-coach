import pygame

from src.Elements import *





class Settings:
	def __init__(self , coach):
		self.coach = coach

		self.show = False
		self.font = pygame.font.SysFont("Consolas",14,bold=True)
		self.pane = pygame.Surface(C.PANE_SIZE,pygame.SRCALPHA)

		# Banners
		self.banners = {
			"UI"    : pygame.Rect(
				C.SIDEBAR_X_MARGIN,
				125,
				C.SIDEBAR_WIDTH - 3*C.SIDEBAR_X_MARGIN,
				C.TEXTBOX_HEIGHT
			),
			"BOTS"  : pygame.Rect(
				C.SIDEBAR_X_MARGIN,
				125 + 5*(C.BUTTON_HEIGHT + 3*C.GRID_GAP),
				C.SIDEBAR_WIDTH - 3*C.SIDEBAR_X_MARGIN,
				C.TEXTBOX_HEIGHT
			),
		}

		# Sliders
		self.sliders = {
			"SPEDOMETER"	: Slider(
				self,
				self.banners["UI"].left + C.BUTTON_WIDTH + C.GRID_GAP,
				self.banners["UI"].bottom + 3*(C.BUTTON_HEIGHT + 3*C.GRID_GAP) + 0.075*C.BUTTON_HEIGHT + C.GRID_GAP,
				(
					3*C.BUTTON_WIDTH,
					0.85*C.BUTTON_HEIGHT
				),
				metric="C.MOVE_SPEED",
				domain=(1,10),
				nparts=10
			),
		}

		# Buttons
		self.buttons = {
			### header
			"NEXT"			: ButtonNext(
				self.pane,
				C.SIDEBAR_WIDTH - 2*C.SIDEBAR_X_MARGIN - 0.8*C.BUTTON_WIDTH,
				C.SIDEBAR_Y_MARGIN + 0.1*C.BUTTON_HEIGHT,
				[0.8*L for L in C.BUTTON_SIZE],
				coach=self.coach
			),
			"PREV"			: ButtonPrevious(
				self.pane,
				C.SIDEBAR_WIDTH - 2*C.SIDEBAR_X_MARGIN - 1.6*C.BUTTON_WIDTH,
				C.SIDEBAR_Y_MARGIN + 0.1*C.BUTTON_HEIGHT,
				[0.8*L for L in C.BUTTON_SIZE],
				coach=self.coach
			),
			"SHOW_ANALYSIS"	: ButtonShowAnalysis(
				self.pane,
				C.SIDEBAR_X_MARGIN + C.BUTTON_WIDTH + C.GRID_GAP,
				C.SIDEBAR_Y_MARGIN,
				coach=self.coach
			),
			"SHUT"			: ButtonShut(
				self.pane,
				C.SIDEBAR_X_MARGIN + 0.075*C.BUTTON_WIDTH,
				C.SIDEBAR_Y_MARGIN + 0.075*C.BUTTON_HEIGHT,
				[0.85*L for L in C.BUTTON_SIZE],
				coach=self.coach
			),
			### UI
			"B_STYLIST"		: ButtonBoardStylist(
				self.pane,
				self.banners["UI"].left + C.BUTTON_WIDTH + 5*C.GRID_GAP,
				self.banners["UI"].bottom + C.GRID_GAP,
				board=self.coach.board
			),
			"ECOI"			: ButtonECOI(
				self.pane,
				self.banners["UI"].left,
				self.banners["UI"].bottom + C.GRID_GAP,
				C.BUTTON_SIZE,
				True,
				reader=self.coach.reader
			),
			"P_STYLIST"		: ButtonPieceStylist(
				self.pane,
				self.banners["UI"].left + C.BUTTON_WIDTH + 5*C.GRID_GAP,
				self.banners["UI"].bottom + C.BUTTON_HEIGHT + 4*C.GRID_GAP,
				board=self.coach.board
			),
			"LEGAL_MOVES"	: ButtonLegalMoves(
				self.pane,
				self.banners["UI"].left,
				self.banners["UI"].bottom + C.BUTTON_HEIGHT + 4*C.GRID_GAP,
				C.BUTTON_SIZE,
				True,
				board=self.coach.board
			),
			"FLIP"			: ButtonFlip(
				self.pane,
				self.banners["UI"].left + C.BUTTON_WIDTH + 5*C.GRID_GAP,
				self.banners["UI"].bottom + 2*(C.BUTTON_HEIGHT + 3*C.GRID_GAP) + C.GRID_GAP,
				board=self.coach.board
			),
			"COORDS"		: ButtonCoords(
				self.pane,
				self.banners["UI"].left,
				self.banners["UI"].bottom + 2*(C.BUTTON_HEIGHT + 3*C.GRID_GAP) + C.GRID_GAP,
				board=self.coach.board
			),
			"SPEDOMETER"	: ButtonSpedometer(
				self.pane,
				self.banners["UI"].left,
				self.banners["UI"].bottom + 3*(C.BUTTON_HEIGHT + 3*C.GRID_GAP) + C.GRID_GAP,
				slider=self.sliders["SPEDOMETER"]
			),
			### bots
			"BOT_BLACK"		: ButtonBot(
				self.pane,
				self.banners["BOTS"].left + C.BUTTON_WIDTH + 5*C.GRID_GAP,
				self.banners["BOTS"].bottom + C.GRID_GAP,
				engine=self.coach.engine,
				player="BLACK"
			),
			"BOT_WHITE"		: ButtonBot(
				self.pane,
				self.banners["BOTS"].left,
				self.banners["BOTS"].bottom + C.GRID_GAP,
				engine=self.coach.engine,
				player="WHITE"
			),
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

		for slider in self.sliders.values():
			slider.render()
