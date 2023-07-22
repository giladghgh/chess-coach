import pygame
import os

from data.Constants import C



class Man:
	image_dir = 'D:\\Gilad\\Documents\\Projects\\Personal\\Chess Coach\\media\\Sets\\' + C.CHESS_SET + '\\'

	def __init__(self , position , colour , board):
		self.position = position
		self.f = position[0]
		self.r = position[1]
		self.colour = colour
		self.board = board
		self.has_moved = False


	def move(self , board , tile , forced=False):
		out = False
		for t in board.tiles:
			t.highlight = False

		if forced or (tile in self.valid_moves(board)):
			print(self.creed)
			print("origin: " + board.tile_of(self.position).pgn)
			print("target: " + tile.pgn)

			origin_tile = board.tile_of(self.position)
			self.position = tile.position
			self.f = tile.f
			self.r = tile.r

			origin_tile.occupant = None
			tile.occupant = self
			board.agent = None

			self.has_moved = True

			# Promoting (auto-queen)
			if self.creed == 'P':
				if self.r in (0,7):
					from data.men.Queen import Queen
					tile.occupant = Queen(
						tile.position,
						self.colour,
						self.board
					)

			# Castling
			if self.creed == 'K':
				if origin_tile.f - self.f == 2:
					partner = board.tile_of((0 , self.r)).occupant
					partner.move(board , board.tile_of((3 , self.r)) , forced=True)
				elif origin_tile.f - self.f == -2:
					partner = board.tile_of((7 , self.r)).occupant
					partner.move(board , board.tile_of((5 , self.r)) , forced=True)

			out = tile.pgn
			if self.creed != 'P':
				out = self.creed + out
		else:
			board.agent = None
			out = False

		return out


	def moves(self , board):
		out = []
		for direction in self.legal_moves(board):
			for tile in direction:
				if tile.occupant is not None:
					if tile.occupant.colour == self.colour:
						break
					else:
						out.append(tile)
						break
				else:
					out.append(tile)

		return out


	def prey(self , board):
		return self.moves(board)


	def valid_moves(self , board):
		out = []
		for tile in self.moves(board):
			if not board.is_in_check(self.colour , movement=[self.position,tile.position]):
				out.append(tile)

		return out