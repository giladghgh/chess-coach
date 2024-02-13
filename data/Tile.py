import pygame

from data.Constants import C



class Tile:
	def __init__(self , board , f , r , w , h , preoccupant=None):
		self.board = board
		self.f     = f
		self.r     = r
		self.w     = w
		self.h     = h

		self.x = self.w * (self.f-1)
		self.y = self.h * (self.r-1)
		self.position = (self.f , self.r)
		self.pgn = C.FILES[self.f] + str(self.r)

		self.occupant = preoccupant

		# TILE COLOURING
		self.highlight = False
		if (self.f + self.r) % 2 == 1:
			self.rgb_reg = C.TILE_LIGHT
			self.rgb_high = C.TILE_LIGHT_HIGH
		else:
			self.rgb_reg = C.TILE_DARK
			self.rgb_high = C.TILE_DARK_HIGH

	def render(self):
		tile_colour = self.rgb_high if self.highlight else self.rgb_reg
		pygame.draw.rect(
			self.board.display,
			tile_colour,
			self.rect
		)

		if self.occupant:
			occupant_rect = self.occupant.image.get_rect()
			occupant_rect.center = self.rect.center
			self.board.display.blit(self.occupant.image , occupant_rect)


	@property
	def rect(self):
		return pygame.Rect(
			self.x + C.SIDEBAR_WIDTH,
			C.BOARD_HEIGHT - C.TILE_HEIGHT - self.y,
			self.w,
			self.h
		)

	# @property
	# def pgn(self):
	# 	return C.FILES[self.f] + str(self.r)