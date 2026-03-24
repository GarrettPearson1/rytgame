import pygame
import os
import random

pygame.init()
screen = pygame.display.set_mode((900, 650))
WIDTH, HEIGHT = 900, 650
clock = pygame.time.Clock()
running = True
dt = 0

fade_surface = pygame.Surface((900, 650))
fade_surface.fill((0, 0, 0)) # Background color
fade_surface.set_alpha(55)   # Lower = longer trail

tick1 = 0
speed = 3

map = [(200,-100),(400,-500),(300,-600),(500,-700),(200,-750),(300,-800),(200,-850),(300,-900)]
colors = ["#0400FF","#0400FF","#7700FF","#CC00FF","#FF008C","#FF0000","#FF5100","#FFD900"]
speeds = []
player_pos = pygame.Vector2(450, 550)
last_pos = []
complete = False
can_run = True
key_uped = True
hold = False
for i in range(20):
    last_pos.append(player_pos)



def clamp(val, minimum=0, maximum=255):
    """Ensures a value stays within the 0-255 range."""
    if val < minimum:
        return minimum
    if val > maximum:
        return maximum
    return val

def darken_hex_color(hex_color, percentage):
    """
    Darkens a hex color by a specified percentage.
    
    Args:
        hex_color (str): The input color in '#RRGGBB' format.
        percentage (int): The percentage to darken (e.g., 70 for 70%).

    Returns:
        str: The darker color in '#RRGGBB' format.
    """
    # Remove the '#' if present
    hex_color = hex_color.strip('#')
    if len(hex_color) != 6:
        raise ValueError("Invalid hex color format. Use '#RRGGBB' or 'RRGGBB'.")

    # Calculate the scaling factor (1.0 for original, 0.0 for black)
    # To darken by 70%, the new color will be 30% (100% - 70%) of the original brightness.
    scale_factor = 1.0 - (percentage / 100.0)
    
    if scale_factor < 0:
        scale_factor = 0 # Ensure we don't go below black

    # Convert hex to RGB integers
    r = int(hex_color[:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:], 16)

    # Apply the scaling factor and clamp values
    r = clamp(int(r * scale_factor))
    g = clamp(int(g * scale_factor))
    b = clamp(int(b * scale_factor))

    # Convert RGB back to hex string and return
    return "#%02x%02x%02x" % (r, g, b)


def load_speeds():
    global speeds
    
    sim_tick = 0
    for i in range(len(map)):
        speeds.append((map[i][0]-player_pos.x)/((player_pos.y-(map[i][1]+(sim_tick*3)))/speed))
        sim_tick += (map[i][0]-player_pos.x)/(speeds[i])
        player_pos.x = map[i][0]+0
    player_pos.x = 450

load_speeds()

def load_speed():
    return (map[0][0]-player_pos.x)/((player_pos.y-(map[0][1]+(tick1*3)))/speed)

def draw_rect(x,y,w,h,r,c):

    original_image = pygame.Surface((w, h), pygame.SRCALPHA)
    original_image.fill(c)
    rect = original_image.get_rect(center=(x, y))
    angle = r

    rotated_image = pygame.transform.rotate(original_image, angle)
    rect = rotated_image.get_rect(center=rect.center)
    screen.blit(rotated_image, rect)

def draw_things():
    for i in range(len(map)):
        draw_rect(map[i-1][0],map[i-1][1]+10+tick1*speed,50,50,(tick1*2)%360,darken_hex_color(colors[i-1],70))
        draw_rect(map[i-1][0],map[i-1][1]+5+tick1*speed,50,50,(tick1*2)%360,darken_hex_color(colors[i-1],70))
        draw_rect(map[i-1][0],map[i-1][1]+tick1*speed,50,50,(tick1*2)%360, colors[i-1])
        
def player_physics():
    global player_pos, last_pos, running, complete, can_run, key_uped, hold

    if len(speeds) == 0:
        player_pos.x += 0
        can_run = False
        return
    else:
        player_pos.x += speeds[0]
    if tick1 % 1 == 0:
        last_pos.append((player_pos.x+0,player_pos.y+0))
    if len(last_pos) > 20:
        del last_pos[0]
    for i in range(20):
        pygame.draw.line(screen,"#414141",(last_pos[19-i][0],last_pos[19-i][1]+i*7),(last_pos[18-i][0],last_pos[18-i][1]+(i+1)*7),10)
    pygame.draw.circle(screen,"white",player_pos,15)

    keys = pygame.key.get_pressed()

    if not keys[pygame.K_SPACE]:
        key_uped = True
        hold = False
    
    if keys[pygame.K_SPACE] and map[0][1]+tick1*speed > 500 and not complete and abs(map[0][0]-player_pos.x) < 30 and not hold:
        complete = True
        hold = True
    elif keys[pygame.K_SPACE] and not complete and key_uped:
        hold = True

def maps_check():
    global speeds, map, colors, complete, running, can_run, key_uped
    if complete:
        del map[0]
        del speeds[0]
        del colors[0]
        complete = False
        speeds[0] = load_speed()
        key_uped = False
    elif map[0][1]+tick1*speed > 600 or (abs(map[0][0]-player_pos.x) > 50 and map[0][1]+tick1*speed > 540):
        can_run = False

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if can_run:
        tick1 += 1
    
        #Semitransparent BG
        screen.blit(fade_surface, (0, 0))
        pygame.draw.rect(screen,"black",(0,530,900,150))
    
        maps_check()
        draw_things()
        player_physics()

    

    pygame.display.flip()




    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000