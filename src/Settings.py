from src.Elements import *





class Settings:
	def __init__(self , coach):
		self.coach = coach

		self.show = False
		self.font = pygame.font.SysFont("Consolas",14,bold=True)
		self.pane = pygame.Surface((C.SIDEBAR_WIDTH,C.BOARD_HEIGHT))

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
				415,
				C.SIDEBAR_WIDTH - 3*C.SIDEBAR_X_MARGIN,
				C.TEXTBOX_HEIGHT
			),
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
			### UI
			"B_STYLIST"			: ButtonBoardStylist(
				self.coach,
				"BSTYLE_",
				C.SIDEBAR_X_MARGIN + 100,
				self.banners["UI"].bottom + C.GRID_GAP,
				self
			),
			"FLIP"				: ButtonFlip(
				self.coach,
				"FLIP",
				C.SIDEBAR_X_MARGIN,
				self.banners["UI"].bottom + C.GRID_GAP,
				self
			),
			"P_STYLIST"			: ButtonPieceStylist(
				self.coach,
				"PSTYLE_",
				C.SIDEBAR_X_MARGIN + 100,
				self.banners["UI"].y + 100,
				self
			),
			"COORDS"			: ButtonCoords(
				self.coach,
				"COORDS",
				C.SIDEBAR_X_MARGIN,
				self.banners["UI"].y + 100,
				self
			),
			"LEGAL_MOVES"		: ButtonLegalMoves(
				self.coach,
				"LEGAL_MOVES",
				C.SIDEBAR_X_MARGIN,
				self.banners["UI"].y + 175,
				self,
				C.BUTTON_SIZE,
				True
			),
			"ECO_INTERPRETER"	: ButtonECOI(
				self.coach,
				"ECOI",
				C.SIDEBAR_X_MARGIN + 100,
				self.banners["UI"].y + 175,
				self,
				C.BUTTON_SIZE,
				True
			),
			### bots
			"BOT_BLACK"			: ButtonBot(
				self.coach,
				"BOT_BLACK_",
				C.SIDEBAR_X_MARGIN + 100,
				self.banners["BOTS"].y + 25,
				self,
				player="BLACK"
			),
			"BOT_WHITE"			: ButtonBot(
				self.coach,
				"BOT_WHITE_",
				C.SIDEBAR_X_MARGIN,
				self.banners["BOTS"].y + 25,
				self,
				player="WHITE"
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
