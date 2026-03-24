import pygame
import math
import ast
import colorsys

pygame.init()
screen = pygame.display.set_mode((900, 650))
WIDTH, HEIGHT = 900, 650
clock = pygame.time.Clock()
running = True
dt = 0
original_surface = pygame.Surface((WIDTH, HEIGHT))

fade_surface = pygame.Surface((900, 650))
fade_surface.fill((0, 0, 0)) # Background color
fade_surface.set_alpha(55)   # Lower = longer trail

tick1 = 0
speed = 3
ticks = 0

map = []
colors = []
type = []
speeds = []
player_pos = pygame.Vector2(450,550)
last_pos = []
complete = False
can_run = False
mainscreen = True
options = False
key_uped = True
hold = False
angle = 0
dragging = False
mover = False
vol = 100
sfx = 100

editor = False
saving = False
paint = False
s_types = ['box','duo','bg']
s_type = 'box'
bg_list = []
mouse_up = True
level = None
rand = True
mued = False
mup = True
plced = False
paused = False
pausUP = True
slider = 0
drag = -1
emode = 1
edit_map = []
sp_up = True
og_my = None
self2 = "#0400FF"
background_c = "#004A68"
lvl_color = "#BEBEBE"

for i in range(20):
    last_pos.append(player_pos)

levels = []

