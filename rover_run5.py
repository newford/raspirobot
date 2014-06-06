from raspirobotboard import *
import pygame, random
import sys
from pygame.locals import *

FORWARD = 'Forward'
BACKWARD = 'Backward'
STOP = 'Stop'
RIGHT = 'Right'
LEFT = 'Left'
COLL_AVOID = 'Collision avoidance'

TIME_STEP = 0.1  # time between status updates

FULL_SPEED = 16
HALF_SPEED = 12
MIN_SPEED = 1
MAX_SPEED = 16
ZERO_SPEED = 0
START_SPEED = 6


rr = RaspiRobot()

# check if switch 1 closed: stop execution
if rr.sw1_closed():
    print('Switch 1 closed: quitting. Bye.')
    sys.exit()

pygame.init()
screen = pygame.display.set_mode((640, 480))
font = pygame.font.SysFont("arial", 64)

pygame.display.set_caption('RaspiRobot')
pygame.mouse.set_visible(0)

dir_stop, dir_forward, dir_back, dir_left, dir_right = range(5)
bot_direction = dir_stop
status = STOP
speed = 0
speed1 = 0  # left wheel, facing front (!)
speed2 = 0  # right wheel, facing front

# Functions we need:

def update_distance(status = STOP):
    dist = get_range()
    if dist == 0:
        return(dist)
    message = 'Distance: ' + str(dist) + ' cm'
    status_message = 'Status: ' + status
    text_surface = font.render(message, True, (150, 150, 150))
    status_surface = font.render(status_message, True, (150, 150, 150))
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
    return(dist)

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
        status = COLL_AVOID
    return status

def collision_avoid():
    # back off:
    backoff_time = 0.1
    rr.reverse(backoff_time)

    turn_time = 0.2
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

def go_forward_pwm(left_duty = 0, right_duty = 0):
    # left_duty range (0,16), 
    # right_duty range (0,16), 
    global bot_direction
    bot_direction = dir_forward
    # rr.forward()
    rr.set_led1(True)
    rr.set_led2(True)
    # rough pwm of left and right channels
    go = 1
    for j in range(1, 100):
        for i in range(0, 16):
          rr.set_motors((left_duty * go > i), 0, (right_duty * go > i), 0)
          if j == 199:
              print('Left: ' + str(left_duty * (left_duty * go > i)) + 'Right: ' + str(right_duty * (right_duty * go > i)))

def go_backward_pwm(left_duty = 0, right_duty = 0):
    # left_duty range (0,16), 
    # right_duty range (0,16), 
    global bot_direction
    bot_direction = dir_forward
    # rr.forward()
    rr.set_led1(True)
    rr.set_led2(True)
    # rough pwm of left and right channels
    go = 1
    for j in range(1, 100):
        for i in range(0, 16):
          rr.set_motors((left_duty * go > i), 1, (right_duty * go > i), 1)
          if j == 199:
              print('Left: ' + str(left_duty * (left_duty * go > i)) + 'Right: ' + str(right_duty * (right_duty * go > i)))

def go_left_pwm(left_duty = 0, alt_right_duty = 0):
    # left_duty range (0,16), 
    # right_duty range (0,16), 
    global bot_direction
    bot_direction = dir_forward
    right_duty = left_duty  # same speed on both wheels, but different directions
    rr.set_led1(True)
    rr.set_led2(False)
    # rough pwm of left and right channels
    go = 1
    for j in range(1, 100):
        for i in range(0, 16):
          rr.set_motors((left_duty * go > i), 1, (right_duty * go > i), 0)
          if j == 199:
              print('Left: ' + str(left_duty * (left_duty * go > i)) + 'Right: ' + str(right_duty * (right_duty * go > i)))

def go_right_pwm(left_duty = 0, alt_right_duty = 0):
    # left_duty range (0,16), 
    # right_duty range (0,16), 
    global bot_direction
    bot_direction = dir_forward
    right_duty = left_duty  # same speed on both wheels, but different directions
    rr.set_led1(False)
    rr.set_led2(True)
    # rough pwm of left and right channels
    go = 1
    for j in range(1, 100):
        for i in range(0, 16):
          rr.set_motors((left_duty * go > i), 0, (right_duty * go > i), 1)
          if j == 199:
              print('Left: ' + str(left_duty * (left_duty * go > i)) + 'Right: ' + str(right_duty * (right_duty * go > i)))

def  drive_on(status,hold_time = 0.1, speed1 = 0, speed2 = 0, dist):
    current_time = time.clock()
    new_time = current_time
    # TODO: fixme
    # use input dist to alter speed
    while new_time < current_time + hold_time:
        # must keep motors going
        if status == FORWARD:
            go_forward_pwm(speed1, speed2)
        elif status == BACKWARD:
            go_backward_pwm(speed1, speed2)
        elif status == LEFT:
            go_left_pwm(HALF_SPEED)
        elif status == RIGHT:
            go_right_pwm(HALF_SPEED)
        new_time = time.clock()


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

print('Welcome to Raspirobot!')
dist_meas = update_distance(status)

