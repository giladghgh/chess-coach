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
	# 	(19/20)*C.MONITOR_SIZE[0] - (C.PANE_WIDTH + C.BOARD_WIDTH),
	# 	C.MONITOR_SIZE[1]/10
	# )

	os.environ["SDL_VIDEO_WINDOW_POS"] = "%d,%d" % C.WINDOW_POS

	coach  = Coach()
	clock  = coach.clock
	board  = coach.board
	engine = coach.engine

	cache   = None
	running = True
	done    = False
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

			# Keyboard
			elif event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE,pygame.K_RIGHT,pygame.K_LEFT):
				match event.key:
					### quit or shut pane
					case pygame.K_ESCAPE:
						for context in coach.contexts:
							if context.show:
								context.show = False
								break
						else:
							running = False

					### open tray
					case pygame.K_RIGHT:
						if not coach.toggle_tray.active:
							coach.toggle_tray.active = False
							coach.toggle_tray.click()

					### shut tray
					case pygame.K_LEFT:
						if coach.toggle_tray.active:
							coach.toggle_tray.active = True
							coach.toggle_tray.click()

			# Clock
			elif event in (clock.whiteface.timer.TICK,clock.blackface.timer.TICK):
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

			# TODO: KING BURIALS
			if coach.is_game_over():
				done = True

				# Clock
				# pygame.time.set_timer(pygame.USEREVENT,0)

				if board.outcome[0] == "Draw":
					print("The game is a draw by " + board.outcome[1].lower() + "!")
				elif board.outcome[1] == "Checkmate":
					print(board.outcome[0] + " wins by checkmate!")

			elif engine.scheme[board.ply == "b"] and len(board.movelog) == board.halfmovenum:
				engine.play()

		# coach.screen.fill(C.BACKGR_PANE , (0,0,C.PANE_WIDTH,C.BOARD_HEIGHT))
		# coach.screen.fill(C.BACKGR_TRAY , (C.PANE_WIDTH + C.BOARD_WIDTH,0,C.TRAY_WIDTH,C.BOARD_HEIGHT))
		coach.screen.fill(C.BACKGR_PANE)
		board.render()
		coach.render()
		pygame.display.update()
