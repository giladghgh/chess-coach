centre = [l/2 for l in (500,500)]

print(
	list(map(sum,zip(centre,[100,100])))
)


import pygame
print(sorted(pygame.font.get_fonts()))
#  'agencyfb', 'algerian', 'arial', 'arialblack', 'arialrounded', 'bahnschrift', 'baskervilleoldface', 'bauhaus93',
#  'bell', 'bentonsans', 'bentonsansblack', 'bentonsansbook', 'bentonsansmedium', 'bentonsansregular', 'berlinsansfb',
#  'berlinsansfbdemi', 'bernardcondensed', 'blackadderitc', 'bodoni', 'bodoniblack', 'bodonicondensed',
#  'bodonipostercompressed', 'bookantiqua', 'bookmanoldstyle', 'bookshelfsymbol7', 'bradleyhanditc', 'britannic',
#  'broadway', 'brushscript', 'calibri', 'californianfb', 'calisto', 'cambria', 'cambriamath', 'candara',
#  'cascadiacoderegular', 'cascadiamonoregular', 'castellar', 'centaur', 'century', 'centurygothic', 'centuryschoolbook',
#  'chevinmedium', 'chiller', 'colonna', 'comicsansms', 'consolas', 'constantia', 'cooperblack', 'copperplategothic',
#  'corbel', 'couriernew', 'curlz', 'doulossil', 'dubai', 'dubaimedium', 'dubairegular', 'ebrima', 'econsansregular',
#  'edwardianscriptitc', 'elephant', 'engravers', 'erasdemiitc', 'erasitc', 'erasmediumitc', 'extra', 'felixtitling',
#  'flamabasic', 'footlight', 'forte', 'franklingothicbook', 'franklingothicdemi', 'franklingothicdemicond',
#  'franklingothicheavy', 'franklingothicmedium', 'franklingothicmediumcond', 'freestylescript', 'frenchscript',
#  'gabriola', 'gadugi', 'garamond', 'georgia', 'gigi', 'gillsans', 'gillsanscondensed', 'gillsansextcondensed',
#  'gillsansultra', 'gillsansultracondensed', 'gloucesterextracondensed', 'goudyoldstyle', 'goudystout',
#  'haettenschweiler', 'harlowsolid', 'harrington', 'hightowertext', 'holomdl2assets', 'impact', 'imprintshadow',
#  'informalroman', 'inkfree', 'javanesetext', 'jokerman', 'juiceitc', 'kristenitc', 'kunstlerscript', 'leelawadee',
#  'leelawadeeui', 'leelawadeeuisemilight', 'lucidabright', 'lucidacalligraphy', 'lucidaconsole', 'lucidafax',
#  'lucidafaxregular', 'lucidahandwriting', 'lucidasans', 'lucidasansregular', 'lucidasansroman', 'lucidasanstypewriter',
#  'lucidasanstypewriteroblique', 'lucidasanstypewriterregular', 'magneto', 'maiandragd', 'malgungothic',
#  'malgungothicsemilight', 'maturascriptcapitals', 'merriweather', 'merriweatherblack', 'merriweatherregular',
#  'merriweathersans', 'merriweathersansregular', 'microsofthimalaya', 'microsoftjhenghei', 'microsoftjhengheiui',
#  'microsoftnewtailue', 'microsoftphagspa', 'microsoftsansserif', 'microsofttaile', 'microsoftuighur', 'microsoftyahei',
#  'microsoftyaheiui', 'microsoftyibaiti', 'mingliuextb', 'mingliuhkscsextb', 'mistral', 'modernno20', 'mongolianbaiti',
#  'monotypecorsiva', 'msgothic', 'msoutlook', 'mspgothic', 'msreferencesansserif', 'msreferencespecialty', 'msuigothic',
#  'mvboli', 'myanmartext', 'niagaraengraved', 'niagarasolid', 'nirmalaui', 'nirmalauisemilight', 'nsimsun',
#  'ocraextended', 'oldenglishtext', 'onyx', 'palacescript', 'palatinolinotype', 'papyrus', 'parchment', 'perpetua',
#  'perpetuatitling', 'playbill', 'pmingliuextb', 'poorrichard', 'pristina', 'ptsans', 'rage', 'ravie', 'rockwell',
#  'rockwellcondensed', 'rockwellextra', 'script', 'segoemdl2assets', 'segoeprint', 'segoescript', 'segoeui',
#  'segoeuiblack', 'segoeuiemoji', 'segoeuihistoric', 'segoeuisemibold', 'segoeuisemilight', 'segoeuisymbol',
#  'showcardgothic', 'simsun', 'simsunextb', 'sitkabanner', 'sitkadisplay', 'sitkaheading', 'sitkasmall',
#  'sitkasubheading', 'sitkatext', 'snapitc', 'stencil', 'supertext01', 'swgamekeys', 'sylfaen', 'symbol', 'tahoma',
#  'tempussansitc', 'timesnewroman', 'trebuchetms', 'twcen', 'twcencondensed', 'twcencondensedextra', 'verdana',
#  'vinerhanditc', 'vivaldi', 'vladimirscript', 'voynich101', 'webdings', 'widelatin', 'wingdings', 'wingdings2',
#  'wingdings3', 'yugothic', 'yugothicmedium', 'yugothicregular', 'yugothicui', 'yugothicuiregular', 'yugothicuisemibold',
#  'yugothicuisemilight'
