
import pygame
import random
import json
import os
import sys
import math

pygame.init()

# FULL SCREEN
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("FREE MAX")

clock = pygame.time.Clock()

# 16:9 virtual screen
W, H = 960, 540
game = pygame.Surface((W, H))

font = pygame.font.Font(None, 28)
big = pygame.font.Font(None, 65)

WHITE = (255,255,255)
BLACK = (15,15,25)
BLUE = (65,155,235)
GREEN = (30,180,70)
ORANGE = (255,130,0)
YELLOW = (255,220,0)
RED = (230,40,40)

# Hindi voice
def speak(text):
    try:
        from plyer import tts
        tts.speak(text)
    except:
        pass

# Sound
try:
    import array
    pygame.mixer.init(22050, -16, 1)

    def sound(freq):
        rate = 22050
        samples = array.array("h")
        for i in range(int(rate * .12)):
            v = int(4000 * math.sin(2*math.pi*freq*i/rate))
            samples.append(v)
        return pygame.mixer.Sound(buffer=samples)

    coin_sound = sound(950)
    jump_sound = sound(500)
    death_sound = sound(160)
except:
    coin_sound = None
    jump_sound = None
    death_sound = None

def play(s):
    if s:
        try:
            s.play()
        except:
            pass

# SAVE
SAVE = "free_max_save.json"

def load_level():
    try:
        with open(SAVE) as f:
            return max(1, min(100, json.load(f)["level"]))
    except:
        return 1

level = load_level()
score = 0

def save():
    try:
        with open(SAVE, "w") as f:
            json.dump({"level":level}, f)
    except:
        pass

# Dialogues
coins_dialogues = [
    "Mitron! Ek aur coin!",
    "Wah! Acche din aa gaye!",
    "Vikas ki raftaar tez hai!",
    "Shandaar! Kamaal ho gaya!",
    "Coin collection jaari hai!",
    "Are wah! Jackpot mitron!"
]

death_dialogues = [
    "Are mitron! Ye kya ho gaya!",
    "Aaj kismat saath nahi hai!",
    "Chalo bhai phir se koshish!",
    "Game mein bhi chunauti hai!",
    "Abki baar phir se prayas!"
]

win_dialogues = [
    "Mitron! Level jeet liya!",
    "Shandaar pradarshan!",
    "Wah! Kya baat hai!"
]

dialogue = "Namaste Mitron!"
dialogue_timer = 0

def new_dialogue(kind):
    global dialogue, dialogue_timer

    if kind == "coin":
        dialogue = random.choice(coins_dialogues)
    elif kind == "death":
        dialogue = random.choice(death_dialogues)
    else:
        dialogue = random.choice(win_dialogues)

    dialogue_timer = pygame.time.get_ticks() + 3000
    speak(dialogue)

# Player
player = pygame.Rect(60, 360, 36, 60)
vy = 0
gravity = .65
jump_power = -13
speed = 5
on_ground = False

# Level
platforms = []
coins = []
spikes = []
finish = pygame.Rect(900,350,35,80)