class CompactPicker:
    def __init__(self, x, y):
        # The main container (200x200)
        self.rect = pygame.Rect(x, y, 200, 200)
       
        # Sub-elements scaled to fit
        self.hue_rect = pygame.Rect(x + 10, y + 10, 180, 20)
        self.l_rect = pygame.Rect(x + 170, y + 40, 20, 120)
        self.preview_rect = pygame.Rect(x + 10, y + 40, 150, 120)
        self.copy_rect = pygame.Rect(x + 10, y + 165, 180, 25)
       
        self.hue = 0
        self.lightness = 50
        self.color = pygame.Color(255, 0, 0)
        self.hex_code = "#0400FF"
        self.font = pygame.font.SysFont("Arial", 14, bold=True)
       
        # Pre-render small Hue Bar
        self.hue_surf = pygame.Surface((180, 20))
        for i in range(180):
            c = pygame.Color(0)
            c.hsla = (i * 2, 100, 50, 100) # Map 180px to 360 degrees
            pygame.draw.line(self.hue_surf, c, (i, 0), (i, 20))




    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0]: # Left click held
            if self.hue_rect.collidepoint(mouse_pos):
                self.hue = (mouse_pos[0] - self.hue_rect.x)
            if self.l_rect.collidepoint(mouse_pos):
                rel_y = max(0, min(120, mouse_pos[1] - self.l_rect.y))
                self.lightness = 100 - (rel_y / 1.2) # Map 120px to 0-100
           
            # Update Hue (index * 2 because surface is 180px wide)
            self.color.hsla = (max(0, min(360, self.hue * 2)), 100, self.lightness, 100)
            self.hex_code = f"#{self.color.r:02x}{self.color.g:02x}{self.color.b:02x}".upper()




    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.copy_rect.collidepoint(event.pos):
                try:
                    pygame.scrap.put(pygame.SCRAP_TEXT, self.hex_code.encode())
                except:
                    pass




    def draw(self, surface):
        global self2
       
        # Main Panel
        pygame.draw.rect(surface, (30, 30, 30), self.rect, border_radius=5)
        pygame.draw.rect(surface, (80, 80, 80), self.rect, 1, border_radius=5)
       
        # 1. Hue Bar & Dot
        surface.blit(self.hue_surf, self.hue_rect)
        pygame.draw.rect(surface, (255, 255, 255), (self.hue_rect.x + self.hue - 2, self.hue_rect.y, 4, 20), 1)
       
        # 2. Lightness Bar & Dot
        l_surf = pygame.Surface((20, 120))
        for i in range(120):
            c = pygame.Color(0)
            c.hsla = (self.hue * 2, 100, 100 - (i / 1.2), 100)
            pygame.draw.line(l_surf, c, (0, i), (20, i))
        surface.blit(l_surf, self.l_rect)
        l_dot_y = self.l_rect.y + int((100 - self.lightness) * 1.2)
        pygame.draw.rect(surface, (255, 255, 255), (self.l_rect.x, l_dot_y - 2, 20, 4), 1)




        # 3. Preview Area
        pygame.draw.rect(surface, self.color, self.preview_rect)
       
        # 4. Copy Button/Text Area
        btn_col = (60, 60, 60) if not self.copy_rect.collidepoint(pygame.mouse.get_pos()) else (90, 90, 90)
        pygame.draw.rect(surface, btn_col, self.copy_rect, border_radius=3)
        txt = self.font.render(f"{self.hex_code}", True, (255, 255, 255))
        surface.blit(txt, (self.copy_rect.centerx - txt.get_width()//2, self.copy_rect.y + 5))


        self2 = self.hex_code

def add_point(x,y):
    global map, colors, type
    
    if len(map) == 0:
        map.insert(0,(x,y+tick1*-3))
        colors.insert(0,self2)
        type.insert(0,s_type)
        return
    map.append((450,1000000000000000000000000000))
    for i in range(len(map)):
        if map[i-1][1] < 550+tick1*-3:
            map.insert(i-1,(x,y+tick1*-3))
            colors.insert(i-1,self2)
            type.insert(i-1,s_type)
            del map[-1]
            return
    del map[-1]
    map.insert(len(map),(x,y+tick1*-3))
    colors.insert(len(map),self2)
    type.insert(len(map),s_type)
    
def dir_of_lin(x1,y1,x2,y2):
    dx = x2 - x1
    dy = y2 - y1
    return math.degrees(math.atan2(dy, dx))

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

def lighten_hex_color(hex_color, factor):
    """
    Makes a hex color brighter by a given factor.
    Factor > 1.0 makes it brighter. Factor < 1.0 makes it darker.
    """
    # 1. Convert hex to RGB (0-255 range)
    hex_color = hex_color.strip('#')
    if len(hex_color) != 6:
        raise ValueError("Invalid hex color format. Use '#RRGGBB' or 'RRGGBB'.")
        
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    # 2. Convert RGB (0-255) to HLS (0.0-1.0 range)
    # colorsys expects RGB values as floats between 0 and 1
    r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
    h, l, s = colorsys.rgb_to_hls(r_norm, g_norm, b_norm)

    # 3. Adjust the lightness ('l' parameter)
    l = min(1.0, l * factor)  # Ensure lightness doesn't exceed 1.0 (pure white)

    # 4. Convert HLS back to RGB (0.0-1.0 range)
    r_new_norm, g_new_norm, b_new_norm = colorsys.hls_to_rgb(h, l, s)

    # 5. Convert RGB (0.0-1.0) back to hex (0-255 range)
    r_new = int(min(255, max(0, r_new_norm * 255)))
    g_new = int(min(255, max(0, g_new_norm * 255)))
    b_new = int(min(255, max(0, b_new_norm * 255)))
    
    return f"#{r_new:02X}{g_new:02X}{b_new:02X}"

def load_speed():
    return (map[0][0]-player_pos.x)/((player_pos.y-(map[0][1]+(tick1*3)))/speed)

def draw_rect(x,y,w,h,r,c,t):

    original_image = pygame.Surface((w, h), pygame.SRCALPHA)
    original_image.fill(c)
    rect = original_image.get_rect(center=(x, y))
    angle = r

    rotated_image = pygame.transform.rotate(original_image, angle)
    rect = rotated_image.get_rect(center=rect.center)
    rotated_image.set_alpha(t)
    original_surface.blit(rotated_image, rect)

def draw_model(i):
    global background_c

    if type[i-1] == 'box':
        if emode == 3:
            draw_rect(map[i-1][0],map[i-1][1]+10+tick1*speed,50,50,0,darken_hex_color(colors[i-1],70),255)
            draw_rect(map[i-1][0],map[i-1][1]+5+tick1*speed,50,50,0,darken_hex_color(colors[i-1],70),255)
            draw_rect(map[i-1][0],map[i-1][1]+tick1*speed,50,50,0, colors[i-1],255)
        else:
            draw_rect(map[i-1][0],map[i-1][1]+10+tick1*speed,50,50,(tick1*2)%360,darken_hex_color(colors[i-1],70),255)
            draw_rect(map[i-1][0],map[i-1][1]+5+tick1*speed,50,50,(tick1*2)%360,darken_hex_color(colors[i-1],70),255)
            draw_rect(map[i-1][0],map[i-1][1]+tick1*speed,50,50,(tick1*2)%360, colors[i-1],255)
    elif type[i-1] == 'duo':
        if emode == 3:
            draw_rect(map[i-1][0],map[i-1][1]+10+tick1*speed,50,50,0,darken_hex_color(colors[i-1],70),100)
            draw_rect(map[i-1][0],map[i-1][1]+5+tick1*speed,50,50,0,darken_hex_color(colors[i-1],70),100)
            draw_rect(map[i-1][0],map[i-1][1]+tick1*speed,50,50,0, colors[i-1],100)
        else:
            draw_rect(map[i-1][0],map[i-1][1]+10+tick1*speed,50,50,(tick1*2)%360,darken_hex_color(colors[i-1],70),100)
            draw_rect(map[i-1][0],map[i-1][1]+5+tick1*speed,50,50,(tick1*2)%360,darken_hex_color(colors[i-1],70),100)
            draw_rect(map[i-1][0],map[i-1][1]+tick1*speed,50,50,(tick1*2)%360, colors[i-1],100)
    

def draw_things():
    global background_c, map

    background_c = "#004A68"
    for i in range(len(map),0,-1):
        draw_model(i)
        
    if not emode == 3:
        return
    
    for i in range(len(map)):
        if type[i-1] == 'bg':
            if not map[i-1][0] == 100:
                map[i-1] = (100,map[i-1][1])
            pygame.draw.line(original_surface,colors[i-1],(0,map[i-1][1]+10+tick1*speed),(900,map[i-1][1]+10+tick1*speed),2)
            pygame.draw.circle(original_surface,darken_hex_color(colors[i-1],25),(100,map[i-1][1]+10+tick1*speed),12)
            pygame.draw.circle(original_surface,colors[i-1],(100,map[i-1][1]+10+tick1*speed),10)
            if map[i-1][1]+10+tick1*speed > 550:
                background_c = colors[i-1]
        
def player_physics():
    global player_pos, last_pos, running, complete, can_run, key_uped, hold, angle, background_c, bg_list

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
        #pygame.draw.line(original_surface,"#414141",(last_pos[19-i][0],last_pos[19-i][1]+i*7),(last_pos[18-i][0],last_pos[18-i][1]+(i+1)*7),10)
        pygame.draw.line(original_surface,lighten_hex_color(background_c,(19-i)*0.15),(last_pos[19-i][0],last_pos[19-i][1]+i*7),(last_pos[18-i][0],last_pos[18-i][1]+(i+1)*7),10)
    pygame.draw.circle(original_surface,"white",player_pos,15)

    keys = pygame.key.get_pressed()

    if not keys[pygame.K_SPACE]:
        key_uped = True
        hold = False
    
    if keys[pygame.K_SPACE] and map[0][1]+tick1*speed > 500 and not complete and abs(map[0][0]-player_pos.x) < 30 and not hold:
        complete = True
        hold = True

    elif keys[pygame.K_SPACE] and not complete and key_uped:
        hold = True
    
    if bg_list[0][1] > 550:
        background_c = bg_list[0][0]
        del bg_list[0]
    
    #angle = speeds[0]*10

def maps_check():
    global speeds, map, colors, complete, running, can_run, key_uped, type
    if complete:
        if type[0] == 'box':
            del map[0]
            del type[0]
            del colors[0]
            complete = False
            speeds[0] = load_speed()
            key_uped = False
        elif type[0] == 'duo':
            type[0] = 'box'
            complete = False
            key_uped = False
    elif map[0][1]+tick1*speed > 600 or (abs(map[0][0]-player_pos.x) > 70 and map[0][1]+tick1*speed > 540):
        can_run = False

def draw_editor():
    global emode, keys, tick1, mued, mup, sp_up, colors, editor, mainscreen, can_run, saving, dtick, paint, mouse_up, s_type, plced
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_e] and emode == 3:
        if mued:
            pygame.mixer.music.stop()
            mued = False
            mup = False
        elif mup:
            emode = 1
            for i in range(30):
                original_surface.blit(fade_surface, (0, 0))
            print(map)
            print()
    elif keys[pygame.K_l] and emode == 3 and not mued:
        pygame.mixer.music.load(level+".mp3")
        pygame.mixer.music.play()
        pygame.mixer.music.set_pos(tick1/60)
        mued = True
    if mued:
        tick1 += 1
        if keys[pygame.K_SPACE] and sp_up:
            sp_up = False
            add_point(450,550)

        elif not keys[pygame.K_SPACE] and not sp_up:
            sp_up = True
    if mup == False and not keys[pygame.K_e]:
        mup = True
    


    mouse_x, mouse_y = pygame.mouse.get_pos()
    font = pygame.font.SysFont('Impact', 20)

    if not mued and keys[pygame.K_SPACE] and pygame.mouse.get_pressed()[0] and not plced:
        add_point(mouse_x,mouse_y)
        plced = True
    
    if not pygame.mouse.get_pressed()[0]:
        plced = False
        

    if emode == 1:
        draw_rect(450,325,900,650,0,"black",255)
        pygame.draw.rect(original_surface, "#FF3F3F",(20,20,50,50))
        text = font.render("Home", False, "#972525")
        text_rect = text.get_rect(center=(45,45))
        original_surface.blit(text, text_rect) 
        if (mouse_x > 20 and mouse_x < 70 and mouse_y > 20 and mouse_y < 70):
            draw_rect(45,45,50,50,0,"black",50)
            if pygame.mouse.get_pressed()[0]:
                mainscreen = True
                can_run = False
                editor = False

        pygame.draw.rect(original_surface, "#FFCC3F",(80,20,50,50))
        text = font.render("Edit", False, "#856A1F")
        text_rect = text.get_rect(center=(105,45))
        original_surface.blit(text, text_rect) 
        if (mouse_x > 80 and mouse_x < 130 and mouse_y > 20 and mouse_y < 70):
            draw_rect(105,45,50,50,0,"black",50)
            if pygame.mouse.get_pressed()[0] and not emode == 3:
                emode = 3
                tick1 = 0
    
    elif emode == 3:
        if saving:
            dtick += 1
        if saving and dtick > 50:
            saving = False
        font = pygame.font.SysFont('Georiga', 30)
        text = font.render("Editing... Press 'E' to exit.", False, "#FFFFFF")
        text_rect = text.get_rect(topleft=(20,20))
        original_surface.blit(text, text_rect)
        font = pygame.font.SysFont('Georiga', 20)
        text = font.render(str(tick1/60), False, "#FFFFFF")
        text_rect = text.get_rect(topleft=(20,50))
        original_surface.blit(text, text_rect)
        if paint:
            picker.update()
            picker.draw(original_surface)
        
        
        pygame.draw.rect(original_surface, "#3F42FF",(830,20,50,50))
        font = pygame.font.SysFont('Impact', 19)
        if saving:
            font = pygame.font.SysFont('Impact', 12)
            text = font.render("Saveing...", False, "#1E207A")
        else:
            text = font.render("Save", False, "#1E207A")
        text_rect = text.get_rect(center=(855,45))
        original_surface.blit(text, text_rect) 
        if (mouse_x > 830 and mouse_x < 880 and mouse_y > 20 and mouse_y < 70):
            draw_rect(855,45,50,50,0,"black",50)
            if pygame.mouse.get_pressed()[0] and not saving:
                saving = True
                dtick = 0
                save_edits()

        pygame.draw.rect(original_surface, "#FF0000",(830,140,50,50))
        font = pygame.font.SysFont('Impact', 19)
        text = font.render("Paint", False, "#790000")
        text_rect = text.get_rect(center=(855,165))
        original_surface.blit(text, text_rect)
        if (mouse_x > 830 and mouse_x < 880 and mouse_y > 140 and mouse_y < 190):
            draw_rect(855,165,50,50,0,"black",50)
            if pygame.mouse.get_pressed()[0]:
                if mouse_up:
                    if paint:
                        paint = False
                    else:
                        paint = True
                    mouse_up = False
        if not pygame.mouse.get_pressed()[0]:
            mouse_up = True
        
        pygame.draw.rect(original_surface, "#00FF95",(830,80,50,50))
        font = pygame.font.SysFont('Impact', 19)
        text = font.render(s_type, False, "#00683D")
        text_rect = text.get_rect(center=(855,105))
        original_surface.blit(text, text_rect)
        if (mouse_x > 830 and mouse_x < 880 and mouse_y > 80 and mouse_y < 130):
            draw_rect(855,105,50,50,0,"black",50)
            if pygame.mouse.get_pressed()[0]:
                if mouse_up:
                    mouse_up = False
                    s_type = s_types[(s_types.index(s_type)+1) % len(s_types)]

def save_edits():
    save_data(level,str(map),1)
    save_data(level,str(colors),2)
    save_data(level,str(type),3)

def check_click(mx,my):
    global map, drag, colors, mover, type

    
    keys = pygame.key.get_pressed()
    if dragging:
        mover = False
        return False
    if drag == -1:
        for i in range(len(map)):
            if mx > (map[i-1][0]-25) and mx < (map[i-1][0]+25) and my > (map[i-1][1]-25+tick1*3) and my < (map[i-1][1]+25+tick1*3) and pygame.mouse.get_pressed()[0]:
                if keys[pygame.K_BACKSPACE]:
                    del map[i-1]
                    del colors[i-1]
                    del type[i-1]
                    return False
                if paint:
                    colors[i-1] = self2
                if type[i-1] == 'bg':
                    map[i-1] = (map[i-1][0],my-(tick1*3))
                else:
                    map[i-1] = (mx,map[i-1][1])
                drag = i-1
                mover = True
                return True
        mover = False
        return False
    elif pygame.mouse.get_pressed()[0]:
        if type[drag] == 'bg':
            map[drag] = (map[drag][0],my-(tick1*3))
        else:
            map[drag] = (mx,map[drag][1])
        mover = True
        return True
    else:
        drag = -1
        mover = False
        return False

def save_data(id, text, x):

    with open("playerdata.txt", 'r') as file:
        lines = file.readlines()

    with open("playerdata.txt", "w+") as file:
        done = False
        for i in range(len(lines)):
            if not done and id+"\n" == lines[i-1]:
                if text == "~delete":
                    del lines[i-1]
                    del lines[i-1]
                    del lines[i-1]
                    del lines[i-1]
                    del lines[i-1]
                else:
                    lines[i-1+x] = text+"\n"
                done = True
                
        if not done and not text == "~delete":
            lines.append(id+"\n")
            lines.append(text+"\n")
            lines.append(text+"\n")
            lines.append(text+"\n")
            lines.append("\n")
        file.writelines(lines)

def load_data(id,x):

    with open("playerdata.txt", 'r') as file:
        lines = file.readlines()
    
    if id == "~all":
        for i in range(len(lines)):
            while "\n" in lines[i-1]:
                lines[i-1] = lines[i-1].replace("\n","")
        return lines
    else:
        if id+"\n" in lines:
            while "\n" in lines[lines.index(id+"\n")+x]:
                lines[lines.index(id+"\n")+x] = lines[lines.index(id+"\n")+x].replace("\n","")
            return lines[lines.index(id+"\n")+x]
        else:
            return ""

def start_game():
    global speeds, can_run, map, colors, type, player_pos, tick1, speed, dtick, mainscreen, bg_list, paused, pausUP

    can_run = True
    mainscreen = False
    paused = False
    pausUP = True
    dtick = 0
    tick1 = 0
    speed = 3
    bg_list = [("#004A68",200)]
    map = ast.literal_eval(load_data(level,1))
    colors = ast.literal_eval(load_data(level,2))
    type = ast.literal_eval(load_data(level,3))
    player_pos = pygame.Vector2(map[0][0], 550)
    for i in range(len(map)-len(colors)):
        colors.append(colors[len(colors)-1])
    for i in range(len(map)-len(type)):
        type.append(type[len(type)-1])
    for i in range(len(map)):
        if map[i-1] == 'bg':
            bg_list.append((colors[i-1],map[i-1][1]))
            del map[i-1]
            del type[i-1]
            del colors[i-1]
            i -= 1
    draw_rect(450,325,900,650,0,background_c,255)

    speeds = [0]
    speeds[0] = load_speed()

    if not editor:
        pygame.mixer.music.load(level+".mp3")
        pygame.mixer.music.play()


def draw_bar(x,y,l,w,p,c,c2):
    pygame.draw.line(original_surface,c,(x,y),(x+l,y),w)
    pygame.draw.line(original_surface,c2,(x+3,y),(x+l-3,y),w-4)
    if not p == 0:
        pygame.draw.line(original_surface,c,(x+6,y),(x+l-6-((l-12)-(l-12)*p),y),w-8)


def draw_mainscreen():
    global levels, mainscreen, level, editor, type, colors, map, can_run, lvl_color

    extra_y = 0
    levels = load_data("~all",0)
    pygame.draw.rect(original_surface, "#000000",(0,0,900,650))
    for i in range(int(len(levels)/6)):
        mouse_x,mouse_y = pygame.mouse.get_pos()
        if mouse_x > 150 and mouse_x < 750 and mouse_y > 50+i*100 and mouse_y < 50+i*100+80:
            extra_y = 10
            if pygame.mouse.get_pressed()[0]:
                level = levels[i*6-6]
                lvl_color = ast.literal_eval(levels[i*6-2])
                start_game()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_e] and keys[pygame.K_r]:
                level = levels[i*6-6]
                pygame.mixer.music.stop()
                map = ast.literal_eval(load_data(level,1))
                colors = ast.literal_eval(load_data(level,2))
                type = ast.literal_eval(load_data(level,3))
                for i in range(len(map)-len(colors)):
                    colors.append(colors[len(colors)-1])
                for i in range(len(map)-len(type)):
                    type.append(type[len(type)-1])
                mainscreen = False
                editor = True
                can_run = True
                return
        else:
            extra_y = 0
        pygame.draw.rect(original_surface, darken_hex_color(ast.literal_eval(levels[i*6-2])[1],50),(150,60+i*100,600,80))
        pygame.draw.rect(original_surface, ast.literal_eval(levels[i*6-2])[1],(150,50+i*100+extra_y,600,80))
        font = pygame.font.SysFont('Impact', 30)
        text = font.render(levels[i*6-6], False, ast.literal_eval(levels[i*6-2])[2])
        text_rect = text.get_rect(topleft=(160,60+i*100+extra_y))
        original_surface.blit(text, text_rect)
        draw_bar(160,110+i*100+extra_y,500,15,ast.literal_eval(levels[i*6-2])[0]/100,ast.literal_eval(levels[i*6-2])[2],ast.literal_eval(levels[i*6-2])[3])
        font = pygame.font.SysFont('Impact', 16)
        font.set_bold(True)
        text = font.render(str(ast.literal_eval(levels[i*6-2])[0])+"%", True, ast.literal_eval(levels[i*6-2])[3])
        text_rect = text.get_rect(topleft=(669,100+i*100+extra_y))
        original_surface.blit(text, text_rect)
        font = pygame.font.SysFont('Impact', 15)
        text = font.render(str(ast.literal_eval(levels[i*6-2])[0])+"%", False, ast.literal_eval(levels[i*6-2])[2])
        text_rect = text.get_rect(topleft=(670,100+i*100+extra_y))
        original_surface.blit(text, text_rect)

