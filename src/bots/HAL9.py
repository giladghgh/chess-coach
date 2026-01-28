import chess

from src.Gameplay import Move,Line

from src.Constants import C,E

from src.Bot import NativeBot





class BotHAL9(NativeBot):
	def __init__(self , engine):
		super().__init__(engine)

		self.code = "H9"

		self.config["PARAMS"] = {
			"Minimum Thinking Time" : 1000,
			"Depth"                 : 15,
		}


	def update(self):
		super().update()

		self.eval = min( max( self.score() , 0 ) , self.emax )


	def play(self):
		movetree = {}
		for move in self.model.legal_moves:
			self.model.push(move)

			move.score = self.score()
			branch = self.search(self.depth-1 , Line(move))
			movetree[move] = branch

			# print("\nmove:",move)
			# print(branch)

			self.model.pop()
			# break

		###########################################
		# for step,line in movescores.items():
		# 	print(step,end="")
		# 	for branch in line:
		# 		print("\t\t",branch)
		###########################################

		best , main = max( movetree.items() , key=lambda m:m[1].score )

		# print()
		# print("best:",type(best),best)
		# print("main:",type(main),main)

		# print("\nbest:",best,main)
		return self.engine.uci_to_move( best )


	def score(self):
		value = 0

		for colour in chess.COLORS:
			score = 0
			for piece in chess.PIECES:
				creed = chess.piece_symbol(piece).upper()

				for square in self.model.pieces(piece,colour):
					if colour == chess.WHITE:
						f = chess.square_file(square)
						r = 7 - chess.square_rank(square)
					else:
						f = 7 - chess.square_file(square)
						r = chess.square_rank(square)

					mat = E.SCOREBOARD_MATERIAL[creed]
					pos = E.SCOREBOARD_POSITION[creed][r][f] / 100

					score += mat + pos

			if self.model.is_check() and self.model.turn == colour:
				score += 15

			### gain perspective
			value += score * (1,-1)[colour == self.model.turn]

		return round(value,4)


	def search(self , depth , history):
		if not depth:
			return history

		lines = Line()
		for move in self.model.legal_moves:
			self.model.push(move)

			move.score = self.score()
			lines.append(
				self.search(
					depth-1,
					history + [move]
				)
			)

			self.model.pop()

		return lines


	@property
	def depth(self):
		return int((
			E.BOT_WHITE_DEPTH,
			E.BOT_BLACK_DEPTH,
		)[self.engine.coach.board.ply == "b"])
