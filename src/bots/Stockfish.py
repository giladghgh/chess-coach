from stockfish import Stockfish

from src.Elements import Arrow

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

		if self.code not in E.BOT_EXCLUDE_ALL:
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

		if self is E.BOT_GAUGE:             ### must run AFTER .get_evaluation() because it changes the eval
			self.update_topls()


	def update_topls(self):
		for rank,line in enumerate(self.model.get_top_moves(3)):
			move = self.engine.txt_to_move(line.pop("Move"))

			score = "M"+str(line["Mate"]) if line["Mate"] else line["Centipawn"]/100

			arrow = Arrow(
				self.engine.coach,
				move.origin,
				move.target,
				C.ARROW_TOPLS_COLOUR[rank]
			)

			self.engine.topls[rank] = (score , move.text , arrow)


	def calculate(self):
		return self.engine.txt_to_move( self.model.get_best_move() )
