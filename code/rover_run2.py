from raspirobotboard import *
import pygame
import sys
from pygame.locals import *

FORWARD = 'Forward'
BACKWARD = 'Backward'
STOP = 'Stop'
RIGHT = 'Right'
LEFT = 'Left'

rr = RaspiRobot()

pygame.init()
screen = pygame.display.set_mode((640, 480))
font = pygame.font.SysFont("arial", 64)

pygame.display.set_caption('RaspiRobot')
pygame.mouse.set_visible(0)

dir_stop, dir_forward, dir_back, dir_left, dir_right = range(5)
bot_direction = dir_stop
status = STOP

# Functions we need:

# Move rover forward 
def rover_forw():
    rr.set_led1(True)
    rr.set_led2(True)
    rr.forward()

# Move rover backward
def rover_backw():
    rr.set_led1(True)
    rr.set_led2(True)
    rr.reverse()

# Stop rover
def rover_stop():
    rr.set_led1(False)
    rr.set_led2(False)
    rr.stop()

# Turn left
def rover_left():
    rr.set_led1(True)
    rr.set_led2(False)
    rr.left()

# Turn right
def rover_right():
    rr.set_led1(False)
    rr.set_led2(True)
    rr.right()

def update_distance():
    dist = get_range()
    if dist == 0:
        return
    message = 'Distance: ' + str(dist) + ' in'
    text_surface = font.render(message, True, (127, 127, 127))
    screen.fill((255, 255, 255))
    screen.blit(text_surface, (100, 100))
    
    w = screen.get_width() - 20
    proximity = ((100 - dist) / 100.0) * w
    if proximity < 0:
        proximity = 0
    pygame.draw.rect(screen, (0, 255, 0), Rect((10, 10),(w, 50)))    
    pygame.draw.rect(screen, (255, 0, 0), Rect((10, 10),(proximity, 50)))
    pygame.display.update()

def get_range():
    try:
        dist = rr.get_range_inch()
    except:
        dist = 0
    return dist

def collision_check():
    dist = get_range()
    if dist > 0 and dist < 10 and bot_direction == dir_forward:
        go_stop()

def go_stop():
    global bot_direction
    bot_direction = dir_stop
    rr.stop()
    rr.set_led1(False)
    rr.set_led2(False)
    
def go_forward():
    global bot_direction
    bot_direction = dir_forward
    rr.forward()
    rr.set_led1(True)
    rr.set_led2(True)

def go_back():
    global bot_direction
    bot_direction = dir_back
    rr.set_led1(True)
    rr.set_led2(True)
    rr.reverse()

def go_right():
    global bot_direction
    bot_direction = dir_right
    rr.set_led1(False)
    rr.set_led2(True)
    rr.right()

def go_left():
    global bot_direction
    bot_direction = dir_left
    rr.set_led1(True)
    rr.set_led2(False)
    rr.left()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_UP:
                go_forward()
                status = FORWARD
            elif event.key == K_DOWN:
                go_back()
                status = BACKWARD
            elif event.key == K_RIGHT:
                go_right()
                status = RIGHT
            elif event.key == K_LEFT:
                go_left()
                status = RIGHT
            elif event.key == K_SPACE:
                go_stop()
                status = STOP
        elif event.type == MOUSEBUTTONDOWN: # this works with a wireless mouse connected to Pi
            (button1, button2, button3) = pygame.mouse.get_pressed()
            if button1 and status == FORWARD:
                # this will never happen because STOP is set at MOUSEBUTTONUP
                status = STOP
                rover_stop()
            elif button1 and status == STOP:
                status = FORWARD
                rover_forw()
            elif button3 and status == BACKWARD:
                # this will never happen because STOP is set at MOUSEBUTTONUP
                status = STOP
                rover_stop()
            elif button3 and status == STOP:
                status = BACKWARD
                rover_backw()
            else:
                status = STOP
                rover_stop()
            print(status)
            print button1, button2, button3

        elif event.type == MOUSEBUTTONUP: # this works with a wireless mouse connected to Pi
            status = STOP
            rover_stop()
            print(status)

        elif event.type == MOUSEMOTION: # this works with a wireless mouse connected to Pi
            (button1, button2, button3) = pygame.mouse.get_pressed()
            if button1:
                if status != LEFT:
                    status = LEFT
                    rover_left()
                    print(status)
            elif button3:
                if status != RIGHT:
                    status = RIGHT
                    rover_right()
                    print(status)
            else:
                if status != STOP:
                    # buttons are up, so stop turning
                    status = STOP
                    rover_stop()
                    print(status)

    collision_check()
    update_distance()
    time.sleep(0.1)
