# Imports
import math
import random
import numpy
import pygame

# Simulation code heavily influenced by this part of this youtube video https://www.youtube.com/watch?v=PGk0rnyTa1U&t=308s


# Translate code from https://stackoverflow.com/questions/1969240/mapping-a-range-of-values-to-another
def translate(value, init_min, init_max, target_min, target_max):
    init_span = init_max - init_min
    target_span = target_max - target_min

    scaled_value = float(value - init_min) / float(init_span)

    return target_min + (scaled_value * target_span)


# Find the distance between two points
def dist(a, b):
    return math.sqrt(abs((a[0] - b[0]) ** 2) + abs((a[1] - b[1]) ** 2))


# Strings are connections between two points
class String:
    # Constructor
    def __init__(self, point_a, point_b):
        self.point_a = point_a
        self.point_b = point_b
        self.len = dist(point_a.pos, point_b.pos)

    # If the mouse is over the string, return true
    def hover(self, mouse):
        pos = mouse
        mouse_len = dist(pos, self.point_a.pos) + dist(pos, self.point_b.pos)
        distance = dist(self.point_a.pos, self.point_b.pos)

        return distance - 1 <= mouse_len <= distance + 1


# One point, a white circle
class Point:
    # Constructor
    def __init__(self, pos_):
        self.pos = pos_
        self.previous_pos = self.pos
        self.locked = False
        self.radius = 40

    # Check if the mouse is over the point, return true
    def hover(self, mouse):
        distance = dist(mouse, self.pos)
        return distance < self.radius/2


