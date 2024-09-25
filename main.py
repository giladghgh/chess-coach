import os,time
import pygame

from src.Coach import Coach
from src.Constants import C





if __name__ == "__main__":
	pygame.init()
	pygame.display.set_caption("Chess Coach")
	pygame.display.set_icon(pygame.image.load(C.DIR_MEDIA + "coach_icon.png"))

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

	cache   = None
	running = True
	done    = False
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

			elif event.type == pygame.KEYDOWN:
				match event.key:
					case pygame.K_ESCAPE:
						for context in coach.contexts:
							if context.show:
								context.show = False
								break
						else:
							running = False
					case pygame.K_t:
						coach.toggle_tray.click()
					case pygame.K_LEFT:
						if coach.toggle_tray.active:            ### can't hide if it's hidden already
							coach.toggle_tray.active = True
							coach.toggle_tray.click()
					case pygame.K_RIGHT:
						if not coach.toggle_tray.active:
							coach.toggle_tray.active = False
							coach.toggle_tray.click()

			elif event.type == pygame.USEREVENT:
				coach.clock.tick()

			elif event.type in (
				pygame.KEYDOWN,
				pygame.KEYUP,
				pygame.MOUSEMOTION,
				pygame.MOUSEBUTTONUP,
				pygame.MOUSEBUTTONDOWN,
			):
				coach.handle_click(event)

		if not done:

			# TODO: KING BURIALS
			#   - DRAW, SAME FILE
			#   - WHITE, BOTH ON LIGHT TILES
			#   - BLACK, BOTH ON DARK TILES
			if coach.is_game_over():
				done = True

				if board.outcome[0] == "Draw":
					print("The game is a draw by " + board.outcome[1].lower() + "!")
				elif board.outcome[1] == "Checkmate":
					print(board.outcome[0] + " wins by checkmate!")

			elif engine.scheme[board.ply == "b"] and len(board.movelog) == board.halfmovenum:
				engine.play()

		coach.screen.fill(C.BACKGR_PANE)
		board.render()
		coach.render()
		pygame.display.update()
