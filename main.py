import pygame as pg
import numpy as np
import math
from colorsys import hls_to_rgb
from itertools import product
import pygame_widgets
from pygame_widgets.dropdown import Dropdown

#todo: większe okno z zachowaniem rozdzielczości
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

SPHERE_CENTER = [SCREEN_WIDTH/2, SCREEN_HEIGHT/2, SCREEN_WIDTH/2]
SPHERE_RADIUS = 100
LIGHT_SOURCE_POSITION = [400, 200, 0]
OBSERVER_POSITION = [200, 200, 0]

BALL_COLOR = 0.1
COLOR_SATURATION = 0.5

STEP = 50

#Phong Equation
Ia = 1      # natężenie światła w otoczeniu obiektu
Ip = .6      # natężenie światła punktowego

Ka = 0.4   # współczynnik odbicia światła otoczenia
Ks = 0.9     # współczynnik odbicia światła kierunkowego 
Kd = 0.9   # współczysnnik odbicia światła rozproszonego 

n = 27      # współczynnik gładkości powierzchni

def calc_light_intensity(point):
    N = versor(vector(SPHERE_CENTER, point))
    L = versor(vector(point, LIGHT_SOURCE_POSITION))
    V = versor(vector(point, OBSERVER_POSITION))
    R = versor(np.subtract(np.multiply(np.multiply(N, 2), np.multiply(N, L)), L))

    r = calc_light_source_distance(point) / 100
    f = f_att(r)

    I = Ia*Ka + Ip * f * Kd * max(np.dot(N,L), 0) + Ip * f * Ks * max(np.dot(R,V),0)**n
    
    return min(I, 1)

def versor(vector):
    n = math.sqrt(sum(e**2 for e in vector))
    return [e / n for e in vector]

def vector(start_point, end_point):
    return [end_point[0] - start_point[0], end_point[1] - start_point[1], end_point[2] - start_point[2]]

def calc_light_source_distance(point):
    x_diff = LIGHT_SOURCE_POSITION[0] - point[0]
    y_diff = LIGHT_SOURCE_POSITION[1] - point[1]
    z_diff = LIGHT_SOURCE_POSITION[2] - point[2]

    return math.sqrt((x_diff)**2 + (y_diff)**2 + (z_diff)**2)

def f_att(r):    # współczynnik tłumienia źródła z odległością
    C1 = 0.1
    C2 = 0.2
    C3 = 0.25

    return min(1/(C1 + C2*r +C3*r**2), 1)

def find_z_coordinate(x, y):
    b = -2 * SPHERE_CENTER[2]
    c = SPHERE_CENTER[2]**2 + (x - SPHERE_CENTER[0])**2 + (y - SPHERE_CENTER[1])**2 - SPHERE_RADIUS**2
    delta = b**2 - 4*c

    if delta == 0:
        return -b/2
    elif delta > 0:
        return min((math.sqrt(delta) - b)/2, (-math.sqrt(delta) - b)/2)
    
def draw():
    x_range = range(SCREEN_WIDTH)
    y_range = range(SCREEN_HEIGHT)

    for x, y in product(x_range, y_range):
        z = find_z_coordinate(x, y)

        if z:
            ilumination = calc_light_intensity([x, y, z])
            r, g, b = hls_to_rgb(BALL_COLOR, ilumination, COLOR_SATURATION)
            color = (255*r,255*g,255*b)

            screen.set_at((x, SCREEN_HEIGHT - y), color)

def check_for_light_in_sphere(x,y,z):
    r = math.sqrt((x-SPHERE_CENTER[0])**2 + (y-SPHERE_CENTER[1])**2 + (z-SPHERE_CENTER[2])**2)
    #print(r)
    return r > 100

def move(direction):
    match direction:
        case "up":
            if check_for_light_in_sphere(LIGHT_SOURCE_POSITION[0],LIGHT_SOURCE_POSITION[1]+STEP,LIGHT_SOURCE_POSITION[2]):
                LIGHT_SOURCE_POSITION[1] += STEP
        case "down":
            if check_for_light_in_sphere(LIGHT_SOURCE_POSITION[0],LIGHT_SOURCE_POSITION[1]-STEP,LIGHT_SOURCE_POSITION[2]):
                LIGHT_SOURCE_POSITION[1] -= STEP
        case "left":
            if check_for_light_in_sphere(LIGHT_SOURCE_POSITION[0]-STEP,LIGHT_SOURCE_POSITION[1],LIGHT_SOURCE_POSITION[2]):
                LIGHT_SOURCE_POSITION[0] -= STEP
        case "right":
            if check_for_light_in_sphere(LIGHT_SOURCE_POSITION[0]+STEP,LIGHT_SOURCE_POSITION[1],LIGHT_SOURCE_POSITION[2]):
                LIGHT_SOURCE_POSITION[0] += STEP
        case "forward":
            if check_for_light_in_sphere(LIGHT_SOURCE_POSITION[0],LIGHT_SOURCE_POSITION[1],LIGHT_SOURCE_POSITION[2]+STEP):
                LIGHT_SOURCE_POSITION[2] += STEP
        case "backward":
            if check_for_light_in_sphere(LIGHT_SOURCE_POSITION[0],LIGHT_SOURCE_POSITION[1],LIGHT_SOURCE_POSITION[2]-STEP):
                LIGHT_SOURCE_POSITION[2] -= STEP



pg.init()
screen = pg.display.set_mode(SCREEN_SIZE)
pg.display.set_caption("Phong Model")

default = (0.4, 0.9, 0.9) # Ka, Kd, Ks
chalk = (0.4, 0.3, 0.01)
wood = (0.8, 0.8, 0.3)

current = default

dropdown = Dropdown(
    screen, 10, 10, 100, 20, name='Select material',
    choices=[
        'Metal',
        'Chalk',
        'Wood'
    ],
    values=[default, chalk, wood]
)

run = True
draw()
while run:

    keys = pg.key.get_pressed()
    if keys[pg.K_w] == True:
        move("up")
        draw()

    if keys[pg.K_s] == True:
        move("down")
        draw()

    if keys[pg.K_a] == True:
        move("left")
        draw()

    if keys[pg.K_d] == True:    
        move("right")
        draw()

    if keys[pg.K_q] == True:
        move("backward")
        draw()
  
    if keys[pg.K_e] == True:
        move("forward")
        draw()
        
    material = dropdown.getSelected()

    if current != material and material != None:
        current = material
        Ka = current[0]
        Kd = current[1]
        Ks = current[2]
        screen.fill((0,0,0))
        draw()
        
    pg.display.flip()

    
    events = pg.event.get()
    for event in events:
        if event.type == pg.QUIT:
            pg.quit()
            run = False
            quit()
    pygame_widgets.update(events)