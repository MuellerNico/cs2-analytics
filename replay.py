from demoparser2 import DemoParser
import pandas as pd
import pygame
import pygame_gui
import sys

filename = "demos/natus-vincere-vs-mouz-m1-inferno.dem"
image_folder = "minimaps/"
parser = DemoParser(filename)
tickrate = 64

header = parser.parse_header()
map_name = header["map_name"]

# map coordinates
wanted_fields = ["X", "Y", "team_num", "team_name", "team_clan_name", "is_alive"]
df = parser.parse_ticks(wanted_fields)
print(df)
bbox = df["X"].min(), df["Y"].min(), df["X"].max(), df["Y"].max()
team_names = df["team_clan_name"].unique()
ct_spawn = (2353, 2027) # inferno only
t_spawn = (-1586, 544)
round_start_ticks = parser.parse_event("round_start")["tick"]
freeze_end_ticks = parser.parse_event("round_freeze_end")["tick"]
num_rounds = len(round_start_ticks)
last_round = num_rounds - 1

# Initialize pygame
pygame.init()

# Load the image
image_path = image_folder + map_name + ".png"
bg_image = pygame.image.load(image_path)

# Set up the window size
window_size = (800, 600)  # You can set this to any size you want)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Nico's 2D Replay: " + team_names[0] + " vs " + team_names[1])

# pygame_gui manager
manager = pygame_gui.UIManager(window_size)
#hello_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (100, 50)),
#                                             text='Say Hello',
#                                             manager=manager)
# input field for speed
#speed_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((window_size[0]//2, window_size[1]-30), (30, 30)), manager=manager)
#speed_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((window_size[0]//2, window_size[1]-60), (100, 30)), text="Playback Speed", manager=manager)
# speed_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((window_size[0]//2-100, window_size[1]-30), (200, 20)), start_value=1, value_range=(0.5, 10), manager=manager)
# increase playback speed
speed_up_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((window_size[0]//2+30, window_size[1]-30), (30, 30)),
                                                text='+',
                                                manager=manager)
# decrease playback speed
speed_down_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((window_size[0]//2-30, window_size[1]-30), (30, 30)),
                                                text='-',
                                                manager=manager)
# current playback speed
speed_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((window_size[0]//2, window_size[1]-30), (30, 30)), text="1x", manager=manager)
# previous round
prev_round_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((window_size[0]//2-130, window_size[1]-30), (100, 30)),
                                                text='Prev Round',
                                                manager=manager)    
# next round
next_round_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((window_size[0]//2+60, window_size[1]-30), (100, 30)),
                                                text='Next Round',
                                                manager=manager)
# round number
map_name_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0, window_size[1]-50), (80, 30)), text=map_name, manager=manager)
round_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0, window_size[1]-30), (100, 30)), text=f"Round 0 / {num_rounds}", manager=manager)

# Resize the image to fit the window
bg_image = pygame.transform.scale(bg_image, window_size)

# Set up colors
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
speed = 1
clock = pygame.time.Clock()

# Function to draw a dot at specified coordinates
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

# Main game loop
running = True
paused = False
tick = 0
round = 0

while running:
    time_delta = clock.tick(FPS) / 1000.0
    
    if not paused: # advance tick
        tick += tickrate / FPS * speed
    if round != last_round and tick >= round_start_ticks[round+1]: # next round
        round += 1
    if round_start_ticks[round] <= tick < freeze_end_ticks[round]: # skip freeze time
        tick = freeze_end_ticks[round] 
    
    screen.fill(GRAY)
    screen.blit(bg_image, (0, 0))
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:  # Quit when 'q' is pressed
                running = False
            if event.key == pygame.K_SPACE:  # Pause when 'space' is pressed
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

    # draw players
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

    # Update the display
    manager.update(time_delta)
    manager.draw_ui(screen)
    pygame.display.update()

# Quit pygame
pygame.quit()
sys.exit()
