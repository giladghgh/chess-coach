import os.path
import pygame
import time

from src.Gameplay import Board
from src.Constants import C

path = 'D:\\Gilad\\Documents\\Projects\\Personal\\Chess Coach\\media\\sets\\Classic\\'
myimg = pygame.image.load(path + 'b_pawn.png')
myimg = pygame.transform.scale(myimg,(75,75))
myrec = myimg.get_rect()

color = (255,0,0)
run = True

pygame.init()
screen = pygame.display.set_mode((600,600))

while run:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

	screen.fill('white')
	screen.blit(myimg,myrec)
	pygame.display.update()

pygame.quit()