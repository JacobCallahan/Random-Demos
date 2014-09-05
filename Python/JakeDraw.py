import sys, pygame
from pygame import *

pygame.init()

screen = pygame.display.set_mode((1000, 600))
screen.fill((255,255,255))

#brush = pygame.draw.rect(screen, pygame.color.Color("Red"), (50, 50, 4, 4))

pygame.display.update()
clock = pygame.time.Clock()

z = 0

while 1:
    clock.tick(100)
    x,y = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            z = 1
        elif event.type == MOUSEBUTTONUP:
            z = 0

        if z == 1:
            pygame.draw.rect(screen, pygame.color.Color("Red"), (x-2, y-2, 4, 4))
            pygame.draw.rect(screen, pygame.color.Color("Blue"), (x-2 + 5, y-2 + 5, 4, 4))
            pygame.draw.rect(screen, pygame.color.Color("Yellow"), (x-2 -5, y-2 -5, 4, 4))
            pygame.draw.rect(screen, pygame.color.Color("Green"), (x-2 + 5, y-2 - 5, 4, 4))
            pygame.draw.rect(screen, pygame.color.Color("Orange"), (x-2 -5, y-2 + 5, 4, 4))
            pygame.display.update()
