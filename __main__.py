import pygame
import pygame._sdl2.controller
import time

from enum import Enum

import ledwall
print = ledwall.print


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

DEADZONE = 0.4

running = True
output = ledwall.initScreen(RENDER_MODE)

ledwall.setBrightnessValue(BRIGHTNESS)


print('init game controllers...')
pygame._sdl2.controller.init()
joymode = None

if not pygame._sdl2.controller.get_count():
    print('no controllers detected')
else:
    joymode = 'controller'
    print('found controllers:')
    for i in range(pygame._sdl2.controller.get_count()):
        joy = pygame._sdl2.controller.Controller(i)
        print(' - ' + joy.as_joystick().get_name())

if not joymode:    # use joystick lib as fallback
    pygame.joystick.init()
    if not pygame.joystick.get_count():
        print('no joystick detected')
    else:
        joymode = 'joystick'
        print('found joysticks:')
        for i in range(pygame.joystick.get_count()):
            joy = pygame.joystick.Joystick(i)
            joy.init()
            print(' - ' + joy.get_name())


GRID_HEIGHT = 40
GRID_WIDTH = 11

HEX_WIDTH = 24*1
HEX_HEIGHT = 24#28#27.7/4.0*1

PLAYER_COLORS = [(0, 255, 0),
                 (255, 0, 255),
                 (0, 128, 255),
                 (255, 255, 0)
                 ]

class Direction(Enum):  # currently unused
    RIGHT = 0
    LEFT = 1
    DOWN = 2
    UP = 3

playerKeys = [(pygame.K_RIGHT, pygame.K_LEFT, pygame.K_DOWN, pygame.K_UP),
              (pygame.K_d, pygame.K_a, pygame.K_s, pygame.K_w),
              ]


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
    if int(y) % 4 in (0, 3):
        px = x * HEX_WIDTH
        py = y * HEX_HEIGHT / 3.
    else:
        px = (x + 0.5) * HEX_WIDTH
        py = y * HEX_HEIGHT / 3.

    return px, py


grid = initGrid(GRID_WIDTH, GRID_HEIGHT)


