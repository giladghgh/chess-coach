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

	coach = Coach()

	board  = coach.board
	engine = coach.engine
	clock  = coach.clock

	running = True
	playing = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_DELETE):
				running = False

			# Keyboard
			elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
				### exit
				running = False

			### prev/next move
			elif event.type == pygame.KEYDOWN and any([
				event.key == pygame.K_LEFT,
				event.key == pygame.K_RIGHT,
			]):
				match event.key:
					case pygame.K_LEFT:
						coach.buttons_turns["PREV"].click()
					case pygame.K_RIGHT:
						coach.buttons_turns["NEXT"].click()

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

		if playing:
			if board.is_game_over():
				coach.wrap()
				playing = False

		coach.screen.fill(C.BACKGR_PANE)
		coach.render()
		pygame.display.update()

		# if running and done:
		# 	print("running and done")

		if playing and not board.reminiscing and engine.schema[board.ply == "b"]:     ### after wrap so engine doesn't try play after game over
			engine.play()
