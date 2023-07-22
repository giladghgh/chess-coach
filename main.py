import pygame

from data.Board import Board



WINDOW_SIZE = (600,600)
pygame.init()

screen = pygame.display.set_mode(WINDOW_SIZE)
board = Board(WINDOW_SIZE[0] , WINDOW_SIZE[1])



if __name__ == '__main__':
	running = True
	while running:
		m_x, m_y = pygame.mouse.get_pos()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					board.handle_click(m_x, m_y)
		if board.is_in_checkmate('b'):
			board.export()
			print('White wins!')
			running = False
		elif board.is_in_checkmate('w'):
			board.export()
			print('Black wins!')
			running = False

		screen.fill('white')
		board.draw(screen)
		pygame.display.update()
