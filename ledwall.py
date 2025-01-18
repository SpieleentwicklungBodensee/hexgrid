import pygame
from bitmapfont import BitmapFont

SCR_W = 256
SCR_H = 320

window = None   # the actual ui window
output = None   # the render target
scaled = None   # scale surface to distort output
overlay = None  # vertical masking stripes

brightnessValue = -4

renderMode = 'led'

pygame.display.init()


font = BitmapFont('gfx/heimatfont.png', scr_w=SCR_W, scr_h=SCR_H)
font_big = BitmapFont('gfx/heimatfont.png', zoom=2, scr_w=SCR_W, scr_h=SCR_H)
font_huge = BitmapFont('gfx/heimatfont.png', zoom=3, scr_w=SCR_W, scr_h=SCR_H)


def initScreen(mode='led'):
    global window, output, scaled, overlay, renderMode
    
    renderMode = mode
    
    if renderMode == 'led':
        window = pygame.display.set_mode((1920, 1080), flags=pygame.FULLSCREEN)
        output = pygame.Surface((SCR_W, SCR_H))
        scaled = pygame.Surface((SCR_W * 2, SCR_H))
        overlay = pygame.Surface((SCR_W * 2, SCR_H), flags=pygame.SRCALPHA)

        for x in range(SCR_W):
            pygame.draw.line(overlay, (0, 0, 0), (x * 2, 0), (x * 2, SCR_H))
        
    elif renderMode == 'plain':
        window = pygame.display.set_mode((SCR_W, SCR_H), flags=pygame.SCALED)
        output = window
        
    return output
    

def compose():
    if renderMode == 'plain':
        pass
        
    elif renderMode == 'led':
        pygame.transform.scale(output, (SCR_W * 2, SCR_H), scaled)
        window.blit(scaled, (0, 0))
        window.blit(overlay, (0, 0))

    pygame.display.flip()
    

def setBrightnessValue(b):
    global brightnessValue
    brightnessValue = b

def gamma(v):
    return min(v * 2**(brightnessValue / 4), 255)

def brightness(color):
    color = list(color)
    if isinstance(color[0], (list, tuple)):
        result = []
        for co in color:
            result.append(tuple([gamma(c) for c in co]))
        return result
    return tuple([gamma(c) for c in color])
    
    
