import pygame
import time

import ledwall

# read settings from settings.py
# use default values if no settings.py exists
try:
    from settings import *
except ImportError:
    pass

if not 'RENDER_MODE' in dir():
    # 'led' = for led wall output
    # 'plain' = for pc/laptop or testing
    # 'sim' = led simulation for uli (deprecated)
    # 'arcade' = for toolbox arcade cabinet
    # 'square' = for square displays
    RENDER_MODE = 'led'

if not 'DEFAULT_BRIGHTNESS' in dir():
    if RENDER_MODE == 'led':
        BRIGHTNESS = -4
    else:
        BRIGHTNESS = 0


running = True
output = ledwall.initScreen(RENDER_MODE)

ledwall.setBrightnessValue(BRIGHTNESS)


GRID_HEIGHT = 40
GRID_WIDTH = 11

HEX_WIDTH = 24
HEX_HEIGHT = 8

clock = pygame.time.Clock()
tick = 0

def initGrid(width, height):
    d = {}

    def addSegment(x1, y1, x2, y2, color):
        index = (x1, y1, x2, y2)
        d[index] = color

    defaultColor = (64, 64, 64)

    for y in range(height):
        for x in range(width):
            addSegment(x, y, x, y+1, defaultColor)

            if y % 4 == 0:
                addSegment(x, y, x-1, y+1, defaultColor)
            elif y % 4 == 2:
                addSegment(x, y, x+1, y+1, defaultColor)

    return d

def setSegmentColor(pointFrom, pointTo, color):
    points = sorted((pointFrom, pointTo))
    index = (points[0][0], points[0][1], points[1][0], points[1][1])
    grid[index] = color


def getScreenCoords(x, y):
    if y % 4 == 0 or y % 4 == 3:
        px = x * HEX_WIDTH
        py = y * HEX_HEIGHT
    else:
        px = (x + 0.5) * HEX_WIDTH
        py = y * HEX_HEIGHT

    return px, py


grid = initGrid(GRID_WIDTH, GRID_HEIGHT)

playerX = 4
playerY = 12


while running:
    output.fill((0, 0, 0))

    # draw grid

    for segment, color in grid.items():
        x1, y1, x2, y2 = segment

        x1, y1 = getScreenCoords(x1, y1)
        x2, y2 = getScreenCoords(x2, y2)

        pygame.draw.line(output, ledwall.brightness(color), (x1, y1), (x2, y2))


    px, py = getScreenCoords(playerX, playerY)

    # draw player
    pygame.draw.ellipse(output, ledwall.brightness((255, 0, 0)), rect=(px-2, py-2, 5, 5))

    # draw logo

    ledwall.font_huge.centerText(output, 'HEXGRID', y=2, fgcolor=ledwall.brightness((0, 255, 0)))
    ledwall.compose()


    # event handling

    oldx, oldy = playerX, playerY

    events = pygame.event.get()

    for e in events:
        if e.type==pygame.QUIT:
            running = False
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                running = False

            if e.key == pygame.K_F1:
                BRIGHTNESS -= 1
                ledwall.setBrightnessValue(BRIGHTNESS)
                #EventTimer.set('brightness-msg', 60)
            elif e.key == pygame.K_F2:
                BRIGHTNESS = min(BRIGHTNESS + 1, 0)
                ledwall.setBrightnessValue(BRIGHTNESS)
                #EventTimer.set('brightness-msg', 60)
            elif e.key == pygame.K_F5:
                ledwall.enableOverlay(not ledwall.showOverlay)
            elif e.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()

            elif e.key == pygame.K_LEFT:
                if playerY % 4 == 0:
                    playerX -= 1
                    playerY += 1
                elif playerY % 4 == 1:
                    playerY -= 1
                elif playerY % 4 == 2:
                    playerY += 1
                elif playerY % 4 == 3:
                    playerY -= 1
                    playerX -= 1

            elif e.key == pygame.K_RIGHT:
                if playerY % 4 == 0:
                    playerY += 1
                elif playerY % 4 == 1:
                    playerX += 1
                    playerY -= 1
                elif playerY % 4 == 2:
                    playerY += 1
                    playerX += 1
                elif playerY % 4 == 3:
                    playerY -= 1

            elif e.key == pygame.K_UP:
                playerY -= 1

            elif e.key == pygame.K_DOWN:
                playerY += 1

    if oldx != playerX or oldy != playerY:
        setSegmentColor((oldx, oldy), (playerX, playerY), (0, 255, 0))

    clock.tick(60)
    tick += 1
