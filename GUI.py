import pygame
import threading
import math
from RefGen import RefGen
import numpy as np

class GUI(threading.Thread):
    def __init__(self, width=1300, height=750, refgen=None, pid=None):
        pygame.init()
        self.width = width
        self.height = height
        self.running = False
        self.enterPressed = True

        self.refgen = refgen  # Store the reference to refgen
        self.pid = pid  # Store the reference to pid



        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("OmniBot GUI")

        # Set up colors and fonts
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.gray = (200, 200, 200)
        self.blue = (100, 100, 255)
        self.red = (255, 0, 0)
        self.font = pygame.font.Font(None, 24)

        #Position-Screen attributes
        self.posScreen = pygame.Rect(5, 5, 500, 500)  # Example position for the rectangle
        self.curve_points_pos = []
        self.curve_points_neg = []
        self.size_factor = 0.5  # Default size factor
        self.refPos = (0, 0)  # Initialize reference position
        self.statePos = (0, 0)  # Initialize state position


        self.refY = []

        self.refXpos = []
        self.refXneg = []

        self.meters_to_pixels_x = self.posScreen.width  # 1 meter wide
        self.meters_to_pixels_y = self.posScreen.height  # 1 meter high§

        #Variables-Screen attributes
        self.varScreen = pygame.Rect(5, 500+10, 500, 250-15)  # Example position for the rectangle
        self.inputVector = [1,0,0,0.02]
        self.input_boxes = [
    {
        "label": "Size factor:",
        "rect": pygame.Rect(self.varScreen.left + 180, int(self.varScreen.top + self.varScreen.height/4 * 0 + 10), 140, 32),
        "color": self.white,
        "text": "1",
        "active": False
    },
    {
        "label": "X-origin offset:",
        "rect": pygame.Rect(self.varScreen.left + 180, int(self.varScreen.top + self.varScreen.height/4 * 1 + 10), 140, 32),
        "color": self.white,
        "text": "0",
        "active": False
    },
    {
        "label": "Y-origin offset:",
        "rect": pygame.Rect(self.varScreen.left + 180, int(self.varScreen.top + self.varScreen.height/4 * 2 + 10), 140, 32),
        "color": self.white,
        "text": "0",
        "active": False
    },
    {
        "label": "Interval period:",
        "rect": pygame.Rect(self.varScreen.left + 180, int(self.varScreen.top + self.varScreen.height/4 * 3 + 10), 140, 32),
        "color": self.white,
        "text": "0",
        "active": False
    },
]
        self.toggle_button = {
            "rect": pygame.Rect(self.varScreen.right - 100, self.varScreen.top + 20, 80, 40),
            "on": False,
            "color_on": (0, 200, 0),
            "color_off": (200, 0, 0),
            "label": "OFF",
        }

        self.restart_button = {
            "rect": pygame.Rect(self.varScreen.right - 100, self.varScreen.top + 80, 80, 40),
            "color": self.gray,
            "label": "Restart"
        }

        # Inits for ErrorGraph
        self.errorHistory = []
        self.errorHistoryMax = 300

    def run(self):
        self.running = True
        while self.running:
            try:
                self.screen.fill(self.white)

                pygame.draw.rect(self.screen, self.gray, self.posScreen)  # Draw posScreen rectangle

                self.draw_cartesian_curve(self.inputVector[0])  # Draw the curve based on the size factor

                refvect = self.refgen.getRefPoints()  # Get reference points from Refgen
                statevect = self.pid.getState()  # Get state from PID

                self.update_state_pos(statevect[0], statevect[1])  # Update state position based on input values
                pygame.draw.circle(self.screen, self.red, self.statePos, 5)  # Draw current position

                self.update_ref_pos(refvect[0], refvect[1])  # Update reference position based on input values
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

                
                # Draw toggle button
                toggle = self.toggle_button
                color = toggle["color_on"] if toggle["on"] else toggle["color_off"]
                pygame.draw.rect(self.screen, color, toggle["rect"])
                label = "ON" if toggle["on"] else "OFF"
                label_surface = self.font.render(label, True, self.white)
                label_rect = label_surface.get_rect(center=toggle["rect"].center)
                self.screen.blit(label_surface, label_rect)

                # Draw Restart button
                pygame.draw.rect(self.screen, self.restart_button["color"], self.restart_button["rect"])
                restart_label = self.font.render(self.restart_button["label"], True, self.black)
                label_rect = restart_label.get_rect(center=self.restart_button["rect"].center)
                self.screen.blit(restart_label, label_rect)

                self.draw_error_graph()  # Draw the error graph


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
        i = 0
        for box in self.input_boxes:
            text = box["text"]
            try:
                value = float(text)
            except ValueError:
                value = text  # Return raw string if not a valid number
            self.inputVector[i] = value
            i += 1
        self.enterPressed = True
        return self.inputVector
    
    def draw_cartesian_curve(self, a=1.0):
        if a == 0:
            return

        if self.enterPressed:
            self.curve_points_pos.clear()
            self.curve_points_neg.clear()

            self.enterPressed = False

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
                    raw_y.append(y + self.inputVector[2])
                    raw_x_pos.append(x + self.inputVector[1])
                    raw_x_neg.append(-x + self.inputVector[1])
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
            scale_x = self.meters_to_pixels_x / 2
            scale_y = self.meters_to_pixels_y / 2

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


    def update_ref_pos(self, x, y):
        origin_x = self.posScreen.centerx
        origin_y = self.posScreen.centery
        self.refPos = (
            int(origin_x + x * self.meters_to_pixels_x / 2),
            int(origin_y - y * self.meters_to_pixels_y / 2)
        )

    def update_state_pos(self, x, y):
        origin_x = self.posScreen.centerx
        origin_y = self.posScreen.centery
        self.statePos = (
            int(origin_x + x * self.meters_to_pixels_x / 2),
            int(origin_y - y * self.meters_to_pixels_y / 2)
        )

    def draw_error_graph(self):
        try:
            currentError = self.pid.getErrors()[0]
        except:
            currentError = 0

        self.errorHistory.append(currentError)
        if len(self.errorHistory) > self.errorHistoryMax:
            self.errorHistory.pop(0)

        # Dimensions and position
        padding = 20
        graph_x = self.posScreen.right + padding
        graph_y = self.posScreen.top
        graph_width = self.width - graph_x - padding
        graph_height = self.posScreen.height

        # Adjust resolution
        if self.errorHistoryMax != graph_width:
            self.errorHistoryMax = graph_width
            self.errorHistory = self.errorHistory[-graph_width:]

        # Draw background
        pygame.draw.rect(self.screen, self.gray, (graph_x, graph_y, graph_width, graph_height), border_radius=10)

        # Axis line at bottom (0 error)
        base_y = graph_y + graph_height
        pygame.draw.line(self.screen, (100, 100, 100), (graph_x, base_y), (graph_x + graph_width, base_y), 1)

        # Plot error line
        if len(self.errorHistory) > 1:
            max_display_error = 1.0  # Adjust if your error can exceed 1
            step_x = graph_width / len(self.errorHistory)
            points = []
            for i, err in enumerate(self.errorHistory):
                x = graph_x + int(i * step_x)
                # Scale to fit graph height (higher error = taller line)
                clamped_err = min(err, max_display_error)
                y = base_y - int(clamped_err / max_display_error * graph_height)
                points.append((x, y))
            pygame.draw.lines(self.screen, (255, 0, 0), False, points, 2)

        # Label
        label = self.font.render("X Error (0 to 1)", True, self.black)
        self.screen.blit(label, (graph_x + 10, graph_y + 10))
            
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