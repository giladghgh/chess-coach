import pygame
import time

from data.Constants import C



class Tile:
	def __init__(self , f , r , w , h):
		self.f = f
		self.r = r
		self.w = w
		self.h = h

		self.x = w * f
		self.y = h * r
		self.position = (f,r)
		self.a_position = (self.x,self.y)

		self.occupant = None
		self.pgn = C.FILES[f] + str(8-r)

		self.highlight = False
		if (f + r) % 2 == 0:
			self.rgb_reg = C.TILE_LIGHT
			self.rgb_high = C.TILE_LIGHT_HIGH
		else:
			self.rgb_reg = C.TILE_DARK
			self.rgb_high = C.TILE_DARK_HIGH

		self.rect = pygame.Rect(
			self.x,
			self.y,
			self.w,
			self.h
		)

	def draw(self , display):
		tile_colour = self.rgb_high if self.highlight else self.rgb_reg
		pygame.draw.rect(display, tile_colour, self.rect)

		if self.occupant is not None:
			centere_rect = self.occupant.image.get_rect()
			centere_rect.center = self.rect.center
			display.blit(self.occupant.image , centere_rect.topleft)
