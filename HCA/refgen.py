import threading
import time

class RefGen(threading.Thread):
    # RefGen för att röra sig i en rak linje
    # Måste ändras för att röra sig i en åtta tror jag
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.x_target = 0.0
        self.y_target = 0.0
        self.running = False
        self.x_ref = None
        self.y_ref = None
        self.h = 0.05 # Sampling time seconds

    def set_target(self, newXTarget, newYTarget):
        self.x_target = newXTarget
        self.y_target = newYTarget

    def get_ref(self):
        return self.x_ref, self.y_ref
    
    def set_running(self):
        self.running = not self.running

    def run(self):
        self.set_running()
        self.x_ref = self.bot.get_x()
        self.y_ref = self.bot.get_y()

        alpha = 0.1  # Smoothing factor: 0 = no movement, 1 = jump instantly

        while self.running:
            # Update reference
            self.x_ref += alpha * (self.x_target - self.x_ref)
            self.y_ref += alpha * (self.y_target - self.y_ref)  

            time.sleep(self.h)
