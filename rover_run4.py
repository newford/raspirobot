from raspirobotboard import *
import pygame, random
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

def update_distance(status = STOP):
    dist = get_range()
    if dist == 0:
        return
    message = 'Distance: ' + str(dist) + ' cm'
    status_message = 'Status: ' + status
    text_surface = font.render(message, True, (127, 127, 127))
    status_surface = font.render(status_message, True, (127, 127, 127))
    screen.fill((255, 255, 255))
    screen.blit(text_surface, (100, 100))
    screen.blit(status_surface,(100, 250))
    
    w = screen.get_width() - 20
    proximity = ((100 - dist) / 100.0) * w
    if proximity < 0:
        proximity = 0
    pygame.draw.rect(screen, (0, 255, 0), Rect((10, 10),(w, 50)))    
    pygame.draw.rect(screen, (255, 0, 0), Rect((10, 10),(proximity, 50)))
    pygame.display.update()

def get_range():
    try:
        dist = rr.get_range_cm()
    except:
        dist = 0
    return dist

def collision_check(status):
    dist = get_range()
    if dist > 0 and dist < 25 and bot_direction == dir_forward:
        go_stop()
        status = STOP
    return status

def collision_avoid():
    # back off:
    backoff_time = 0.1
    rr.reverse(backoff_time)

    turn_time = 0.5    
    # choose random direction
    r1 = random.uniform(-1,1)
    if r1 < 0:
        # go_left
        dist = 0
        kkk = 0
        while dist < 25 and kkk < 10:
            kkk += 1
            rr.set_led1(True)
            rr.set_led2(False)
            rr.left(turn_time)
            time.sleep(0.05)
            dist = get_range()
    else:
        # go_right
        dist = 0
        kkk = 0
        while dist < 25 and kkk < 10:
            kkk += 1
            rr.set_led1(False)
            rr.set_led2(True)
            rr.right(turn_time)
            time.sleep(0.05)
            dist = get_range()
    return dist >= 25

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
                status = LEFT
            elif event.key == K_SPACE:
                go_stop()
                status = STOP
            elif event.key == K_ESCAPE:
                pygame.event.post(pygame.event.Event(QUIT))
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

    newstatus = collision_check(status)
    if status == FORWARD and newstatus == STOP:
        print('Collision avoidance')
        success = collision_avoid()
        if success:
            go_forward()
            print('Collision resolved!')
        else:
            status = STOP
            go_stop()
            print('Cannot resolve collision')
    update_distance(status)
    time.sleep(0.05)
