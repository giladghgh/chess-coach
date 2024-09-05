import pygame

from src.Constants import C





class Tile:
	def __init__(self , board , f , r , w , h , preoccupant=None):
		self.board = board
		self.f = f
		self.r = r
		self.w = w
		self.h = h
		self.occupant = preoccupant

		self.position = (self.f , self.r)
		self.pgn 	  = C.FILES[self.f] + str(self.r)

		self.font = pygame.font.SysFont("Consolas",12)

		# Decor
		self.is_fresh = False
		self.is_focus = False
		self.is_legal = False

		### "bottom right is light for white"
		if (self.f + self.r) % 2 == 1:
			self.rgb_basic = C.BOARD_STYLE[0]
			self.rgb_fresh = C.BOARD_STYLE[1]
			self.rgb_focus = C.TILE_FOCUS_LIGHT
			# self.image_path = C.DIR_MEDIA + "\\tile_light.png"
		else:
			self.rgb_basic = C.BOARD_STYLE[2]
			self.rgb_fresh = C.BOARD_STYLE[3]
			self.rgb_focus = C.TILE_FOCUS_DARK
			# self.image_path = C.DIR_MEDIA + "\\tile_dark.png"

		# self.image = pygame.transform.scale(
		# 	pygame.image.load(self.image_path),
		# 	(self.w,self.h)
		# )


	def __str__(self):
		return self.pgn + (self.occupant.colour + self.occupant.creed if self.occupant else "")


	def render(self):
		# if self.image:
		# 	self.board.coach.display.blit(
		# 		self.image,
		# 		self.image.get_rect(center=self.rect.center)
		# 	)
		# else:
		pygame.draw.rect(
			self.board.coach.display,
			self.rgb_basic,
			self.rect
		)


		# Fresh / Focus / Legal decor
		if any([
			self.is_fresh,
			self.is_focus,
			self.is_legal,
		]):
			veil = pygame.Surface(C.TILE_SIZE,pygame.SRCALPHA)

			if self.is_focus:
				veil.fill((*self.rgb_focus,130))
			elif self.is_fresh:
				veil.fill((*self.rgb_fresh,180))
			self.board.coach.display.blit(veil,self.rect)		# blit twice so doubled decor doesn't look like shit

			if self.is_legal:
				pygame.draw.circle(
					veil,
					(50,50,50,75),
					veil.get_rect().center,
					40 if self.occupant else 10
				)
			self.board.coach.display.blit(veil,self.rect)

		# Occupant / PGN coordinate
		if self.occupant:
			self.board.coach.display.blit(
				self.occupant.image,
				self.occupant.image.get_rect(center=self.rect.center)
			)
		elif self.board.show_coords:
			text = self.font.render(self.pgn,True,(235,235,235) if (self.f + self.r) % 2 == 1 else (150,150,150))
			text.set_alpha(150)
			self.board.coach.display.blit(
				text,
				text.get_rect(center=self.rect.center).move(0,1)
			)


	@property
	def rect(self):
		return pygame.Rect(
			C.SIDEBAR_WIDTH + self.x,
			C.BOARD_HEIGHT - C.TILE_HEIGHT - self.y,
			self.w,
			self.h
		)


	@property
	def x(self):
		return self.w * (
			(8-self.f) if self.board.coach.flipped else (self.f-1)
		)


	@property
	def y(self):
		return self.h * (
			(8-self.r) if self.board.coach.flipped else (self.r-1)
		)


	@property
	def id(self):
		return self.pgn + (self.occupant.colour + self.occupant.creed if self.occupant else "")