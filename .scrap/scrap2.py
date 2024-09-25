import sys, pygame
pygame.init()

size = width, height = 640, 480
black = 0, 0, 0

screen = pygame.display.set_mode(size)

# some globals we need
avatar_w = 64
avatar_h = 64

# our game objects are (inneficient) maps with two keys: rect and image
avatar1 = dict()
avatar2 = dict()
avatar3 = dict()

avatar1["rect"] = pygame.Rect(16, 16, avatar_w, avatar_h)
avatar2["rect"] = pygame.Rect(16 + avatar_w + 8, 16, avatar_w, avatar_h)
avatar3["rect"] = pygame.Rect(16 + avatar_w * 2 + 8 + 8, 16, avatar_w, avatar_h)

clickables = (avatar1, avatar2, avatar3)

# resource loading
# crash if the files are not in place (OK for now)
avatar1["image"] = pygame.image.load("avatar1.png")
avatar2["image"] = pygame.image.load("avatar2.png")
avatar3["image"] = pygame.image.load("avatar3.png")

# procedural generation of a circled mask is possible but for now we
# will use an asset
mask = pygame.image.load("mask.png")

masked_avatar = dict()
masked_avatar["image"] = mask
masked_avatar["rect"] = pygame.Rect(size[0] / 2 - avatar_w / 2, 16 + avatar_h * 2, avatar_w, avatar_h)

renderables = (avatar1, avatar2, avatar3, masked_avatar)

def update_masked_avatar (avatar):
    global masked_avatar
    # consider clearing then blit to masked_avatar rather than
    # cloning mask each time, but it's not so simple as it sounds, when
    # you blit, you need the alphas from mask to be transferred too.
    # The lazy, I don't want to do research now, approach is to clone.
    surf = mask.copy()
    surf.blit(avatar["image"], (0, 0), None, pygame.BLEND_RGBA_MULT)
    masked_avatar["image"] = surf

# main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            sys.exit()

    mouse_pos = pygame.mouse.get_pos()

    # process the clickables list
    for obj in clickables:
        if obj["rect"].collidepoint(mouse_pos):
            update_masked_avatar(obj)

    screen.fill((0,150,0))

    # process the renderables list
    for obj in renderables:
        screen.blit(obj["image"], obj["rect"])

    pygame.display.flip()
