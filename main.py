import pygame
import math

#initialize pygame
pygame.init()

# create the screen
screen = pygame.display.set_mode((800, 600))
# caption and icon
pygame.display.set_caption("ACAS-Xu")
icon = pygame.image.load('spaceship.png')
pygame.display.set_icon(icon)

defenderIcon = pygame.image.load('spaceship.png')
attackerIcon =  pygame.image.load('spaceship.png')
defenderX = 370
defenderY = 280
attackerX = 430
attackerY = 310
defenderVX = 0
defenderVY = 0.1
attackerVX = 0.1
attackerVY = 0.1

# bearing angle from north
def defender(bearing, x, y):
    icon = pygame.transform.rotate(defenderIcon, -90 + bearing)
    screen.blit(icon, (x, y))

def attacker(bearing, x, y):
    icon = pygame.transform.rotate(attackerIcon, -90 + bearing)
    screen.blit(icon, (x, y))

running = True
while running:
    screen.fill((255, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    defenderX += defenderVX
    defenderY += defenderVY
    defender(math.degrees(math.atan2(-defenderVY, defenderVX)), defenderX, defenderY)

    attackerX += attackerVX
    attackerY += attackerVY
    attacker(math.degrees(math.atan2(-attackerVY, attackerVX)), attackerX, attackerY)
    pygame.display.update()
