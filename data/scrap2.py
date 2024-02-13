from data.Constants import C

pgn = []
coords = []
for r in range(8,0,-1):
	for f in range(1,9):
		pgn.append((C.FILES[f] + str(r)))
		coords.append((f,r))
	print(pgn)
	#print(coords)
	pgn,coords = [],[]
