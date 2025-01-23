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


while running:
    output.fill((0, 0, 0))

    gridcolor = ledwall.brightness((0, 128 + ((tick * 2) % 128) if (tick * 2) % 256 < 128 else (255 - ((tick * 2) % 128)), 0))

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):

            def getCoords(x, y):
                if y % 4 == 0 or y % 4 == 3:
                    px = x * HEX_WIDTH
                    py = y * HEX_HEIGHT
                else:
                    px = (x + 0.5) * HEX_WIDTH
                    py = y * HEX_HEIGHT

                return px, py

            px1, py1 = getCoords(x, y)
            px2, py2 = getCoords(x, y+1)
            pygame.draw.line(output, gridcolor, (px1, py1), (px2, py2))

            if y % 4 == 0:
                px1, py1 = getCoords(x, y)
                px2, py2 = getCoords(x-1, y+1)
                pygame.draw.line(output, gridcolor, (px1, py1), (px2, py2))

            if y % 4 == 2:
                px1, py1 = getCoords(x, y)
                px2, py2 = getCoords(x+1, y+1)
                pygame.draw.line(output, gridcolor, (px1, py1), (px2, py2))

    ledwall.font_huge.centerText(output, 'HEXGRID', y=2, fgcolor=ledwall.brightness((0, 255, 0)))
    ledwall.compose()

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

    clock.tick(60)
    tick += 1
