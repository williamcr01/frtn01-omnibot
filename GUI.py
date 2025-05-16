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

        self.clock = pygame.time.Clock()



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
        self.xref_buffer, self.yref_buffer = [], []


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

                self.draw_refCurve()  # Draw the reference curve

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

            self.clock.tick(60)  # Limit to 60 FPS

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

    def draw_refCurve(self):
        self.xref_buffer, self.yref_buffer = self.refgen.getXYBuffer()
        # Convert to screen coords
        origin_x = self.posScreen.centerx
        origin_y = self.posScreen.centery
        scale_x = self.meters_to_pixels_x / 2
        scale_y = self.meters_to_pixels_y / 2
        for x, y in zip(self.xref_buffer, self.yref_buffer):
            px = origin_x + x * scale_x
            py = origin_y - y * scale_y
            self.curve_points_pos.append((px, py))

        # Draw
        if len(self.curve_points_pos) > 1:
            pygame.draw.lines(self.screen, self.blue, False, self.curve_points_pos, 2)

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

        # Trim history to the last 300 values
        if len(self.errorHistory) > self.errorHistoryMax:
            self.errorHistory = self.errorHistory[-self.errorHistoryMax:]

        # Draw background
        pygame.draw.rect(self.screen, self.gray, (graph_x, graph_y, graph_width, graph_height), border_radius=10)

        # Axis line at bottom (0 error)
        base_y = graph_y + graph_height
        pygame.draw.line(self.screen, (100, 100, 100), (graph_x, base_y), (graph_x + graph_width, base_y), 1)

        # === Y-Axis with ticks and labels ===
        num_ticks = 5
        for i in range(num_ticks + 1):
            error_value = i / num_ticks  # From 0.0 to 1.0
            y = graph_y + graph_height - int(error_value * graph_height)

            # Tick mark
            pygame.draw.line(self.screen, self.black, (graph_x - 5, y), (graph_x, y), 1)

            # Label
            label_surface = self.font.render(f"{error_value:.1f}", True, self.black)
            self.screen.blit(label_surface, (graph_x - 35, y - 6))

            # Optional grid line
            pygame.draw.line(self.screen, (220, 220, 220), (graph_x, y), (graph_x + graph_width, y), 1)

        # Plot error line
        if len(self.errorHistory) > 1:
            max_display_error = 1.0
            step_x = graph_width / len(self.errorHistory)
            points = []
            for i, err in enumerate(self.errorHistory):
                x = graph_x + int(i * step_x)
                clamped_err = min(err, max_display_error)
                y = base_y - int(clamped_err / max_display_error * graph_height)
                points.append((x, y))
            pygame.draw.lines(self.screen, (255, 0, 0), False, points, 2)

        # Label for axis
        label = self.font.render("X Error (0 to 1)", True, self.black)
        self.screen.blit(label, (graph_x + 10, graph_y + 10))

        # === Show average error after each full loop ===
        try:
            avg_error = self.pid.getAverageError()
            avg_x_error = self.pid.getAverageXError()
            avg_y_error = self.pid.getAverageYError()

            avg_label = self.font.render(f"Avg Dist Error: {avg_error:.3f}", True, self.black)
            self.screen.blit(avg_label, (graph_x + 10, graph_y + graph_height + 10))

            avg_x_label = self.font.render(f"Avg X Error: {avg_x_error:.3f}", True, self.black)
            self.screen.blit(avg_x_label, (graph_x + 10, graph_y + graph_height + 30))

            avg_y_label = self.font.render(f"Avg Y Error: {avg_y_error:.3f}", True, self.black)
            self.screen.blit(avg_y_label, (graph_x + 10, graph_y + graph_height + 50))
        except AttributeError:
            pass

            
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