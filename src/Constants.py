import os





# GAMEPLAY CONSTANTS
class C:
	# MECHANICS
	FILES = (None,"a","b","c","d","e","f","g","h")

	INIT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

	# INIT_FEN = "3r3r/2k5/8/1R6/4Q2Q/8/1K6/R6Q w - - 0 1"    # disambiguation testing
	# INIT_FEN = "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1"       # castle testing
	# INIT_FEN = "1r6/P6K/8/8/8/8/p6k/8 w - - 0 1"            # promote away from check
	# INIT_FEN = "8/8/8/8/8/8/8/k3K2R w K - 0 1"              # castle into check
	# INIT_FEN = "1q5k/8/8/5Q2/1p6/8/P7/1K6 w - - 0 1"        # e.p. into check

	IMPORT_FEN_DEFAULT = "3r3r/2k5/8/1R6/4Q2Q/8/1K6/R6Q b - - 0 1"          # disambiguation practice
	# DEFAULT_FEN_IMPORT = "kp6/1p6/1p6/8/8/8/5P1R/7K w - - 0 1"              # engine search practice


	# INTERFACE
	GRID_GAP = 10

	BOARD_WIDTH = BOARD_HEIGHT = 800        # NO LOWER THAN 600
	BOARD_SIZE  = (BOARD_WIDTH,BOARD_HEIGHT)

	TILE_WIDTH  = BOARD_WIDTH  // 8
	TILE_HEIGHT = BOARD_HEIGHT // 8
	TILE_SIZE   = (TILE_WIDTH,TILE_HEIGHT)

	BUTTON_WIDTH = BUTTON_HEIGHT = 50
	BUTTON_SIZE  = (BUTTON_WIDTH,BUTTON_HEIGHT)

	SIDEBAR_WIDTH  = 275
	TEXTBOX_WIDTH  = 225
	TEXTBOX_HEIGHT = 18

	# SIDEBAR_X_MARGIN = (SIDEBAR_WIDTH - TEXTBOX_WIDTH)/2
	SIDEBAR_X_MARGIN = TEXTBOX_WIDTH / 15
	SIDEBAR_Y_MARGIN = 20

	WINDOW_SIZE = (BOARD_WIDTH + SIDEBAR_WIDTH , BOARD_HEIGHT)
	WINDOW_POS  = (100,100)


	# BOARD STYLES
	TILE_LIGHT_BASIC_HAZEL = (200,180,145)
	TILE_LIGHT_FRESH_HAZEL = (200,160, 75)
	TILE_DARK_BASIC_HAZEL = (115, 80, 55)
	TILE_DARK_FRESH_HAZEL = (165,115, 45)
	BOARD_STYLE_HAZEL = (
		TILE_LIGHT_BASIC_HAZEL,
		TILE_LIGHT_FRESH_HAZEL,
		TILE_DARK_BASIC_HAZEL,
		TILE_DARK_FRESH_HAZEL
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
	TILE_DARK_BASIC_CHEAP = ( 85,120,100)
	TILE_DARK_FRESH_CHEAP = (160,100,  0)
	BOARD_STYLE_CHEAP = (
		TILE_LIGHT_BASIC_CHEAP,
		TILE_LIGHT_FRESH_CHEAP,
		TILE_DARK_BASIC_CHEAP,
		TILE_DARK_FRESH_CHEAP
	)

	BOARD_STYLE = BOARD_STYLE_HAZEL

	TILE_FOCUS_LIGHT = (205,90,80)
	TILE_FOCUS_DARK  = (180,75,60)

	BACKGR_COLOUR = (165,165,170)
	BACKGR_COLOUR_SETTINGS = (125,125,125)
	BACKGR_COLOUR_ANALYSIS = (125,150, 75)

	TEXTBOX_LIGHT = (225,225,225)
	TEXTBOX_DARK  = (118,128,128)

	BUTTON_COLOUR_NEUTRAL = (215,215,215)
	BUTTON_COLOUR_ACTIVE  = (100,110,100)

	ARROW_COLOUR = (250,175,35,190)


	# PIECE STYLE
	PIECE_STYLE = (
		"CLASSIC",
		"TUTORIAL",
		"3D"
	)[0]

	DIR         = os.getcwd()
	DIR_MEDIA   = DIR + "\\media"
	DIR_SETS    = DIR_MEDIA + "\\sets\\" + PIECE_STYLE + "\\"
	DIR_SOUNDS  = DIR_MEDIA + "\\sounds"
	DIR_ICONS   = DIR_MEDIA + "\\icons"
	DIR_BUTTONS = DIR_ICONS + "\\buttons"
	DIR_BOTS    = DIR_ICONS + "\\bots"


	# ECO Interpreter
	EXAMPLE_MOVETEXT = "1. b4 a5 2. bxa5 Nc6 3. a6 Rb8 4. a7 Nb4 5. a8=Q Na6 6. e4 f5 7. Qxb8 g5 8. Qe2 Nxb8 9. Qf3 fxe4 10. Qg4 e3 11. dxe3 Na6 12. Bxa6 bxa6 13. Qh5"
	OPENINGS = {
		"1. d4 d5"       : "Queen's Pawn Game",
		"1. d4 d5 2. c4" : "Queen's Gambit",
		"1. d4 d5 2. c4 c6" : "Slav Defence",
		"1. d4 d5 2. e4" : "Blackmar-Diemer Gambit"
	}





# ENGINE CONSTANTS
class E:
	# INIT_SCHEME = [None,"BASIC"]
	# INIT_SCHEME = [None,"RANDOM"]
	INIT_SCHEME = [None,None]

	# STATIC SCORETABLES
	SCORETABLE_MATERIAL_BASIC = {
		"P" : 10,
		"N" : 30,
		"B" : 30,
		"R" : 50,
		"Q" : 90,
		"K" : 1000
	}
	SCORETABLE_MATERIAL_TUNED = {
		"P" : 10,
		"N" : 33,
		"B" : 35,
		"R" : 50,
		"Q" : 95,
		"K" : 1000
	}
	SCORETABLE_MATERIAL = SCORETABLE_MATERIAL_BASIC

	SCORETABLE_POSITION_BASIC = {
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
				(  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ,  0 ),
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
	SCORETABLE_POSITION = SCORETABLE_POSITION_BASIC