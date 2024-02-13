import os



class C:
	# MECHANICS
	FILES = (None,"a","b","c","d","e","f","g","h")
	INIT_CONFIG = (
		["bR","bN","bB","bQ","bK","bB","bN","bR"],
		["bP","bP","bP","bP","bP","bP","bP","bP"],
		["  ","  ","  ","  ","  ","  ","  ","  "],
		["  ","  ","  ","  ","  ","  ","  ","  "],
		["  ","  ","  ","  ","  ","  ","  ","  "],
		["  ","  ","  ","  ","  ","  ","  ","  "],
		["wP","wP","wP","wP","wP","wP","wP","wP"],
		["wR","wN","wB","wQ","wK","wB","wN","wR"]
	)
	# INIT_CONFIG = (
	# 	["  ", "  ", "  ", "  ", "bK", "bB", "bB", "  "],
	# 	["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
	# 	["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
	# 	["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
	# 	["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
	# 	["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
	# 	["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
	# 	["  ", "  ", "  ", "  ", "wK", "  ", "  ", "  "]
	# )

	# INTERFACE
	BOARD_WIDTH  = BOARD_HEIGHT  = 600
	BOARD_SIZE = (BOARD_WIDTH,BOARD_HEIGHT)
	TILE_WIDTH   = BOARD_WIDTH  // 8
	TILE_HEIGHT  = BOARD_HEIGHT // 8
	TILE_SIZE   = (TILE_WIDTH,TILE_HEIGHT)
	BUTTON_WIDTH = BUTTON_HEIGHT = 50
	BUTTON_SIZE = (BUTTON_WIDTH,BUTTON_HEIGHT)

	SIDEBAR_WIDTH = 200
	BG_COLOUR     = (180,180,188)
	BUTTON_COLOUR = (215,215,215)

	TEXTBOX_LIGHT = (225,225,225)
	TEXTBOX_DARK  = (118,128,128)
	TEXTBOX_WIDTH  = (3/4) * SIDEBAR_WIDTH
	TEXTBOX_HEIGHT = 18
	TEXTBOX_X_OFFSET = TEXTBOX_WIDTH/15


	# BOARD
	TILE_LIGHT = (175,175,175)
	TILE_DARK  = (80,80,80)
	TILE_LIGHT_HIGH = (200,150,100)
	TILE_DARK_HIGH  = (125,75,45)


	# AESTHETICS
	PIECE_STYLE = {
		1:'Classic',
		2:'Tutorial',
		3:'3D'
	}[1]
	DIR       = os.getcwd()
	DIR_MEDIA = DIR + "\\media"
	DIR_SETS  = DIR_MEDIA + "\\Sets\\" + PIECE_STYLE + "\\"

	# OPENINGS
	EXAMPLE_MOVETEXT = "1. b4 a5 2. bxa5 Nc6 3. a6 Rb8 4. a7 Nb4 5. a8=Q Na6 6. e4 f5 7. Qxb8 g5 8. Qe2 Nxb8 9. Qf3 fxe4 10. Qg4 e3 11. dxe3 Na6 12. Bxa6 bxa6 13. Qh5"
	OPENINGS = {
		"1. d4 d5"       : "Queen's Pawn Game",
		"1. d4 d5 2. c4" : "Queen's Gambit",
		"1. d4 d5 2. c4 c6" : "Slav Defence",
		"1. d4 d5 2. e4" : "Blackmar-Diemer Gambit"
	}

	# ENGINE
	#INIT_PLAYER_SCHEME = ["random","random"]
	#INIT_PLAYER_SCHEME = [None,"Random"]
	INIT_PLAYER_SCHEME = [None,None]
