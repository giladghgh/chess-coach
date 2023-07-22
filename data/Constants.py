class C:
	FILES = ('a','b','c','d','e','f','g','h')
	# RANKS is left as an exercise to the user.

	INAUGURATION = [
		['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
		['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
		['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
		['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
		['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
		['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
		['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
		['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
	]

	TILE_LIGHT = (175,175,175)
	TILE_LIGHT_HIGH = (200,150,100)
	TILE_DARK = (80, 80, 80)
	TILE_DARK_HIGH = (125,75,45)

	CHESS_SET = {
		1:'Classic',
		2:'Tutorial',
		3:'Staunton'
	}[1]