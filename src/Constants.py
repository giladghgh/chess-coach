import os





class C:
	# INITIALS
	INIT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
	# INIT_FEN = "Q7/ppppppPp/8/7K/8/7k/RrBbPPNn/8 w - - 0 1"    # graveyard test
	# INIT_FEN = "3r3r/2k5/8/1R6/4Q2Q/8/1K6/R6Q w - - 0 1"    # disambiguation test
	# INIT_FEN = "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1"       # castle test
	# INIT_FEN = "1r6/P6K/8/8/8/8/p6k/8 w - - 0 1"            # promote away from check
	# INIT_FEN = "8/8/8/8/8/8/8/k3K2R w K - 0 1"              # castle into check
	# INIT_FEN = "1Q5K/8/8/5q2/1p6/8/P7/1k6 w - - 0 1"        # e.p. into check

	PIECE_STYLE = "CLASSIC"

	SHOW_MOVE_FRESH = True
	SHOW_MOVE_LEGAL = True
	SHOW_TILE_COORD = False
	BOARD_FLIPPED   = False



	# MECHANICS
	FILES = (None,"a","b","c","d","e","f","g","h")

	# IMPORT_FEN_DEFAULT = "k7/1p6/1p6/8/8/8/5P1R/7K b - - 3 18"              # engine search practice
	IMPORT_FEN_DEFAULT = "k7/1p2n3/1p6/8/8/8/5P1R/7K w - - 1 1"             # engine search practice
	# IMPORT_FEN_DEFAULT = "3r3r/2k5/8/1R6/4Q2Q/8/1K6/R6Q b - - 0 1"          # disambiguation practice


	# GAMEPLAY
	AUTO_PROMOTE = "Q"

	TIME_STARTER_WHITE = (1,30,0)
	TIME_BONUS_WHITE   = 0

	TIME_STARTER_BLACK = (1,30,0)
	TIME_BONUS_BLACK   = 0


	# INTERFACE
	MOVE_SPEED 	= 8
	MOVE_VOLUME = 1

	GRID_GAP = 10

	X_MARGIN = 15
	Y_MARGIN = 20

	SIDEBAR_WIDTH = 275

	BOARD_WIDTH = BOARD_HEIGHT = 800                ### NO LOWER THAN 600 (i think)
	BOARD_SIZE  = (BOARD_WIDTH,BOARD_HEIGHT)

	TILE_WIDTH  = BOARD_WIDTH  // 8
	TILE_HEIGHT = BOARD_HEIGHT // 8
	TILE_SIZE   = (TILE_WIDTH,TILE_HEIGHT)

	BUTTON_WIDTH = BUTTON_HEIGHT = 50
	BUTTON_SIZE  = (BUTTON_WIDTH,BUTTON_HEIGHT)

	PANE_GAP   = 8*GRID_GAP
	PANE_WIDTH = SIDEBAR_WIDTH
	PANE_SIZE  = (PANE_WIDTH + PANE_GAP , BOARD_HEIGHT)

	TRAY_GAP   = 3*GRID_GAP
	TRAY_WIDTH = (2/3)*SIDEBAR_WIDTH
	TRAY_SIZE  = (TRAY_GAP + TRAY_WIDTH , BOARD_HEIGHT)

	TEXTBOX_WIDTH  = 225
	TEXTBOX_HEIGHT = 18
	TEXTBOX_SIZE   = (TEXTBOX_WIDTH,TEXTBOX_HEIGHT)

	WINDOW_WIDTH  = SIDEBAR_WIDTH + BOARD_WIDTH + TRAY_WIDTH
	WINDOW_HEIGHT = BOARD_HEIGHT
	WINDOW_SIZE   = (PANE_WIDTH + BOARD_WIDTH + TRAY_WIDTH , BOARD_HEIGHT)
	# WINDOW_POS  = (100,100)
	WINDOW_POS = (30,130)


	# COACH STYLES
	BACKGR_PANE     = (165,165,165)
	BACKGR_TRAY     = ( 50, 45, 45)
	BACKGR_SETTINGS = (120,120,120)
	BACKGR_ANALYSIS = (105,115,120)
	BACKGR_COACHING = (125,128,115)

	TEXTBOX_LIGHT = (155,155,155)
	TEXTBOX_DARK  = (100,105,105)

	BUTTON_LIVE   = (100,110,100)
	BUTTON_IDLE   = (  0,  0, 25, 50)
	BUTTON_DEAD   = (215,215,215)
	BUTTON_BORDER = (  0,  0,  0, 15)

	TIMER_LIVE      = ( 80, 25, 20)
	TIMER_IDLE      = (115,115,115)
	TIMER_DEAD      = (  0,  0,  0,  0)
	TIMER_CASE_LIVE = (215,215,215)
	TIMER_CASE_DEAD = (115,115,115)

	BANNER_COLOUR = ( 75, 75, 75)
	SLIDER_COLOUR = (215,215,215,150)
	ARROW_COLOUR  = (250,175, 35,180)


	# BOARD STYLES
	TILE_FOCUS_LIGHT = (205, 90, 80)
	TILE_FOCUS_DARK  = (180, 75, 60)

	TILE_LIGHT_BASIC_BROWN = (200,180,145)
	TILE_LIGHT_FRESH_BROWN = (200,160, 75)
	TILE_DARK_BASIC_BROWN  = (115, 80, 55)
	TILE_DARK_FRESH_BROWN  = (165,115, 45)
	BOARD_STYLE_BROWN = (
		TILE_LIGHT_BASIC_BROWN,
		TILE_LIGHT_FRESH_BROWN,
		TILE_DARK_BASIC_BROWN,
		TILE_DARK_FRESH_BROWN
	)

	TILE_LIGHT_BASIC_BLEAK = (175,175,175)
	TILE_LIGHT_FRESH_BLEAK = (200,150,100)
	TILE_DARK_BASIC_BLEAK  = ( 80, 80, 80)
	TILE_DARK_FRESH_BLEAK  = (125, 75, 45)
	BOARD_STYLE_BLEAK = (
		TILE_LIGHT_BASIC_BLEAK,
		TILE_LIGHT_FRESH_BLEAK,
		TILE_DARK_BASIC_BLEAK,
		TILE_DARK_FRESH_BLEAK
	)

	TILE_LIGHT_BASIC_CHEAP = (205,205,205)
	TILE_LIGHT_FRESH_CHEAP = (200,170,100)
	TILE_DARK_BASIC_CHEAP  = ( 85,120,100)
	TILE_DARK_FRESH_CHEAP  = (160,100,  0)
	BOARD_STYLE_CHEAP = (
		TILE_LIGHT_BASIC_CHEAP,
		TILE_LIGHT_FRESH_CHEAP,
		TILE_DARK_BASIC_CHEAP,
		TILE_DARK_FRESH_CHEAP
	)

	BOARD_STYLE = BOARD_STYLE_BROWN


	# DIRECTORIES
	DIR         = os.getcwd()
	DIR_MEDIA   = DIR + "\\media\\"
	DIR_ICONS   = DIR_MEDIA + "icons\\"
	DIR_SETS    = DIR_MEDIA + "sets\\"
	DIR_SET     = DIR_SETS + PIECE_STYLE + "\\"
	DIR_SOUNDS  = DIR_MEDIA + "sounds\\"