def create_level():
    global platforms, coins, spikes, player
    global vy, on_ground, finish

    platforms = [
        pygame.Rect(0,430,960,110),
        pygame.Rect(180,350,120,18),
        pygame.Rect(370,290,120,18),
        pygame.Rect(570,350,120,18),
        pygame.Rect(760,290,110,18)
    ]

    coins = []

    for i in range(5):
        x = 170 + i*145
        y = random.choice([390,310,250,340])
        coins.append(pygame.Rect(x,y,20,20))

    spikes = []

    for i in range(min(3+level//8,12)):
        x = random.randint(220,820)
        spikes.append(pygame.Rect(x,410,30,20))

    finish = pygame.Rect(900,350,35,80)
    player = pygame.Rect(60,365,36,60)
    vy = 0
    on_ground = False

def reset():
    global score, state
    score = 0
    state = "playing"
    create_level()

create_level()

state = "menu"

# Controls
left = pygame.Rect(25,440,90,80)
right = pygame.Rect(130,440,90,80)
jump = pygame.Rect(820,400,120,120)

# Pixel Modi-style hero
def draw_hero():
    x,y = player.x,player.y

    # Face
    pygame.draw.rect(game,(235,185,145),(x+7,y,25,23))
    # White hair
    pygame.draw.rect(game,WHITE,(x+7,y,25,7))
    # Beard
    pygame.draw.rect(game,WHITE,(x+10,y+17,20,10))
    # Eye
    pygame.draw.rect(game,BLACK,(x+25,y+10,3,3))
    # Orange jacket
    pygame.draw.rect(game,ORANGE,(x+4,y+25,29,25))
    # White kurta
    pygame.draw.rect(game,WHITE,(x+17,y+28,5,20))
    # Legs
    pygame.draw.rect(game,BLACK,(x+5,y+49,11,11))
    pygame.draw.rect(game,BLACK,(x+22,y+49,11,11))

def button(rect, label):
    pygame.draw.rect(game,BLACK,rect,border_radius=14)
    t = font.render(label,True,WHITE)
    game.blit(t,(rect.centerx-t.get_width()//2,
                 rect.centery-t.get_height()//2))

running = True

while running:
    clock.tick(50)

    sw,sh = screen.get_size()

    # Fill entire screen, preserving 16:9 proportions
    scale = min(sw/W,sh/H)
    dw,dh = int(W*scale),int(H*scale)
    ox,oy = (sw-dw)//2,(sh-dh)//2

    mx,my = pygame.mouse.get_pos()
    mx = (mx-ox)/scale
    my = (my-oy)/scale

    mouse = pygame.mouse.get_pressed()[0]
    keys = pygame.key.get_pressed()

    jump_pressed = False
    left_pressed = False
    right_pressed = False

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                running = False
            if e.key == pygame.K_SPACE:
                jump_pressed = True

        if e.type == pygame.MOUSEBUTTONDOWN:
            if state == "menu":
                reset()
            elif state == "dead":
                reset()
            elif state == "won":
                if level < 100:
                    level += 1
                    save()
                else:
                    level = 1
                    save()
                reset()

    if mouse:
        left_pressed = left.collidepoint(mx,my)
        right_pressed = right.collidepoint(mx,my)
        jump_pressed = jump_pressed or jump.collidepoint(mx,my)

    left_pressed = left_pressed or keys[pygame.K_LEFT]
    right_pressed = right_pressed or keys[pygame.K_RIGHT]
    jump_pressed = jump_pressed or keys[pygame.K_SPACE]

    game.fill(BLUE)

    # Clouds
    for x in [100,400,720]:
        pygame.draw.circle(game,WHITE,(x,75),22)
        pygame.draw.circle(game,WHITE,(x+25,75),17)

    pygame.draw.rect(game,GREEN,(0,430,W,110))

    if state == "menu":

        title = big.render("FREE MAX",True,YELLOW)
        game.blit(title,(350,150))

        game.blit(font.render(
            "MODI JI PIXEL ADVENTURE",True,WHITE
        ),(330,220))

        game.blit(big.render(
            "TAP TO PLAY",True,WHITE
        ),(345,300))

        draw_hero()

    elif state == "playing":

        if left_pressed:
            player.x -= speed
        if right_pressed:
            player.x += speed

        player.x = max(0,min(924,player.x))

        if jump_pressed and on_ground:
            vy = jump_power
            on_ground = False
            play(jump_sound)

        old_bottom = player.bottom
        vy += gravity
        player.y += int(vy)

        on_ground = False

        for p in platforms:
            if (
                vy >= 0
                and old_bottom <= p.top
                and player.bottom >= p.top
                and player.right > p.left
                and player.left < p.right
            ):
                player.bottom = p.top
                vy = 0
                on_ground = True

        for c in coins[:]:
            if player.colliderect(c):
                coins.remove(c)
                score += 10
                new_dialogue("coin")
                play(coin_sound)

        for s in spikes:
            if player.colliderect(s):
                state = "dead"
                new_dialogue("death")
                play(death_sound)

        if player.top > H:
            state = "dead"
            new_dialogue("death")
            play(death_sound)

        if player.colliderect(finish):
            state = "won"
            new_dialogue("win")

        for p in platforms:
            pygame.draw.rect(game,GREEN,p)

        for s in spikes:
            pygame.draw.polygon(game,RED,[
                (s.left,s.bottom),
                (s.centerx,s.top),
                (s.right,s.bottom)
            ])

        for c in coins:
            pygame.draw.circle(game,YELLOW,c.center,12)
            pygame.draw.circle(game,ORANGE,c.center,5)

        pygame.draw.rect(game,WHITE,
                         (finish.x,finish.y,5,80))
        pygame.draw.rect(game,YELLOW,
                         (finish.x+5,finish.y,35,22))

        draw_hero()

        game.blit(font.render(
            "FREE MAX  LEVEL "+str(level)+"/100",
            True,WHITE),(15,12))

        game.blit(font.render(
            "COINS: "+str(score),True,YELLOW
        ),(15,42))

        # Visible left/right buttons
        button(left,"LEFT")
        button(right,"RIGHT")

        # Jump control is invisible but active
        if pygame.time.get_ticks() < dialogue_timer:
            pygame.draw.rect(game,BLACK,(180,80,600,50),
                             border_radius=10)
            game.blit(font.render(
                dialogue,True,YELLOW
            ),(195,96))

    elif state == "dead":

        draw_hero()

        game.blit(big.render(
            "GAME OVER!",True,RED
        ),(330,160))

        game.blit(font.render(
            dialogue,True,YELLOW
        ),(260,240))

        game.blit(font.render(
            "TAP TO RESTART",True,WHITE
        ),(365,320))

    elif state == "won":

        game.blit(big.render(
            "LEVEL COMPLETE!",True,YELLOW
        ),(270,160))

        game.blit(font.render(
            dialogue,True,WHITE
        ),(300,240))

        game.blit(font.render(
            "LEVEL "+str(level)+"/100",True,WHITE
        ),(400,290))

        game.blit(font.render(
            "TAP FOR NEXT LEVEL",True,YELLOW
        ),(350,350))

    # Scale to screen
    screen.fill(BLACK)
    scaled = pygame.transform.scale(game,(dw,dh))
    screen.blit(scaled,(ox,oy))
    pygame.display.flip()

pygame.quit()
sys.exit()
