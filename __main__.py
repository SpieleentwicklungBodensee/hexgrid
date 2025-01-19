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

while running:
    output.fill(ledwall.brightness((0,32,128)))

    ledwall.font_huge.centerText(output, 'HEXGRID', y=2)
    
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
            elif e.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
                
