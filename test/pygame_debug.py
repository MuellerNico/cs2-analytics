import pygame
import pygame_gui

# Initialize pygame and pygame_gui
pygame.init()

# Set up the window
window_size = (800, 600)
screen = pygame.display.set_mode(window_size)
manager = pygame_gui.UIManager(window_size)

# Create a button as a simple UI component
button_rect = pygame.Rect((350, 275), (100, 50))
button = pygame_gui.elements.UIButton(relative_rect=button_rect, text='Test Button', manager=manager)

# Set up the clock
clock = pygame.time.Clock()

# Main loop
running = True
while running:
    time_delta = clock.tick(60)/1000.0  # 60 FPS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Pass events to pygame_gui
        manager.process_events(event)

    # Clear the screen
    screen.fill((0, 0, 0))

    # Update the UI manager
    manager.update(time_delta)

    # Draw the UI
    manager.draw_ui(screen)

    # Update the display
    pygame.display.update()

pygame.quit()
