import os,time
import pygame

from src.Constants import C,E
from src.Coach import Coach





if __name__ == "__main__":
	pygame.init()
	pygame.display.set_caption("Chess Coach")
	pygame.display.set_icon(pygame.image.load(C.DIR_MEDIA + "coach_icon.png"))
	pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_WAIT)

	os.environ["SDL_VIDEO_WINDOW_POS"] = "%d,%d" % C.WINDOW_POS

	coach  = Coach()
	clock  = coach.clock
	board  = coach.board
	engine = coach.engine

	running = True
	done    = False
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_DELETE):
				running = False

			# Keyboard
			elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
				### exit pane, or quit
				for context in coach.contexts:
					if context.show:
						context.show = False
						break
				else:
					running = False

			### prev/next move
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					coach.buttons_turns["PREV"].click()
				elif event.key == pygame.K_RIGHT:
					coach.buttons_turns["NEXT"].click()
				elif event.key in (pygame.K_UP,pygame.K_DOWN):
					print(E.BOT_DEPTH_WHITE , E.BOT_DEPTH_BLACK)

			# Clock
			elif event in clock.TICKS:
				coach.clock.tick(event)

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
			if coach.is_game_over():
				done = True

				print("###- GAME OVER -###")
				print(board.outcome[0] + " by " + board.outcome[1].lower() + "!")
				print("####-####-####-####")

		coach.screen.fill(C.BACKGR_PANE)
		board.render()
		coach.render()
		pygame.display.update()

		if engine.schema[board.ply == "b"] and len(board.movelog) == board.halfmovenum:
			engine.play()
