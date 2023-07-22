import pygame

from data.Man import Man



class Queen(Man):
	def __init__(self , position , colour , board):
		super().__init__(position , colour , board)
		self.creed = 'Q'
		self.id = self.colour + self.creed

		self.image_path = Man.image_dir + colour + '_queen.png'
		self.image = pygame.image.load(self.image_path)
		self.image = pygame.transform.scale(self.image , (board.tile_width-20 , board.tile_height-20))


	def _legal_moves(self, board):
		from data.men.Bishop import Bishop
		from data.men.Rook import Rook
		out = []

		moves_b = Bishop.legal_moves(board)
		out.append(moves_b)

		moves_r = Rook.legal_moves(board)
		out.append(moves_r)

		return out


	def legal_moves(self , board):
		out = []

		moves_n = []
		for i in range(self.r)[::-1]:
			moves_n.append(board.tile_of(
				(self.f , i)
			))
		out.append(moves_n)
		
		moves_ne = []
		for i in range(1,8):
			if (self.f+i > 7) or (self.r-i < 0):
				break
			moves_ne.append(board.tile_of(
				(self.f+i , self.r-i)
			))
		out.append(moves_ne)
		
		moves_e = []
		for i in range(self.f+1 , 8):
			moves_e.append(board.tile_of(
				(i , self.r)
			))
		out.append(moves_e)
		
		moves_se = []
		for i in range(1,8):
			if (self.f+i > 7) or (self.r+i > 7):
				break
			moves_se.append(board.tile_of(
				(self.f+i , self.r+i)
			))
		out.append(moves_se)
		
		moves_s = []
		for i in range(self.r+1 , 8):
			moves_s.append(board.tile_of(
				(self.f , i)
			))
		out.append(moves_s)
		
		moves_sw = []
		for i in range(1,8):
			if (self.f-i < 0) or (self.r+i > 7):
				break
			moves_sw.append(board.tile_of(
				(self.f-i , self.r+i)
			))
		out.append(moves_sw)
		
		moves_w = []
		for i in range(self.f)[::-1]:
			moves_w.append(board.tile_of(
				(i , self.r)
			))
		out.append(moves_w)

		moves_w = []
		for i in range(self.f)[::-1]:
			moves_w.append(board.tile_of(
				(i , self.r)
			))
		out.append(moves_w)

		moves_nw = []
		for i in range(1, 8):
			if (self.f-i < 0) or (self.r-i < 0):
				break
			moves_nw.append(board.tile_of(
				(self.f-i , self.r-i)
			))
		out.append(moves_nw)

		return out