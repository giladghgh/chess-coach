import pygame

from src.Constants import C





class Tile:
	def __init__(self , display , f , r , w , h , preoccupant=None):
		self.display = display
		self.f = f
		self.r = r
		self.w = w
		self.h = h
		self.occupant = preoccupant

		self.position = (self.f , self.r)
		self.pgn 	  = C.FILES[self.f] + str(self.r)

		self.font = pygame.font.SysFont("Consolas",12)

		# Brightness            "bottom right is light"
		if (self.f + self.r) % 2 == 1:
			self.rgb_basic = C.BOARD_DESIGN[0]
			self.rgb_fresh = C.BOARD_DESIGN[1]
			self.rgb_focus = C.TILE_FOCUS_LIGHT
		else:
			self.rgb_basic = C.BOARD_DESIGN[2]
			self.rgb_fresh = C.BOARD_DESIGN[3]
			self.rgb_focus = C.TILE_FOCUS_DARK

		# Decor
		self.veil     = pygame.Surface(C.TILE_SIZE,pygame.SRCALPHA)
		self.is_fresh = False
		self.is_legal = False
		self.is_focus = False

		self.prose = self.font.render(
			self.pgn,
			True,
			(235,235,235) if (self.f + self.r) % 2 == 1 else (150,150,150)
		)
		self.prose.set_alpha(150)


	def __str__(self):
		return self.pgn + ((self.occupant.colour + self.occupant.creed) if self.occupant else "")


	def __eq__(self , other):
		return (self.f,self.r) == (other.f,other.r)


	def render(self):
		pygame.draw.rect(
			self.display,
			self.rgb_basic,
			self.rect
		)

		# Fresh / Legal / Focus decor
		if self.is_focus or self.is_fresh or self.is_legal:
			self.veil.fill((0,0,0,0))

			if self.is_fresh:
				self.veil.fill((*self.rgb_fresh,180))
				self.display.blit(self.veil,self.rect)
			elif self.is_focus:
				self.veil.fill((*self.rgb_focus,130))
				self.display.blit(self.veil,self.rect)

			if self.is_legal:
				pygame.draw.circle(
					self.veil,
					(50,50,50,75),
					[l/2 for l in C.TILE_SIZE],
					40 if self.occupant else 10
				)
				self.display.blit(self.veil,self.rect)          # blit twice so doubled decor doesn't look shit

		# Occupant ...
		if self.occupant:
			self.display.blit(
				self.occupant.image,
				self.occupant.image.get_rect(center=self.rect.center)
			)

		# ... or co-ordinate
		elif C.SHOW_TILE_COORD:
			self.display.blit(
				self.prose,
				self.prose.get_rect(center=self.rect.center).move(0,1)
			)


	@property
	def rect(self):
		return pygame.Rect(
			C.PANE_WIDTH + self.x,
			C.WINDOW_HEIGHT - C.TILE_HEIGHT - self.y,
			self.w,
			self.h
		)

	@property
	def x(self):
		return self.w * (
			(8-self.f) if C.BOARD_FLIPPED else (self.f-1)
		)

	@property
	def y(self):
		return self.h * (
			(8-self.r) if C.BOARD_FLIPPED else (self.r-1)
		)

	@property
	def id(self):
		return self.pgn + (self.occupant.colour + self.occupant.creed if self.occupant else "")