class E:
	# INITIALS
	INIT_SCHEME = [None,None]
	# INIT_SCHEME = [None,"SIMPLE"]
	# INIT_SCHEME = [None,"RANDOM"]

	BOT_DEPTH_BLACK = 2
	BOT_DEPTH_WHITE = 1



	# SCOREBOARDS
	SCOREBOARD_MATERIAL_BASIC = {
		"P" : 1,
		"N" : 3,
		"B" : 3,
		"R" : 5,
		"Q" : 9,
		"K" : 100
	}
	SCOREBOARD_MATERIAL_TUNED = {
		"P" : 1,
		"N" : 3.3,
		"B" : 3.5,
		"R" : 5,
		"Q" : 9.5,
		"K" : 100
	}
	SCOREBOARD_MATERIAL = SCOREBOARD_MATERIAL_BASIC

	SCOREBOARD_POSITION_BASIC = {               ### in centipawns I guess
		"P" : [
				( 99 , 99 , 99 , 99 , 99 , 99 , 99 , 99 ),
				( 50 , 50 , 50 , 50 , 50 , 50 , 50 , 50 ),
				( 10 , 10 , 20 , 30 , 30 , 20 , 10 , 10 ),
				(  5 ,  5 , 10 , 25 , 25 , 10 ,  5 ,  5 ),
				(  0 ,  0 ,  0 , 20 , 20 ,  0 ,  0 ,  0 ),
				(  5 , -5 ,-10 ,  0 ,  0 ,-10 , -5 ,  5 ),
				(  5 , 10 , 10 ,-20 ,-20 , 10 , 10 ,  5 ),
				(  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 )
			],
		"N" : [
				(-50 ,-40 ,-30 ,-30 ,-30 ,-30 ,-40 ,-50 ),
				(-40 ,-20 ,  0 ,  0 ,  0 ,  0 ,-20 ,-40 ),
				(-30 ,  0 , 10 , 15 , 15 , 10 ,  0 ,-30 ),
				(-30 ,  5 , 15 , 20 , 20 , 15 ,  5 ,-30 ),
				(-30 ,  0 , 15 , 20 , 20 , 15 ,  0 ,-30 ),
				(-30 ,  5 , 10 , 15 , 15 , 10 ,  5 ,-30 ),
				(-40 ,-20 ,  0 ,  5 ,  5 ,  0 ,-20 ,-40 ),
				(-50 ,-40 ,-30 ,-30 ,-30 ,-30 ,-40 ,-50 )
			],
		"B" : [
				(-20 ,-10 ,-10 ,-10 ,-10 ,-10 ,-10 ,-20 ),
				(-10 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,-10 ),
				(-10 ,  0 ,  5 , 10 , 10 ,  5 ,  0 ,-10 ),
				(-10 ,  5 ,  5 , 10 , 10 ,  5 ,  5 ,-10 ),
				(-10 ,  0 , 10 , 10 , 10 , 10 ,  0 ,-10 ),
				(-10 , 10 , 10 , 10 , 10 , 10 , 10 ,-10 ),
				(-10 ,  5 ,  0 ,  0 ,  0 ,  0 ,  5 ,-10 ),
				(-20 ,-10 ,-10 ,-10 ,-10 ,-10 ,-10 ,-20 )
			],
		"R" : [
				(  3 ,  3 ,  3 ,  3 ,  3 ,  3 ,  3 ,  3 ),
				(  5 , 10 , 10 , 10 , 10 , 10 , 10 ,  5 ),
				( -5 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 , -5 ),
				( -5 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 , -5 ),
				( -5 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 , -5 ),
				( -5 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 , -5 ),
				( -5 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 , -5 ),
				(  0 ,  0 ,  0 ,  5 ,  5 ,  0 ,  0 ,  0 )
			],
		"Q" : [
				(-20 ,-10 ,-10 , -5 , -5 ,-10 ,-10 ,-20 ),
				(-10 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,-10 ),
				(-10 ,  0 ,  5 ,  5 ,  5 ,  5 ,  0 ,-10 ),
				( -5 ,  0 ,  5 ,  5 ,  5 ,  5 ,  0 , -5 ),
				(  0 ,  0 ,  5 ,  5 ,  5 ,  5 ,  0 , -5 ),
				(-10 ,  5 ,  5 ,  5 ,  5 ,  5 ,  0 ,-10 ),
				(-10 ,  0 ,  5 ,  0 ,  0 ,  0 ,  0 ,-10 ),
				(-20 ,-10 ,-10 , -5 , -5 ,-10 ,-10 ,-20 )
			],
		"K" : [
				(-30 ,-40 ,-40 ,-50 ,-50 ,-40 ,-40 ,-30 ),
				(-30 ,-40 ,-40 ,-50 ,-50 ,-40 ,-40 ,-30 ),
				(-30 ,-40 ,-40 ,-50 ,-50 ,-40 ,-40 ,-30 ),
				(-30 ,-40 ,-40 ,-50 ,-50 ,-40 ,-40 ,-30 ),
				(-20 ,-30 ,-30 ,-40 ,-40 ,-30 ,-30 ,-20 ),
				(-10 ,-20 ,-20 ,-20 ,-20 ,-20 ,-20 ,-10 ),
				( 20 , 20 ,  0 ,  0 ,  0 ,  0 , 20 , 20 ),
				( 20 , 30 , 10 ,  0 ,  0 , 10 , 30 , 20 )
			]
	}
	SCOREBOARD_POSITION = SCOREBOARD_POSITION_BASIC