class Player:
    def __init__(self, x, y, color=(255, 255, 255)):
        self.x = x
        self.y = y

        self.nextx = x
        self.nexty = y + 1

        self.dist = 0
        self.nextdir = 1        # for racecar steering only
        self.speed = 1.0 / 32

        self.idle = True

        self.racecar = False
        self.input_right_left_down_up = [False, False, False, False]
        self.target_right_left_down_up = [True, False, False, False]

        self.color = color


    def pressLeft(self):
        self.nextdir = -1
        self.input_right_left_down_up[1] = True
        self.idle = False

    def pressRight(self):
        self.nextdir = 1
        self.input_right_left_down_up[0] = True
        self.idle = False

    def pressUp(self):
        self.input_right_left_down_up[3] = True
        self.idle = False

    def pressDown(self):
        self.input_right_left_down_up[2] = True
        self.idle = False

    def pressDirection(self, d):
        (self.pressRight,
         self.pressLeft,
         self.pressDown,
         self.pressUp)[d]()


    def releaseLeft(self):
        self.input_right_left_down_up[1] = False

    def releaseRight(self):
        self.input_right_left_down_up[0] = False

    def releaseUp(self):
        self.input_right_left_down_up[3] = False

    def releaseDown(self):
        self.input_right_left_down_up[2] = False

    def releaseDirection(self, d):
        (self.releaseRight,
         self.releaseLeft,
         self.releaseDown,
         self.releaseUp)[d]()


    def turn(self):

        #x=0 : x=1   : x=2
        #    :       :
        #    : |     :
        #    :/ \    :/         y=0
        # \ /:    \ /:
        #  | :     | .          y=1
        #  | :     | .
        #  | :     |            y=2
        # / \:    / \
        #    :\ /               y=3
        #    : |

        line = self.nexty % 4   # y-line of target (=current) point

        setSegmentColor((self.x, self.y), (self.nextx, self.nexty), self.color)

        downwards = self.nexty - self.y > 0     # whether player came to current point by going down or not
        rightside = self.nextx == self.x        # whether player was traveling on the right half of the hexagon (including middle - see sketch)

        if not self.racecar:

            neighbours = [(self.nextx, self.nexty-1), (self.nextx, self.nexty+1)]
            if   line == 0: neighbours.append((self.nextx-1, self.nexty+1))
            elif line == 1: neighbours.append((self.nextx+1, self.nexty-1))
            elif line == 2: neighbours.append((self.nextx+1, self.nexty+1))
            else:           neighbours.append((self.nextx-1, self.nexty-1))
            neighbours.remove((self.x, self.y))

            nextxScreenCoord, nextyScreenCoord = getScreenCoords(self.nextx, self.nexty)
            i0_right = getScreenCoords(neighbours[0][0], neighbours[0][1])[0] > nextxScreenCoord
            i0_left  = getScreenCoords(neighbours[0][0], neighbours[0][1])[0] < nextxScreenCoord
            i0_down  = getScreenCoords(neighbours[0][0], neighbours[0][1])[1] > nextyScreenCoord
            i0_up    = getScreenCoords(neighbours[0][0], neighbours[0][1])[1] < nextyScreenCoord
            i1_right = getScreenCoords(neighbours[1][0], neighbours[1][1])[0] > nextxScreenCoord
            i1_left  = getScreenCoords(neighbours[1][0], neighbours[1][1])[0] < nextxScreenCoord
            i1_down  = getScreenCoords(neighbours[1][0], neighbours[1][1])[1] > nextyScreenCoord
            i1_up    = getScreenCoords(neighbours[1][0], neighbours[1][1])[1] < nextyScreenCoord

            i0_score = 0
            if self.target_right_left_down_up[0] and i0_right: i0_score += 1
            if self.target_right_left_down_up[1] and i0_left: i0_score += 1
            if self.target_right_left_down_up[2] and i0_down: i0_score += 1
            if self.target_right_left_down_up[3] and i0_up: i0_score += 1
            if self.target_right_left_down_up[0] and i0_left: i0_score -= 1
            if self.target_right_left_down_up[1] and i0_right: i0_score -= 1
            if self.target_right_left_down_up[2] and i0_up: i0_score -= 1
            if self.target_right_left_down_up[3] and i0_down: i0_score -= 1
            i1_score = 0
            if self.target_right_left_down_up[0] and i1_right: i1_score += 1
            if self.target_right_left_down_up[1] and i1_left: i1_score += 1
            if self.target_right_left_down_up[2] and i1_down: i1_score += 1
            if self.target_right_left_down_up[3] and i1_up: i1_score += 1
            if self.target_right_left_down_up[0] and i1_left: i1_score -= 1
            if self.target_right_left_down_up[1] and i1_right: i1_score -= 1
            if self.target_right_left_down_up[2] and i1_up: i1_score -= 1
            if self.target_right_left_down_up[3] and i1_down: i1_score -= 1
            neighbour_i = 0 if i0_score > i1_score else 1

            dirx = neighbours[neighbour_i][0] - self.nextx
            diry = neighbours[neighbour_i][1] - self.nexty

        else: # self.racecar

            if self.nextdir == -1:  # turn left
                if line == 0:
                    if downwards:
                        dirx = 0
                        diry = 1
                    else:
                        if rightside:
                            dirx = -1
                            diry = 1
                        else:
                            dirx = 0
                            diry = -1

                elif line == 1:
                    if downwards:
                        if rightside:
                            dirx = 1
                            diry = -1
                        else:
                            dirx = 0
                            diry = 1
                    else:
                        dirx = 0
                        diry = -1

                elif line == 2:
                    if downwards:
                        dirx = 1
                        diry = 1
                    else:
                        if rightside:
                            dirx = 0
                            diry = -1
                        else:
                            dirx = 0
                            diry = 1

                elif line == 3:
                    if downwards:
                        if rightside:
                            dirx = 0
                            diry = 1
                        else:
                            dirx = 0
                            diry = -1
                    else:
                        dirx = -1
                        diry = -1

            elif self.nextdir == 1: # turn right
                if line == 0:
                    if downwards:
                        dirx = -1
                        diry = 1
                    else:
                        if rightside:
                            dirx = 0
                            diry = -1
                        else:
                            dirx = 0
                            diry = 1

                elif line == 1:
                    if downwards:
                        if rightside:
                            dirx = 0
                            diry = 1
                        else:
                            dirx = 0
                            diry = -1
                    else:
                        dirx = 1
                        diry = -1

                elif line == 2:
                    if downwards:
                        dirx = 0
                        diry = 1
                    else:
                        if rightside:
                            dirx = 1
                            diry = 1
                        else:
                            dirx = 0
                            diry = -1

                elif line == 3:
                    if downwards:
                        if rightside:
                            dirx = -1
                            diry = -1
                        else:
                            dirx = 0
                            diry = 1
                    else:
                        dirx = 0
                        diry = -1

        self.x = self.nextx
        self.y = self.nexty

        self.nextx += dirx
        self.nexty += diry

        self.dist = 0