def draw_slider(x,y,l,v,m,id,ex):
    global slider

    pygame.draw.line(original_surface,lvl_color[2],(x-3,y),(x+l+3,y),14)
    pygame.draw.line(original_surface,lvl_color[3],(x,y),(x+l,y),10)
    pygame.draw.circle(original_surface,darken_hex_color(lvl_color[2],25),(x+v*(l/m),y),13)
    pygame.draw.circle(original_surface,lvl_color[2],(x+v*(l/m),y),10)
    font = pygame.font.SysFont('Impact', 16)
    font.set_bold(True)
    text = font.render(str(round(v))+ex, True, lvl_color[3])
    text_rect = text.get_rect(center=(x+l+30,y))
    original_surface.blit(text, text_rect)
    font = pygame.font.SysFont('Impact', 15)
    text = font.render(str(round(v))+ex, False, lvl_color[2])
    text_rect = text.get_rect(center=(x+l+30,y))
    original_surface.blit(text, text_rect)

    mouse_x, mouse_y = pygame.mouse.get_pos()
    if mouse_x > x+v*(l/m)-13 and mouse_x < x+v*(l/m)+13 and mouse_y > y-13 and mouse_y < y+13:
        if pygame.mouse.get_pressed()[0]:
            slider = id
    if slider == id and not pygame.mouse.get_pressed()[0]:
        slider = 0
    if slider == id:
        if mouse_x < x:
            return 0
        if mouse_x > x+l:
            return m
        return (mouse_x-x)/l*m
    return v
            


