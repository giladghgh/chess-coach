from stockfish import Stockfish

from src.Constants import C,E

from src.Bot import ExoticBot





class BotStockfish(ExoticBot):
	def __init__(self , engine):
		super().__init__(engine)

		self.code = "SF"

		self.config["PATH"]   = "data" + C.SEP + "stockfish" + C.SEP + "stockfish-windows-x86-64-avx2.exe"
		self.config["PARAMS"] = {
			"Minimum Thinking Time" : 0,
			"Min Split Depth"       : 10,
		}

		if self.code not in E.BOT_EXCLUDE:
			self.model = Stockfish(
				path=self.config["PATH"],
				depth=15,
				parameters=self.config["PARAMS"]
			)


	def update(self):
		self.model.set_fen_position(self.engine.fen)

		match (score := self.model.get_evaluation())["type"]:
			case "cp":
				self.eval = score["value"]/100
			case "mate":
				self.eval = self.emax if score["value"]>0 else -self.emax


	def play(self):
		best = self.model.get_best_move()

		return self.engine.txt_to_move(best)
