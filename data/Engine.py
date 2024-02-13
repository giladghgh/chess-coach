from data.Constants import C

import random



class Engine:
	def __init__(self, coach):
		self.coach = coach

		self.board = self.coach.board
		self.coach.engine = self

		self.player_scheme = C.INIT_PLAYER_SCHEME
		self.eval = {
			"":10,
			"N":30,
			"B":30,
			"R":30,
			"Q":90,
			"K":1000
		}


	def play(self):
		catalogue = []
		for man in self.board.all_men(self.board.ply):
			moves = man.legal_moves(self.board)
			if moves:
				catalogue.append((man,moves))

		if not catalogue: return None

		scheme = self.player_scheme[self.board.ply == "b"]
		play = {
			"Random" : self.choose_random(catalogue),
			"Materialistic" : self.choose_materialistic(catalogue)
		}[scheme]

		self.coach.force_move(origin=play[0].position , target=play[1].position , special=play[2])


	def choose_random(self , catalogue):
		line = random.choice(catalogue)

		man  = line[0]
		move = random.choice(line[1])

		# Auto-queen:
		special = None
		if not man.creed and (
			man.colour == "w" and move.r == 8
		) or (
			man.colour == "b" and move.r == 1
		):
			special = "Q"

		return man,move,special


	def choose_materialistic(self , catalogue):
		return catalogue[0][0],catalogue[0][1][0],None
