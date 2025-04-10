import pygame
import threading
import math
from RefGen import RefGen
import numpy as np

class GUI(threading.Thread):
    def __init__(self, width=800, height=600, refgen=None):
        pygame.init()
        self.width = width
        self.height = height
        self.running = False

        self.refgen = refgen  # Store the reference to refgen



        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("OmniBot GUI")

        # Set up colors and fonts
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.gray = (200, 200, 200)
        self.blue = (100, 100, 255)
        self.font = pygame.font.Font(None, 32)

        #Position-Screen attributes
        self.posScreen = pygame.Rect(5, 5, self.width*2/5-5, self.height*2/3-5)  # Example position for the rectangle
        self.curve_points_pos = []
        self.curve_points_neg = []
        self.last_a = None
        self.size_factor = 0.5  # Default size factor
        self.refPos = (0, 0)  # Initialize reference position


        self.refY = []

        self.refXpos = []
        self.refXneg = []

        #Variables-Screen attributes
        self.varScreen = pygame.Rect(5, self.height*2/3+5, self.width*2/5-5, self.height*1/3-10)  # Example position for the rectangle
        self.input_boxes = [
            {
        "label": "Size factor:",
        "rect": pygame.Rect(self.varScreen.left + 150, int(self.varScreen.top + self.varScreen.height/4 * 0 + 10), 140, 32),
        "color": self.white,
        "text": "0",
        "active": False
    },
    {
        "label": "X-position:",
        "rect": pygame.Rect(self.varScreen.left + 150, int(self.varScreen.top + self.varScreen.height/4 * 1 + 10), 140, 32),
        "color": self.white,
        "text": "0",
        "active": False
    },
    {
        "label": "Y-postion:",
        "rect": pygame.Rect(self.varScreen.left + 150, int(self.varScreen.top + self.varScreen.height/4 * 2 + 10), 140, 32),
        "color": self.white,
        "text": "0",
        "active": False
    },
    {
        "label": "Interval period:",
        "rect": pygame.Rect(self.varScreen.left + 150, int(self.varScreen.top + self.varScreen.height/4 * 3 + 10), 140, 32),
        "color": self.white,
        "text": "0",
        "active": False
    },
        ]

    def run(self):
        self.running = True
        while self.running:
            try:
                self.screen.fill(self.white)

                pygame.draw.rect(self.screen, self.gray, self.posScreen)  # Draw posScreen rectangle

                self.draw_cartesian_curve(self.size_factor)  # Draw the curve based on the size factor

                refvect = self.refgen.getRefPoints()  # Get reference points from Refgen

                self.update_ref_pos(refvect[0], refvect[1], self.size_factor)  # Update reference position based on input values
                pygame.draw.circle(self.screen, self.black, self.refPos, 5)  # Draw reference position

                pygame.draw.rect(self.screen, self.gray, self.varScreen)  # Draw varScreen rectangle

                #Draw input boxes
                for box in self.input_boxes:
                    # Draw label
                    label_surface = self.font.render(box["label"], True, self.black)
                    label_pos = (box["rect"].left - 10 - label_surface.get_width(), box["rect"].y + 5)
                    self.screen.blit(label_surface, label_pos)

                    # Draw input box
                    pygame.draw.rect(self.screen, box["color"], box["rect"], 2)

                    #Draw input text
                    text_surface = self.font.render(box["text"], True, box["color"])
                    text_rect = text_surface.get_rect(center=box["rect"].center)
                    self.screen.blit(text_surface, text_rect)

                pygame.display.flip() # Update the display
            except Exception as e:
                print(f"Error in run loop: {e}")
                self.running = False

        self.stop()

    def start(self):
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        return thread
    
    def get_inputs(self):
        """Returns a dictionary of label: value pairs (converted to float where possible)."""
        result = {}
        for box in self.input_boxes:
            label = box["label"]
            text = box["text"]
            try:
                value = float(text)
            except ValueError:
                value = text  # Return raw string if not a valid number
            result[label] = value
        return result
    
    def draw_cartesian_curve(self, a=1.0):
        if a == 0:
            return

        if a != self.last_a:
            self.curve_points_pos.clear()
            self.curve_points_neg.clear()
            self.last_a = a

            # Clear old ref points
            self.refXpos.clear()
            self.refXneg.clear()
            self.refY.clear()

            y_min = -abs(a)
            y_max = abs(a)
            num_raw_points = 1000

            raw_x_pos = []
            raw_x_neg = []
            raw_y = []

            for i in range(num_raw_points):
                y = y_min + (y_max - y_min) * i / (num_raw_points - 1)
                try:
                    x_squared = y**2 - (y**4) / (a**2)
                    if x_squared < 0:
                        continue
                    x = math.sqrt(x_squared)
                    raw_y.append(y)
                    raw_x_pos.append(x)
                    raw_x_neg.append(-x)
                except:
                    continue

            # Resample for equal speed
            def resample_curve(x_list, y_list, num_points=500):
                distances = [0]
                for i in range(1, len(x_list)):
                    dx = x_list[i] - x_list[i - 1]
                    dy = y_list[i] - y_list[i - 1]
                    dist = math.hypot(dx, dy)
                    distances.append(distances[-1] + dist)

                total_length = distances[-1]
                step = total_length / (num_points - 1)
                target_lengths = [i * step for i in range(num_points)]

                resampled_x, resampled_y = [], []
                j = 0
                for t_len in target_lengths:
                    while j < len(distances) - 1 and distances[j + 1] < t_len:
                        j += 1
                    ratio = (t_len - distances[j]) / (distances[j + 1] - distances[j])
                    x_interp = x_list[j] + ratio * (x_list[j + 1] - x_list[j])
                    y_interp = y_list[j] + ratio * (y_list[j + 1] - y_list[j])
                    resampled_x.append(x_interp)
                    resampled_y.append(y_interp)

                return resampled_x, resampled_y

            resXpos, resY = resample_curve(raw_x_pos, raw_y)
            resXneg, _ = resample_curve(raw_x_neg, raw_y)

            self.refXpos = resXpos
            self.refXneg = resXneg
            self.refY = resY

            # Convert to screen coords
            origin_x = self.posScreen.centerx
            origin_y = self.posScreen.centery
            scale_x = self.posScreen.width / (abs(a) * 2)  # x -> width
            scale_y = self.posScreen.height / (abs(a) * 2)  # y -> height

            for x, y in zip(resXpos, resY):
                px = origin_x + x * scale_x  # <-- changed sign to +
                py = origin_y - y * scale_y  # <-- also fixed y direction
                self.curve_points_pos.append((px, py))

            for x, y in zip(resXneg, resY):
                px = origin_x + x * scale_x  # this stays same if x is negative
                py = origin_y - y * scale_y
                self.curve_points_neg.append((px, py))

            # Send to RefGen: 4 segments for looping
            self.refgen.setRefPoints(self.refXpos, self.refXneg, self.refY)

        # Draw
        if len(self.curve_points_pos) > 1:
            pygame.draw.lines(self.screen, self.blue, False, self.curve_points_pos, 2)
        if len(self.curve_points_neg) > 1:
            pygame.draw.lines(self.screen, self.blue, False, self.curve_points_neg, 2)


    def update_ref_pos(self, x, y, size_factor):
        """Update reference position based on input values (x, y)."""
        reference_x = self.posScreen.centerx + x * (self.posScreen.width / (abs(size_factor) * 2))
        reference_y = self.posScreen.centery - y * (self.posScreen.height / (abs(size_factor) * 2))
        self.refPos = (int(reference_x), int(reference_y))  # Update reference position


            
    def stop(self):
        """Stops the GUI thread."""
        if self.running:  # Prevent multiple calls
            print("Stopping GUI...")

            self.running = False  # Set flag first

            # Fill screen with black to visually indicate shutdown
            self.screen.fill((0, 0, 0))
            pygame.display.flip()

            # Process any remaining events to avoid crashes
            pygame.event.clear()

            # Small delay to allow Pygame to process the shutdown
            pygame.time.delay(100)

            # Quit Pygame
            pygame.quit()
            print("GUI thread exited.")