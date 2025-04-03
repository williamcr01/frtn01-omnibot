import pygame
import threading

class GUI:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.running = False

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("OmniBot GUI")
        self.white = (255, 255, 255)

    def run(self):
        self.running = True
        while self.running:
            try:
                self.screen.fill(self.white)

                pygame.display.flip() # Update the display
            except Exception as e:
                print(f"Error in run loop: {e}")
                self.running = False
        pygame.stop()

    def start(self):
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        return thread
            
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