player1 = Player(4, 12, color=PLAYER_COLORS[0])
player2 = Player(GRID_WIDTH - 4, GRID_HEIGHT - 12, color=PLAYER_COLORS[1])

players = [player1, player2]


while running:
    output.fill((0, 0, 0))

    # draw grid

    for segment, color in grid.items():
        x1, y1, x2, y2 = segment

        x1, y1 = getScreenCoords(x1, y1)
        x2, y2 = getScreenCoords(x2, y2)

        pygame.draw.line(output, ledwall.brightness(color), (x1, y1), (x2, y2))



    # draw players

    for player in players:
        oldx, oldy = getScreenCoords(player.x, player.y)
        newx, newy = getScreenCoords(player.nextx, player.nexty)

        x = oldx + (newx - oldx) * player.dist
        y = oldy + (newy - oldy) * player.dist

        pygame.draw.ellipse(output, ledwall.brightness(player.color), rect=(x-2, y-2, 5, 5))

    # draw logo

    if tick % 32 < 24 and tick < 60 * 2:
        ledwall.centerText('HEXGRID', y=2, color=(0, 255, 0), fontsize=3)

    ledwall.compose(do_cls=False)


    # event handling

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

            else:
                for p, keys in enumerate(playerKeys):
                    for d, key in enumerate(keys):
                        if e.key == key:
                            players[p].pressDirection(d)

        elif e.type == pygame.KEYUP:
                for p, keys in enumerate(playerKeys):
                    for d, key in enumerate(keys):
                        if e.key == key:
                            players[p].releaseDirection(d)

        elif e.type == pygame.CONTROLLERAXISMOTION and joymode == 'controller':
            value = max(-1, e.value / 32767)
            p = e.instance_id

            if e.axis == pygame.CONTROLLER_AXIS_LEFTX:
                if value < 0:
                    if value < -DEADZONE:
                        players[p].pressLeft()
                    else:
                        players[p].releaseLeft()
                else:
                    if value > DEADZONE:
                        players[p].pressRight()
                    else:
                        players[p].releaseRight()
            elif e.axis == pygame.CONTROLLER_AXIS_LEFTY:
                if value < 0:
                    if value < -DEADZONE:
                        players[p].pressUp()
                    else:
                        players[p].releaseUp()
                else:
                    if value > DEADZONE:
                        players[p].pressDown()
                    else:
                        players[p].releaseDown()

        elif e.type == pygame.CONTROLLERBUTTONDOWN and joymode == 'controller':
            p = e.instance_id

            if e.button in (pygame.CONTROLLER_BUTTON_A, pygame.CONTROLLER_BUTTON_B, pygame.CONTROLLER_BUTTON_X, pygame.CONTROLLER_BUTTON_Y):
                pass

            elif e.button == pygame.CONTROLLER_BUTTON_DPAD_LEFT:
                players[p].pressLeft()
            elif e.button == pygame.CONTROLLER_BUTTON_DPAD_RIGHT:
                players[p].pressRight()
            elif e.button == pygame.CONTROLLER_BUTTON_DPAD_UP:
                players[p].pressUp()
            elif e.button == pygame.CONTROLLER_BUTTON_DPAD_DOWN:
                players[p].pressDown()

        elif e.type == pygame.CONTROLLERBUTTONUP and joymode == 'controller':
            p = e.instance_id

            if e.button == pygame.CONTROLLER_BUTTON_DPAD_LEFT:
                players[p].releaseLeft()
            elif e.button == pygame.CONTROLLER_BUTTON_DPAD_RIGHT:
                players[p].releaseRight()
            elif e.button == pygame.CONTROLLER_BUTTON_DPAD_UP:
                players[p].releaseUp()
            elif e.button == pygame.CONTROLLER_BUTTON_DPAD_DOWN:
                players[p].releaseDown()

    # update players

    for player in players:
        if True in player.input_right_left_down_up: player.target_right_left_down_up = list(player.input_right_left_down_up)

        if not player.idle:
            player.dist += player.speed
            if player.dist >= 1.0:
                player.turn()

    clock.tick(60)
    tick += 1

    if tick >= 60 * 4:
        ledwall.cls()

    #print('tick =', tick)

