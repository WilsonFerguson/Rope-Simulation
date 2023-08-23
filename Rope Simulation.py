# Instructions for imports:
# Might have to: pip install ctypes
# pip install numpy (for the library)
# pip install pygame
# pip install pygame_widgets

# Classes were the extra feature I used (they are found in the Button.py and RopeSimulationLibrary.py files)

# Imports
from RopeSimulationLibrary import *
from Button import Button
import ctypes
import pygame_widgets
from pygame_widgets.slider import Slider

# Get the user's monitor's dimensions, only works for windows I believe, code from https://stackoverflow.com/questions/3129322/how-do-i-get-monitor-resolution-in-python
user32 = ctypes.windll.user32
width = user32.GetSystemMetrics(0)
height = user32.GetSystemMetrics(1)
# Use this code if you are on a mac and comment the previous code out:
width = 1920
height = 1080

# Create the pygame window and name it 'Rope Simulation'
pygame.init()
dis = pygame.display.set_mode((width, height), pygame.FULLSCREEN, vsync=1)
pygame.display.set_caption('Rope Simulation')

# FPS of the game
FPS = 60
clock = pygame.time.Clock()

# Create the rope simulation
# Parameters: Display, width, height, gravity, num iterations, keep length, wind speed
simulation = RopeSimulation(dis, width, height, 2, 10, True, 0)

title_screen = True

button_dimensions = (width / 8, height / 8)

pygame.font.init()

font = pygame.font.SysFont('calibri', 50)
title_font = pygame.font.SysFont('calibri', 100)


# Function to easily create buttons
def create_button(pos, text, text_color=(75, 75, 75), alpha=100, background_color=(0, 0, 0), alpha_max=100):
    pos = (pos[0] - button_dimensions[0] / 2, pos[1] - button_dimensions[1] / 2)
    return Button(pos, button_dimensions, text, alpha_max, text_color, alpha, background_color)


play_button = create_button((width/2, height/2), "Play")

gap = button_dimensions[0] / 4
custom_button = create_button((width/2 - button_dimensions[0] - gap, height/2), "Custom", alpha=0)
cloth_button = create_button((width/2 + button_dimensions[0] + gap, height/2), "Cloth", alpha=0)

fade_amount = 2

# Wind slider
slider = Slider(dis, int(width/2 - 400), int(height - height / 5), 800, 20, min=-0, max=99, step=0.1)


# Title screen
def manage_title_screen(mouse_pressed):
    global title_screen

    if play_button.pressed and not custom_button.pressed and not cloth_button.pressed:
        if play_button.alpha >= 0:
            play_button.fade(-fade_amount*2)
            custom_button.fade(fade_amount)
            cloth_button.fade(fade_amount)
    if custom_button.pressed or cloth_button.pressed:
        if custom_button.fade(-fade_amount*2) or cloth_button.fade(-fade_amount*2):
            title_screen = False
            return
    # Activate the presses
    if mouse_pressed:
        pos = pygame.mouse.get_pos()
        if not play_button.pressed:
            if play_button.hover(pos):
                play_button.pressed = True
        else:
            if not custom_button.pressed and not cloth_button.pressed:
                if custom_button.hover(pos):
                    custom_button.pressed = True
                elif cloth_button.hover(pos):
                    cloth_button.pressed = True
                    simulation.generate_lattice()

    # Draw the background
    pygame.draw.rect(dis, (75, 75, 75), ((0, 0), (width, height)))
    # Draw the buttons
    play_button.display(font, dis)
    custom_button.display(font, dis)
    cloth_button.display(font, dis)

    # Title text
    text_surf = title_font.render("Rope Simulation", True, (255, 255, 255))
    if custom_button.pressed or cloth_button.pressed: text_surf.set_alpha(translate(cloth_button.alpha, 0, cloth_button.alpha_max, 0, 255))
    # Center code from https://stackoverflow.com/questions/23982907/how-to-center-text-in-pygame
    text_rect = text_surf.get_rect(center=(width/2, height/5))
    dis.blit(text_surf, text_rect)

    # Draw slider and wind slider text
    text_surf = font.render("Wind slider: ", True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=(width/2, height - height / 4))
    dis.blit(text_surf, text_rect)
    slider.draw()

    # Update the display
    pygame.display.update()


# Infinite loop to run the game
while True:
    # Events
    mouse_pressed = False
    events = pygame.event.get()
    for event in events:
        # Escape to quit out of the game
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()
                break
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_pressed = True
        # Handle keyboard and mouse inputs
        if not title_screen: mouse_down = simulation.handle_events(event)

    # Slider events
    if title_screen:
        pygame_widgets.update(events)
        simulation.wind = translate(slider.getValue(), slider.min, slider.max, -2, 2)

    # Set FPS of the game
    clock.tick(FPS)

    # Title screen
    if title_screen:
        manage_title_screen(mouse_pressed)
        # Not fully working
        continue

    # Simulate the game
    simulation.simulate()

    # Display the game
    simulation.display()
