class Bot:
	def __init__(self , engine):
		self.engine = engine

		self.code = None
		self.eval = None
		self.emax = 15

		self.config = {
			"PATH"   : None,
			"PARAMS" : None,
		}

		self.users = 0

	def __repr__(self):
		return type(self).__name__[3:]

	def __eq__(self , this):
		return False if this is None else self.code == (this if type(this) is str else this.code)

	def load(self):
		self.users += 1

	def drop(self):
		self.users -= 1

	def play(self):
		pass



class NativeBot(Bot):
	""" Native bots use Engine's model """

	def __init__(self , engine):
		super().__init__(engine)

		self.model = self.engine.model

	def update(self):
		self.model.set_fen(self.engine.fen)



class ExoticBot(Bot):
	""" Exotic bots use a foreign chess engine """

	def __init__(self , engine):
		super().__init__(engine)

		self.model = None

	def update(self):
		pass