def draw_options():
    global paused, pausUP, mainscreen, editor, can_run, options, vol, sfx

    draw_rect(450,325,900,650,0,"black",50)
    draw_rect(450,325,460,335,0,darken_hex_color(lvl_color[1],50),255)
    draw_rect(450,325,450,325,0,lvl_color[1],255)
    font = pygame.font.SysFont('Impact', 40)
    text = font.render(level, False, lvl_color[2])
    text_rect = text.get_rect(center=(450,200))
    original_surface.blit(text, text_rect)

    draw_bar(300,240,300,15,lvl_color[0]/100,lvl_color[2],lvl_color[3])
    font = pygame.font.SysFont('Impact', 16)
    font.set_bold(True)
    text = font.render(str(lvl_color[0])+"%", True, lvl_color[3])
    text_rect = text.get_rect(topleft=(605,230))
    original_surface.blit(text, text_rect)
    font = pygame.font.SysFont('Impact', 15)
    text = font.render(str(lvl_color[0])+"%", False, lvl_color[2])
    text_rect = text.get_rect(topleft=(606,230))
    original_surface.blit(text, text_rect)

    if options:
        font = pygame.font.SysFont('Impact', 25)
        text = font.render("Volume", False, lvl_color[2])
        text_rect = text.get_rect(center=(450,280))
        original_surface.blit(text, text_rect)
        vol = draw_slider(350,310,200,vol,100,1,"%")

        text = font.render("SFX", False, lvl_color[2])
        text_rect = text.get_rect(center=(450,350))
        original_surface.blit(text, text_rect)
        sfx = draw_slider(350,380,200,sfx,100,2,"%")
        mouse_x, mouse_y = pygame.mouse.get_pos()
        draw_rect(450,445,150,50,0,darken_hex_color(lvl_color[1],50),255)
        draw_rect(450,445,140,40,0,darken_hex_color(lvl_color[1],30),255)
        text = font.render("Back", False, lvl_color[2])
        text_rect = text.get_rect(center=(450,445))
        original_surface.blit(text, text_rect)
        if mouse_x > 375 and mouse_x < 525 and mouse_y > 420 and mouse_y < 470:
            draw_rect(450,445,150,50,0,"black",70)
            if pygame.mouse.get_pressed()[0]:
                options = False


    else:
        font = pygame.font.SysFont('Impact', 35)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        draw_rect(350,325,190,60,0,darken_hex_color(lvl_color[1],50),255)
        draw_rect(550,325,190,60,0,darken_hex_color(lvl_color[1],50),255)
        draw_rect(350,325,180,50,0,darken_hex_color(lvl_color[1],30),255)
        draw_rect(550,325,180,50,0,darken_hex_color(lvl_color[1],30),255)
        text = font.render("Resume", False, darken_hex_color(lvl_color[1],60))
        text_rect = text.get_rect(center=(350,325))
        original_surface.blit(text, text_rect)
        text = font.render("Options", False, darken_hex_color(lvl_color[1],60))
        text_rect = text.get_rect(center=(550,325))
        original_surface.blit(text, text_rect)
        if mouse_x > 255 and mouse_x < 445 and mouse_y > 295 and mouse_y < 355:
            draw_rect(350,325,190,60,0,"black",70)
            if pygame.mouse.get_pressed()[0]:
                paused = False
                pausUP = False
        if mouse_x > 455 and mouse_x < 645 and mouse_y > 295 and mouse_y < 355:
            draw_rect(550,325,190,60,0,"black",70)
            if pygame.mouse.get_pressed()[0]:
                options = True

        draw_rect(350,395,190,60,0,darken_hex_color(lvl_color[1],50),255)
        draw_rect(550,395,190,60,0,darken_hex_color(lvl_color[1],50),255)
        draw_rect(350,395,180,50,0,darken_hex_color(lvl_color[1],30),255)
        draw_rect(550,395,180,50,0,darken_hex_color(lvl_color[1],30),255)
        text = font.render("Edit", False, darken_hex_color(lvl_color[1],60))
        text_rect = text.get_rect(center=(350,395))
        original_surface.blit(text, text_rect)
        text = font.render("Exit", False, darken_hex_color(lvl_color[1],60))
        text_rect = text.get_rect(center=(550,395))
        original_surface.blit(text, text_rect)
        if mouse_x > 255 and mouse_x < 445 and mouse_y > 365 and mouse_y < 425:
            draw_rect(350,395,190,60,0,"black",70)
            if pygame.mouse.get_pressed()[0]:
                pass
        if mouse_x > 455 and mouse_x < 645 and mouse_y > 365 and mouse_y < 425:
            draw_rect(550,395,190,60,0,"black",70)
            if pygame.mouse.get_pressed()[0]:
                paused = False
                pausUP = False
                mainscreen = True
                can_run = False
                editor = False