# Main class for rope simulation
class RopeSimulation:
    # Constructor for class
    def __init__(self, dis, width, height, gravity=5, num_iterations=10, keep_length=True, wind_strength=0):
        # "Public" variables/non-backend variables
        self.gravity = gravity
        self.num_iterations = num_iterations
        self.keep_length = keep_length
        self.wind_strength = wind_strength
        self.run = False
        self.dis = dis
        self.width = width
        self.height = height

        # Backend variables
        self.points = []
        self.strings = []
        self.a = None
        self.b = None
        self.wind = random.uniform(-1, 1)
        self.wind = -self.wind_strength if self.wind < 0 else self.wind_strength
        self.string_removed = False
        self.mouse_down = False

    # Shuffle the point and string arrays to avoid jittering
    def shuffle_arrays(self):
        random.shuffle(self.points)
        random.shuffle(self.strings)

    # Add a point at a given position
    def add_point(self, x, y):
        self.points.append(Point((x, y)))
        # Shuffle arrays
        self.shuffle_arrays()

    # Add a string between two points
    def add_string(self, point_a, point_b):
        # Make the length of the strings are not 0 (division by 0 errors)
        if dist(point_a.pos, point_b.pos) == 0:
            return
        self.strings.append(String(point_a, point_b))
        # Shuffle arrays
        self.shuffle_arrays()

    # Generate the cloth/lattice
    def generate_lattice(self):
        cols = self.width / 15
        rows = self.height / 10
        # Add a point in a grid pattern
        for j in range(8):
            for i in range(12):
                self.points.append(Point(((i + 1) * cols, (j + 1) * rows)))
        # Add the connections/strings
        counter = 0
        for i in range(len(self.points) - 1):
            if counter == 11:
                counter = 0
            else:
                self.strings.append(String(self.points[i], self.points[i + 1]))
                counter += 1
            if i < len(self.points) - 12:
                self.strings.append(String(self.points[i], self.points[i + 12]))
            if i == 0 or i == 3 or i == 6 or i == 9 or i == 11:
                self.points[i].locked = True
        # Shuffle arrays
        self.shuffle_arrays()

    # Handle mouse down inputs
    def handle_mouse_down(self, mouse_pos):
        # When the press the mouse down, if they pressed a point, set it to be the first connection of a string
        for point in self.points:
            if point.hover(mouse_pos):
                self.a = point
                return
        # If they press on a string, remove it
        for string in self.strings:
            if string.hover(mouse_pos):
                self.strings.pop(self.strings.index(string))
                self.string_removed = True
                return

    # Handle mouse up inputs
    def handle_mouse_up(self, mouse_pos):
        for point in self.points:
            # Check if they let go on a point
            if point.hover(mouse_pos):
                # If it's the same point that they pressed on, lock it/unlock it
                if self.a == point:
                    point.locked = not point.locked
                    self.a = None
                    return
                # If it's a different point than what they pressed on, make a string between the two points
                if self.a is not None and self.a != point:
                    self.b = point
                    self.add_string(self.a, self.b)
                    self.a = None
                    self.b = None
                    return

        # Add a point if they pressed somewhere random
        if not self.a and not self.string_removed:
            self.add_point(mouse_pos[0], mouse_pos[1])
            return

        # Reset the first and second points, and the string_removed variable
        self.a = None
        self.b = None
        self.string_removed = False

    # Key press events: when they press 'm' being/make a string
    def handle_key_press(self):
        for point in self.points:
            if point.hover(pygame.mouse.get_pos()):
                # Make the first part of the string if it's not already made
                if self.a is None:
                    self.a = point
                # Make the second part of the string if it's not already made
                elif self.b is None:
                    self.b = point
                # Make the string if a and b are both points
                if self.a is not None and self.b is not None:
                    self.add_string(self.a, self.b)
                    self.a = None
                    self.b = None
                    break

    # Handle all inputs
    def handle_events(self, event):
        # Key pressed inputs
        if event.type == pygame.KEYDOWN:
            # Start/stop the simulation
            if event.key == pygame.K_r:
                self.run = not self.run
            # Add a string if they press m
            if event.key == pygame.K_m:
                self.handle_key_press()

        # Mouse inputs
        # Mouse up input
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            self.handle_mouse_up(pos)
            self.mouse_down = False
        # Mouse down input
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            self.handle_mouse_down(pos)
            self.mouse_down = True

    # Simulate the game
    def simulate(self):
        # Only run it if the simulation should be running
        if not self.run:
            return

        # Simulate the points
        for point in self.points:
            # If it's not locked
            if not point.locked:
                # Previous position
                pos_before_update = point.pos
                # Move the point as much as it moved last time (physics)
                point.pos = numpy.add(point.pos, numpy.subtract(point.pos, point.previous_pos))
                # Add wind and gravity
                point.pos = (point.pos[0] + self.wind, point.pos[1] + self.gravity)
                # Set its previous position to the saved previous position
                point.previous_pos = pos_before_update
        # Do this x amount of times so that the string length should be very close to its desired length
        for i in range(self.num_iterations):
            # Go through every string
            for string in self.strings:
                # Find the center of it (taking the average of the two points)
                string_center = numpy.add(string.point_a.pos, string.point_b.pos)
                string_center = (string_center[0] / 2, string_center[1] / 2)

                # Get the normalized direction of the string
                # A - b gives direction
                string_dir = numpy.subtract(string.point_a.pos, string.point_b.pos)
                # This normalizes it (diving each component of it by the vector's length)
                string_dir_len = math.sqrt(string_dir[0]**2 + string_dir[1]**2)
                string_dir = (string_dir[0] / string_dir_len, string_dir[1] / string_dir_len)

                # Half of the string's length
                c = numpy.true_divide(numpy.multiply(string_dir, string.len), 2)

                # Positions for strings:
                # Add or subtract the string's center by half of the length of the string
                # This will make it so that both points are roughly the string's desired length apart
                a_pos = numpy.add(string_center, c)
                b_pos = numpy.subtract(string_center, c)

                # Get the new length of the string
                # length = numpy.subtract(string.point_a.pos, string.point_b.pos)
                # length = math.sqrt(length[0] ** 2 + length[1] ** 2)
                length = dist(string.point_a.pos, string.point_b.pos)

                # If that length is greater than the string's desired length or if the string should always try to keep its length (the variable)
                if length > string.len or self.keep_length:
                    # If the points are not locked, then set their positions
                    if not string.point_a.locked:
                        string.point_a.pos = a_pos
                    if not string.point_b.locked:
                        string.point_b.pos = b_pos

    # Display the game
    def display(self):
        # Draw the background
        pygame.draw.rect(self.dis, (75, 75, 75), ((0, 0), (self.width, self.height)))

        # Draw the strings
        for string in self.strings:
            pygame.draw.line(self.dis, (255, 255, 255), string.point_a.pos, string.point_b.pos, width=5)
        # Draw the points
        for point in self.points:
            # Default white color
            color = (255, 255, 255)
            # If the point is locked, make it red
            if point.locked:
                color = (255, 0, 0)
            # Draw circle
            pygame.draw.circle(self.dis, color, point.pos, 12)

        # Draw a temporary line to show what the new string would be
        if self.mouse_down:
            if self.a is not None and not self.a.hover(pygame.mouse.get_pos()):
                pygame.draw.line(self.dis, (255, 255, 255), self.a.pos, pygame.mouse.get_pos(), width=5)

        # Update the game
        pygame.display.update()
