import pygame
import sys

# Initialize pygame
pygame.init()

# Load the image
image_path = "minimaps/de_inferno.png"  # Replace with your image path
bg_image = pygame.image.load(image_path)

# Set up the window size
window_size = (800, 600)  # You can set this to any size you want
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Image with Dot")

# Resize the image to fit the window
bg_image = pygame.transform.scale(bg_image, window_size)

# Set up colors
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# Set up FPS
FPS = 30
clock = pygame.time.Clock()

# Function to draw a dot at specified coordinates
def draw_dot(screen, x, y):
    pygame.draw.circle(screen, RED, (x, y), 5)  # Drawing a red dot with radius 5

# Main game loop
running = True
while running:
    # Draw the background image
    screen.blit(bg_image, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:  # Quit when 'q' is pressed
                running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button click
                x, y = pygame.mouse.get_pos()
                draw_dot(screen, x, y)

    # Update the display
    pygame.display.update()

    # Cap the frame rate
    clock.tick(FPS)

# Quit pygame
pygame.quit()
sys.exit()
