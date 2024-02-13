import pygame
import os

from data.Coach import Coach
from data.Constants import C


if __name__ == "__main__":
	os.environ["SDL_VIDEO_WINDOW_POS"] = "1000,200"
	pygame.init()
	pygame.display.set_caption("Chess Coach")

	coach  = Coach()
	board  = coach.board
	engine = coach.engine

	running = True
	done    = False
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
				if any([
					coach.settings.showing,
					#coach.analysis.showing,
				]):
					coach.settings.showing = False
					#coach.analysis.showing = False
				else:
					running = False
			else:
				if engine.player_scheme[board.ply == "b"]:
					engine.play()
				else:
					coach.handle_click(event)

		if not done and board.is_game_over():
			done = True
			coach.board_export()
			if board.finish[0] == "Draw":
				print("The game is a draw by " + board.finish[1].lower() + "!")
			elif board.finish[1] == "Checkmate":
				print(board.finish[0] + " wins!")

		coach.display.fill(C.BG_COLOUR)
		coach.render()
		board.render()
		pygame.display.update()