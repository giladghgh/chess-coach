import os
import pygame

from src.Coach import Coach
from src.Constants import C





if __name__ == "__main__":
	pygame.init()

	# C.MONITOR_SIZE = (
	# 	pygame.display.Info().current_w,
	# 	pygame.display.Info().current_h
	# )
	# C.WINDOW_POS = (
	# 	(19/20)*C.MONITOR_SIZE[0] - (C.SIDEBAR_WIDTH + C.BOARD_WIDTH),
	# 	C.MONITOR_SIZE[1]/10
	# )
	os.environ["SDL_VIDEO_WINDOW_POS"] = "%d,%d" % C.WINDOW_POS

	coach  = Coach()
	board  = coach.board
	engine = coach.engine

	running = True
	done    = False
	while running:
		if engine.player_scheme[board.ply == "b"]:
			engine.play()
		else:
			for event in pygame.event.get():
				if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
					running = False
				else:
					coach.handle_click(event)

		if not done and coach.is_game_over():
			done = True

			if board.outcome[0] == "Draw":
				print("The game is a draw by " + board.outcome[1].lower() + "!")
			elif board.outcome[1] == "Checkmate":
				print(board.outcome[0] + " wins by checkmate!")

		coach.display.fill(C.BACKGR_COLOUR)
		board.render()
		coach.render()
		pygame.display.update()
