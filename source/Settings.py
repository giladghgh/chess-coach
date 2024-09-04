from source.Elements import *





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
		self.btn_shut = ButtonShut(
			self.coach,
			"SHUT_SETTINGS",
			C.SIDEBAR_X_MARGIN + 0.05*C.BUTTON_WIDTH,
			C.SIDEBAR_Y_MARGIN + 0.05*C.BUTTON_HEIGHT,
			self,
			[0.9*L for L in C.BUTTON_SIZE]
		)
		self.btn_show_analysis = ButtonShowAnalysis(
			self.coach,
			"SHOW_ANALYSIS",
			C.SIDEBAR_X_MARGIN + C.BUTTON_WIDTH + C.GRID_GAP,
			C.SIDEBAR_Y_MARGIN,
			self
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
		self.btn_flip = ButtonFlip(
			self.coach,
			"FLIP",
			C.SIDEBAR_X_MARGIN,
			self.banners["UI"].y + 25,
			self
		)
		self.btn_coords = ButtonCoords(
			self.coach,
			"COORDS",
			C.SIDEBAR_X_MARGIN,
			self.banners["UI"].y + 100,
			self
		)
		self.btn_legals = ButtonLegalMoves(
			self.coach,
			"LEGAL_MOVES",
			C.SIDEBAR_X_MARGIN,
			self.banners["UI"].y + 175,
			self,
			C.BUTTON_SIZE,
			True
		)
		self.btn_bstyle = ButtonBoardStylist(
			self.coach,
			"BSTYLE_",
			C.SIDEBAR_X_MARGIN + 100,
			self.banners["UI"].y + 25,
			self
		)
		self.btn_pstyle = ButtonPieceStylist(
			self.coach,
			"PSTYLE_",
			C.SIDEBAR_X_MARGIN + 100,
			self.banners["UI"].y + 100,
			self
		)
		self.btn_eco = ButtonECO(
			self.coach,
			"ECO",
			C.SIDEBAR_X_MARGIN + 100,
			self.banners["UI"].y + 175,
			self
		)
		self.btn_bot_black = ButtonBot(
			self.coach,
			"BOT_BLACK_",
			C.SIDEBAR_X_MARGIN + 100,
			self.banners["BOTS"].y + 25,
			self,
			player="BLACK"
		)
		self.btn_bot_white = ButtonBot(
			self.coach,
			"BOT_WHITE_",
			C.SIDEBAR_X_MARGIN,
			self.banners["BOTS"].y + 25,
			self,
			player="WHITE"
		)
		self.buttons = [
			self.btn_shut,
			self.btn_show_analysis,
			self.btn_prev,
			self.btn_next,
			self.btn_flip,
			self.btn_coords,
			self.btn_legals,
			self.btn_bstyle,
			self.btn_pstyle,
			self.btn_eco,
			self.btn_bot_black,
			self.btn_bot_white,
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
