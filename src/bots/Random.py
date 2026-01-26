import chess,random

from src.Bot import NativeBot





class BotRandom(NativeBot):
	def __init__(self , engine):
		super().__init__(engine)

		self.code = "RM"


	def play(self):
		best = random.choice( list(self.model.legal_moves) )

		return self.engine.uci_to_move(best)
