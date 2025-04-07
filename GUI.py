import pygame
import threading
import math

class GUI:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.running = False

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
        self.size_factor = 1.0  # Default size factor
        self.refPos = (0, 0)  # Initialize reference position

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

                self.update_ref_pos(0, 0, self.size_factor)  # Update reference position based on input values
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
            self.curve_points_pos = []
            self.curve_points_neg = []
            self.last_a = a

            y_min = -abs(a)
            y_max = abs(a)
            num_points = 1000

            origin_x = self.posScreen.centerx
            origin_y = self.posScreen.centery
            graph_width = self.posScreen.width
            graph_height = self.posScreen.height

            for i in range(num_points):
                y = y_min + (y_max - y_min) * i / (num_points - 1)
                try:
                    x_squared = y**2 - (y**4) / (a**2)
                    if x_squared < 0:
                        continue

                    x = math.sqrt(x_squared)

                    py = origin_y + y * (graph_width / (y_max - y_min))
                    px_pos = origin_x - x * (graph_height / (y_max - y_min))
                    px_neg = origin_x + x * (graph_height / (y_max - y_min))

                    self.curve_points_pos.append((px_pos, py))
                    self.curve_points_neg.append((px_neg, py))
                except:
                    continue

        # Draw cached points every frame
        pygame.draw.lines(self.screen, self.blue, False, self.curve_points_pos, 2)
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