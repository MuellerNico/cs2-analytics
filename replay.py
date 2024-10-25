from demoparser2 import DemoParser
import pandas as pd
import pygame
import pygame_gui
import sys

filename = "demos/natus-vincere-vs-mouz-m1-inferno.dem"
minimap_folder = "minimaps/"
parser = DemoParser(filename)

# demo header
header = parser.parse_header()
map_name = header["map_name"]

# query demo file
wanted_fields = ["X", "Y", "team_num", "team_name", "team_clan_name", "is_alive"]
df = parser.parse_ticks(wanted_fields) # get all game ticks
# print(df)
bbox = df["X"].min(), df["Y"].min(), df["X"].max(), df["Y"].max() # bounding box ToDo: proper map dimensions
team_names = df["team_clan_name"].unique()
round_start_ticks = parser.parse_event("round_start")["tick"]
freeze_end_ticks = parser.parse_event("round_freeze_end")["tick"]
num_rounds = len(round_start_ticks)
last_round = num_rounds - 1

# pygame init stuff
pygame.init()

# screen and UI
window_size = (800, 600)  # You can set this to any size you want)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Nico's 2D Replay: " + team_names[0] + " vs " + team_names[1])
manager = pygame_gui.UIManager(window_size)
# load radar minimap
minimap_path = minimap_folder + map_name + ".png" 
minimap = pygame.image.load(minimap_path)
minimap = pygame.transform.scale(minimap, window_size)

#speed_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((window_size[0]//2, window_size[1]-30), (30, 30)), manager=manager)
#speed_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((window_size[0]//2, window_size[1]-60), (100, 30)), text="Playback Speed", manager=manager)
#speed_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((window_size[0]//2-100, window_size[1]-30), (200, 20)), start_value=1, value_range=(0.5, 10), manager=manager)

# UI speed and round buttons
speed_up_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((window_size[0]//2+30, window_size[1]-30), (30, 30)),
                                                text='+',
                                                manager=manager)
speed_down_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((window_size[0]//2-30, window_size[1]-30), (30, 30)),
                                                text='-',
                                                manager=manager)
prev_round_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((window_size[0]//2-130, window_size[1]-30), (100, 30)),
                                                text='Prev Round',
                                                manager=manager)    
next_round_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((window_size[0]//2+60, window_size[1]-30), (100, 30)),
                                                text='Next Round',
                                                manager=manager)
# UI text fields
speed_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((window_size[0]//2, window_size[1]-30), (30, 30)), text="1x", manager=manager)
map_name_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0, window_size[1]-50), (80, 30)), text=map_name, manager=manager)
round_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0, window_size[1]-30), (100, 30)), text=f"Round 0 / {num_rounds}", manager=manager)

BLACK = (12,15,18)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
BROWN = (65,58,39)
RED = (128, 0, 0)
BLUE = (93,121,174)
ORANGE = (222,155,53)
BEIGE = (204,186,124)

DOT_SIZE = 5

FPS = 60
TICKRATE = 64
speed = 1
clock = pygame.time.Clock()

def draw_dot(screen, x, y, color=RED):
    pygame.draw.circle(screen, color, (x, y), DOT_SIZE)  # Drawing a red dot with radius 5

def draw_text(screen, x, y, text, color=WHITE, font_size=36):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def coords_to_screen(x, y):
    x = int((x - bbox[0]) / (bbox[2] - bbox[0]) * window_size[0])
    y = int((y - bbox[1]) / (bbox[3] - bbox[1]) * window_size[1])
    y = window_size[1] - y
    return x, y

running = True
paused = False
tick = 0
round = 0

while running:

    time_delta = clock.tick(FPS) / 1000.0
    
    if not paused: # advance tick
        tick += TICKRATE / FPS * speed
    if round != last_round and tick >= round_start_ticks[round+1]: # next round
        round += 1
    if round_start_ticks[round] <= tick < freeze_end_ticks[round]: # skip freeze time
        tick = freeze_end_ticks[round] 
    
    screen.fill(GRAY)
    screen.blit(minimap, (0, 0))
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:  # Quit on 'q'
                running = False
            if event.key == pygame.K_SPACE:  # Pause on 'space' 
                paused = not paused
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == speed_up_button:
                    speed *= 2
                    speed_text.set_text(f"{speed}x")
                if event.ui_element == speed_down_button:
                    speed /= 2
                    speed_text.set_text(f"{speed}x")
                if event.ui_element == prev_round_button:
                    round = max(0, round-1)
                    tick = round_start_ticks[round]
                if event.ui_element == next_round_button:
                    round = min(round+1, last_round)
                    tick = round_start_ticks[round]

        manager.process_events(event)

    # draw players and player names
    current_df = df[df["tick"] == int(tick)]
    for index, row in current_df.iterrows():
        x, y = coords_to_screen(row["X"], row["Y"])
        color = BLUE if row["team_name"] == "CT" else ORANGE
        color = RED if row["is_alive"] == 0 else color
        draw_dot(screen, x, y, color=color)
        draw_text(screen, x, y + 1.5 * DOT_SIZE, row["name"], color=WHITE, font_size=12)

    #draw_text(screen, 50, window_size[1] - 45, map_name, color=WHITE, font_size=24)
    #draw_text(screen, 50, window_size[1] - 15, f"round {round+1} / {num_rounds}", color=WHITE, font_size=24)
    #draw_text(screen, window_size[0]//2, window_size[1] - 60, f"Playback Speed: {speed}", color=WHITE, font_size=24)

    draw_text(screen, window_size[0] - 50, 15, f"{int(clock.get_fps())} FPS", color=WHITE, font_size=24)
    round_text.set_text(f"Round {round+1} / {num_rounds}") # round 0-based, but displayed 1-based

    # Update display
    manager.update(time_delta)
    manager.draw_ui(screen)
    pygame.display.update()

# Quit pygame
pygame.quit()
sys.exit()