while True:
    key_action = False
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.display.quit()
            sys.exit()
        if event.type == KEYDOWN:
            key_action = True
            if event.key == K_UP:
                print('FORWARD. Speed = ' + str(speed) + 'status: ' + status)
                #go_forward()
                if status != FORWARD:
                    speed = 0
                speed = max(START_SPEED,min(speed + 2, MAX_SPEED))
                speed1 = speed
                speed2 = speed
                go_forward_pwm(speed1,speed2)
                status = FORWARD
            elif event.key == K_DOWN:
                print('BACKWARD. Speed = ' + str(speed) + 'status: ' + status)
                #go_back()
                if status != BACKWARD:
                    speed = 0
                speed = max(START_SPEED,min(speed + 2, MAX_SPEED))
                speed1 = speed
                speed2 = speed
                go_backward_pwm(speed1,speed2)
                status = BACKWARD
            elif event.key == K_RIGHT:
                print('RIGHT. Speed = ' + str(speed) + 'status: ' + status)
                go_right_pwm(HALF_SPEED)
                if status != RIGHT:
                    speed = 0
                speed = 0
                speed1 = 0
                speed2 = 0
                status = RIGHT
            elif event.key == K_LEFT:
                print('LEFT. Speed = ' + str(speed) + 'status: ' + status)
                go_left_pwm(HALF_SPEED)
                if status != LEFT:
                    speed = 0
                speed = 0
                speed1 = 0
                speed2 = 0
                status = LEFT
            elif event.key == K_SPACE:
                print('STOP. Speed = ' + str(speed) + 'status: ' + status)
                speed = 0
                speed1 = 0
                speed2 = 0
                go_stop()
                status = STOP
            elif event.key == K_ESCAPE:
                pygame.event.post(pygame.event.Event(QUIT))
            elif event.key == ord('a'):
                #go left
                print('Hold left, speed = ' + str(speed) + 'status: ' + status)
                speed = max(START_SPEED,speed)
                speed1 = speed
                speed2 = speed/2
                if status == FORWARD:
                    go_forward_pwm(speed1,speed2)
                if status == BACKWARD:
                    go_backward_pwm(speed1,speed2)
            elif event.key == ord('d'):
                #go right
                print('Turn right, speed = ' + str(speed) + 'status: ' + status)
                speed = max(START_SPEED,speed)
                speed1 = speed/2
                speed2 = speed
                if status == FORWARD:
                    go_forward_pwm(speed1,speed2)
                if status == BACKWARD:
                    go_backward_pwm(speed1,speed2)
                
        elif event.type == MOUSEBUTTONDOWN: # this works with a wireless mouse connected to Pi
            key_action = True
            (button1, button2, button3) = pygame.mouse.get_pressed()
            speed = 0
            speed1 = 0
            speed2 = 0
            if button1 and status == FORWARD:
                # this will never happen because STOP is set at MOUSEBUTTONUP
                status = STOP
                go_stop()
            elif button1 and status == STOP:
                status = FORWARD
                go_forward()
            elif button3 and status == BACKWARD:
                # this will never happen because STOP is set at MOUSEBUTTONUP
                status = STOP
                go_stop()
            elif button3 and status == STOP:
                status = BACKWARD
                go_back()
            else:
                status = STOP
                go_stop()
            print(status)
            print button1, button2, button3

        elif event.type == MOUSEBUTTONUP: # this works with a wireless mouse connected to Pi
            key_action = True
            status = STOP
            go_stop()
            speed = 0
            speed1 = 0
            speed2 = 0
            print(status)

        elif event.type == MOUSEMOTION: # this works with a wireless mouse connected to Pi
            key_action = True
            (button1, button2, button3) = pygame.mouse.get_pressed()
            speed = 0
            speed1 = 0
            speed2 = 0
            if button1:
                if status != LEFT:
                    status = LEFT
                    go_left()
                    print(status)
            elif button3:
                if status != RIGHT:
                    status = RIGHT
                    go_right()
                    print(status)
            else:
                if status != STOP:
                    # buttons are up, so stop turning
                    status = STOP
                    go_stop()
                    speed = 0
                    print(status)

    newstatus = collision_check(status)
    if newstatus == COLL_AVOID:
        print('Collision avoidance')
        if status != COLL_AVOID:
            prev_status = status;
            status = COLL_AVOID
            update_distance(status)
        success = collision_avoid()
        if success:
            status = prev_status   # reset status
            speed = START_SPEED
            speed1 = speed
            speed2 = speed
            go_forward_pwm(speed1,speed2)
            print('Collision resolved!')
        else:
            status = STOP
            speed = 0
            go_stop()
            print('Cannot resolve collision')
#    else:
#        if not(key_action):
#            # must keep motors going
#            if speed > 0 and speed < MAX_SPEED:
#                if status == FORWARD: 
#                    go_forward_pwm(speed1, speed2)
#                elif status == BACKWARD:
#                    go_backward_pwm(speed1, speed2)

    dist_meas_new = update_distance(status)
    if dist_meas_new > 0:
        dist_meas = dist_meas_new
    drive_on(status, TIME_STEP, speed1, speed2, dist_meas)
