import time
# import openpyxl as pyxl

from source.Constants import C





class ECO:
	def __init__(self , coach , filepath=C.DIR+"\\ECO Catalogue.xlsm"):
		self.coach    = coach
		self.filepath = filepath

		self.catalogue = None

		self.load()


	def load(self):
		# wb = pyxl.load_workbook(self.filepath)

		# source = {}
		print("loading...")
		print("ECO loaded!")

		#self.catalogue = source
		self.catalogue = C.OPENINGS


	# TODO: ADAPT TO WORK WITH MOVELOG RATHER THAN MOVETEXT
	def interpret(self , movetext):
		if movetext.count(". ") <= 5:
			self.coach.board.opening = self.catalogue.get(
				movetext.strip()
			) or self.coach.board.opening

		return self.coach.board.opening


	def render(self):
		self.coach.display.blit(
			self.coach.opening_font.render(
				self.interpret(self.coach.board.movetext),
				True,
				(255,255,255)
			),
			(C.SIDEBAR_X_MARGIN + 5 , 35)
		)
