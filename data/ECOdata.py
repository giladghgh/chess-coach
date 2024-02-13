import pygame
import openpyxl as pyxl

from data.Constants import C


class ECOdata:
	def __init__(self , coach , filepath):
		self.coach     = coach
		self.filepath  = filepath

		self.catalogue = None

		self.load()


	def load(self):
		wb = pyxl.load_workbook(self.filepath)

		data = {}
		for ws in wb:
			for row in range(1,10):
				pass

		#self.catalogue = data
		self.catalogue = C.OPENINGS


	def read(self , movetext):
		if movetext.count(". ") <= 5:
			self.coach.board.opening = self.catalogue.get(
				movetext.strip()
			) or self.coach.board.opening

		return self.coach.board.opening


	def render(self):
		self.coach.display.blit(
			self.coach.opening_font.render(
				self.read(self.coach.board.movetext),
				True,
				(255,255,255)
			),
			(C.TEXTBOX_X_OFFSET + 5 , 35)
		)
