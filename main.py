import os,time
import pygame

from src.Constants import C
from src.Coach import Coach





if __name__ == "__main__":
	pygame.init()
	pygame.display.set_caption("Chess Coach")
	pygame.display.set_icon(pygame.image.load(C.DIR_MEDIA + "coach_icon.png"))
	pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_WAIT)


	# C.MONITOR_SIZE = (
	# 	pygame.display.Info().current_w,
	# 	pygame.display.Info().current_h
	# )
	# C.WINDOW_POS = (
	# 	(19/20)*C.MONITOR_SIZE[0] - (C.PANE_WIDTH + C.BOARD_WIDTH),
	# 	C.MONITOR_SIZE[1]/10
	# )

	os.environ["SDL_VIDEO_WINDOW_POS"] = "%d,%d" % C.WINDOW_POS

	coach  = Coach()
	clock  = coach.clock
	board  = coach.board
	engine = coach.engine

	running = True
	done    = False
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

			# Keyboard
			elif event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE,pygame.K_LEFT,pygame.K_RIGHT):
				### exit pane or quit
				if event.key == pygame.K_ESCAPE:
					for context in coach.contexts:
						if context.show:
							context.show = False
							break
					else:
						running = False

				### shut tray
				elif event.key == pygame.K_LEFT:
					if coach.tray:
						coach.toggle_tray.click()

				### open tray
				elif event.key == pygame.K_RIGHT:
					if not coach.tray:
						coach.toggle_tray.click()

			# Clock
			elif event in clock.TICKS:
				coach.clock.handle_tick(event)

			# Coach
			elif event.type in (
				pygame.KEYDOWN,
				pygame.KEYUP,
				pygame.MOUSEBUTTONDOWN,
				pygame.MOUSEBUTTONUP,
				pygame.MOUSEMOTION,
				pygame.MOUSEWHEEL,
			):
				coach.handle_click(event)

		if not done:
			# TODO: CONSUMMATION (king placement at end of game)
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
