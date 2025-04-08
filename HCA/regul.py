import PI
import refgen
import threading

class Regul(threading.Thread):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.PI = PI.PI()
        self.refgen = refgen.RefGen(bot)
        self.refgen.running = True
        self.should_run = True

    def set_PI_param(self, params):
        self.PI.set_parameter(params)
    
    def get_PI_param(self):
        return PI.p

    def shutdown(self):
        self.should_run = False

    def limit(self, v, min=-10, max=10): # ändra dess till riktiga värden
        if v < min:
            v = min
        elif v > max:
            v = max
        return v
    
    def run(self):
        while self.should_run:
            pass

    def write_output(self, wheels):
        pass

    def read_input(self):
        return self.bot.get_x(), self.bot.get_y()