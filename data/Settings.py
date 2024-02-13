import pygame

from data.Constants import C
from data.Elements import Button,Dropdown



class Settings:
	def __init__(self , coach):
		self.coach = coach

		self.display = self.coach.display
		self.coach.settings = self

		self.settings_veil = pygame.Surface((C.SIDEBAR_WIDTH,C.BOARD_HEIGHT))
		self.settings_veil.fill([125]*3)
		self.showing = False

		self.btn_settings_show = Button(
			self.coach,
			"SETTINGS_SHOW",
			C.TEXTBOX_X_OFFSET,
			265
		)
		self.btn_settings_hide = Button(
			self.coach,
			"SETTINGS_HIDE",
			C.TEXTBOX_X_OFFSET,
			30,
			context="settings",
			size=(0.8*C.BUTTON_WIDTH , 0.8*C.BUTTON_HEIGHT),
			colour=(100,75,75)
		)
		self.btn_flip_board = Button(
			self.coach,
			"FLIP",
			C.TEXTBOX_X_OFFSET,
			150,
			context="settings"
		)
		self.btn_eco = Button(
			self.coach,
			"ECO",
			C.TEXTBOX_X_OFFSET,
			300,
			context="settings"
		)

		self.btn_bot_white = Button(
			self.coach,
			"BOT_WHITE_",
			2*C.TEXTBOX_X_OFFSET + C.BUTTON_WIDTH,
			150,
			context="settings"
		)
		self.ddn_bot_white = Dropdown(
			self.coach,
			self.btn_bot_white,
			[
				Button(
					self.coach,
					"BOT_WHITE_RANDOM",
					self.btn_bot_white.x - C.BUTTON_WIDTH/2,
					self.btn_bot_white.y - C.BUTTON_HEIGHT - 5,
					context="settings"
				),
				Button(
					self.coach,
					"BOT_WHITE_MATERIALISTIC",
					self.btn_bot_white.x + C.BUTTON_WIDTH/2,
					self.btn_bot_white.y - C.BUTTON_HEIGHT - 5,
					context="settings"
				)
			]
		)

		self.btn_bot_black = Button(
			self.coach,
			"BOT_BLACK_",
			3*C.TEXTBOX_X_OFFSET + 2*C.BUTTON_WIDTH,
			150,
			context="settings"
		)
		self.ddn_bot_black = Dropdown(
			self.coach,
			self.btn_bot_black,
			[
				Button(
					self.coach,
					"BOT_BLACK_RANDOM",
					self.btn_bot_black.x - C.BUTTON_WIDTH/2,
					self.btn_bot_black.y - C.BUTTON_HEIGHT - 5,
					context="settings"
				),
				Button(
					self.coach,
					"BOT_BLACK_MATERIALISTIC",
					self.btn_bot_black.x + C.BUTTON_WIDTH/2,
					self.btn_bot_black.y - C.BUTTON_HEIGHT - 5,
					context="settings"
				)
			]
		)

		self.btn_style = Button(
			self.coach,
			"STYLE_",
			C.TEXTBOX_X_OFFSET,
			225,
			context="settings"
		)
		self.ddn_style = Dropdown(
			self.coach,
			self.btn_style,
			[
				# PREPEND new styles so mouseover tooltip stays visible
				Button(
					self.coach,
					"STYLE_3D",
					self.btn_style.x + C.BUTTON_WIDTH + 55,
					self.btn_style.y,
					context="settings"
				),
				Button(
					self.coach,
					"STYLE_CLASSIC",
					self.btn_style.x + C.BUTTON_WIDTH + 5,
					self.btn_style.y + 50,
					context="settings"
				),
				Button(
					self.coach,
					"STYLE_TUTORIAL",
					self.btn_style.x + C.BUTTON_WIDTH + 5,
					self.btn_style.y,
					context="settings"
				)
			]
		)

		self.elements = [
			self.btn_settings_hide,
			self.btn_flip_board,
			self.btn_eco,
			self.btn_style,
			self.btn_bot_white,
			self.btn_bot_black,
			self.ddn_style,
			self.ddn_bot_white,
			self.ddn_bot_black,
		]


	def render(self):
		self.display.blit(self.settings_veil , (0,0))

		# Buttons
		for elem in self.elements:
			elem.render(self.display)
