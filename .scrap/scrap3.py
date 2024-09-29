import pygame
pygame.init()

SURF_WIDTH, SURF_HEIGHT = 800, 600
surface = pygame.display.set_mode((SURF_WIDTH, SURF_HEIGHT))
pygame.display.set_caption("Pause and Resume")

clock = pygame.time.Clock()
FPS = 30
active = True
time_elapsed = 0

font = pygame.freetype.SysFont("Arial.ttf", 32)
time_label, time_label_rect = font.render("Time elapsed (ms):", "white")
time_count, time_count_rect = font.render(str(time_elapsed), "white")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                print("Timer paused.")
                active = False
            elif event.key == pygame.K_r:
                print("Timer resumed.")
                active = True

    clock.tick(FPS)
    if active:
        time_elapsed += clock.get_time()
        surface.fill("black")
    time_count, time_count_rect = font.render(str(time_elapsed), "white")
    surface.blit(time_label, (10, 10))
    surface.blit(time_count, (25 + time_label_rect.width, 10))
    pygame.display.update()

pygame.quit()