picker = CompactPicker(680, 195)


while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        picker.handle_event(event)

    if can_run:

        if not editor:
            pygame.mixer.music.set_volume(vol/100)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE] and pausUP:
                if paused == False:
                    paused = True
                else:
                    paused = False
                    options = False
                pausUP = False
            if not keys[pygame.K_ESCAPE]:
                pausUP = True
            
            if not paused:
                tick1 += 1
            #Semitransparent BG
            if complete:
                draw_rect(450,325,900,650,0,background_c,200)
            fade_surface.fill(background_c)
            original_surface.blit(fade_surface, (0, 0))
            #draw_rect(0,530,900,150,0,"black",105)

            if not paused:
                maps_check()
            draw_things()
            if not paused:
                player_physics()
            if paused:
                for i in range(20):
                    pygame.draw.line(original_surface,lighten_hex_color(background_c,(19-i)*0.15),(last_pos[19-i][0],last_pos[19-i][1]+i*7),(last_pos[18-i][0],last_pos[18-i][1]+(i+1)*7),10)
                pygame.draw.circle(original_surface,"white",player_pos,15)
                draw_options()
        else:
            if ticks % 35 == 0:
                draw_rect(450,325,900,650,0,background_c,200)
            draw_editor()
            
            if emode == 3:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                if not check_click(mouse_x,mouse_y) and not mover and pygame.mouse.get_pressed()[0] and og_my == None and not mued:
                    og_my = mouse_y
                    dragging = True
                if not pygame.mouse.get_pressed()[0]:
                    og_my = None
                    dragging = False
                
                if not og_my == None:
                    tick1 += (mouse_y-og_my)/3
                    og_my = mouse_y
                    if tick1 < 0:
                        tick1 = 0

    
                fade_surface.fill(background_c)
                original_surface.blit(fade_surface, (0, 0))
                #draw_rect(0,530,900,150,0,"black",105)
                draw_things()
                pygame.draw.circle(original_surface,"white",(450,550),15)

    else:
        if not editor and not mainscreen:
            if dtick == 0:
                pygame.mixer.music.stop()
                map = ast.literal_eval(load_data(level,1))
                colors = ast.literal_eval(load_data(level,2))
                type = ast.literal_eval(load_data(level,3))
                for i in range(len(map)-len(colors)):
                    colors.append(colors[len(colors)-1])
                for i in range(len(map)-len(type)):
                    type.append(type[len(type)-1])
            dtick += 1
            if dtick > 20:
                tick1 = tick1*0.98
                if ticks % 35 == 0:
                    draw_rect(450,325,900,650,0,background_c,200)
                original_surface.blit(fade_surface, (0, 0))
                #draw_rect(0,530,900,150,0,"black",105)
                draw_things()
                pygame.draw.circle(original_surface,"white",(450,550),15)
            if tick1 < 10 and dtick > 20:
                start_game()
        
        if mainscreen:
            draw_mainscreen()
    

    rotated_surface = pygame.transform.rotate(original_surface, angle)
    rotated_rect = rotated_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    
    screen.blit(rotated_surface, rotated_rect)

    pygame.display.flip()
    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000
    ticks += 1