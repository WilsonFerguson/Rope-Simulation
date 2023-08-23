import pygame
from RopeSimulationLibrary import translate


class Button:
    def __init__(self, pos, dimensions, text, alpha_max, text_color=(255, 255, 255), alpha=100, background_color=(0, 0, 0)):
        self.pos = pos
        self.dimensions = dimensions
        self.text = text
        self.text_color = text_color
        self.alpha = alpha
        self.alpha_max = alpha_max
        self.pressed = False
        self.background_color = background_color

    def display(self, font, dis):
        # Text alpha from https://stackoverflow.com/questions/20620109/how-to-render-transparent-text-with-alpha-channel-in-pygame
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_surf.set_alpha(translate(self.alpha, 0, self.alpha_max, 0, 255))
        # Center code from https://stackoverflow.com/questions/23982907/how-to-center-text-in-pygame
        text_rect = text_surf.get_rect(center=(self.pos[0] + self.dimensions[0] / 2, self.pos[1] + self.dimensions[1] / 2))
        dis.blit(text_surf, text_rect)

        # Rectangle alpha from https://stackoverflow.com/questions/6339057/draw-a-transparent-rectangles-and-polygons-in-pygame
        s = pygame.Surface(self.dimensions)
        s.set_alpha(self.alpha)
        s.fill(self.background_color)
        dis.blit(s, self.pos)

    def fade(self, fade_amount):
        # Update the alpha
        self.alpha += fade_amount
        # Constrain it to 0-alpha_max
        self.alpha = min(max(self.alpha, 0), self.alpha_max)
        return self.alpha == 0

    # Check if mouse is hovering over button
    def hover(self, mouse_pos):
        # Horizontal check
        if mouse_pos[0] < self.pos[0] or mouse_pos[0] > self.pos[0] + self.dimensions[0]: return False
        # Vertical check
        if mouse_pos[1] < self.pos[1] or mouse_pos[1] > self.pos[1] + self.dimensions[1]: return False
        # If it's in the box, return true
        return True
