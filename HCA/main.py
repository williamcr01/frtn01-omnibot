from omnibot.tcp import Connection
from time import time, sleep
import refgen
import regul

# Insert suitable IP-adress
HOST = "192.168.0.105"
PORT = 9998

with Connection(HOST, PORT) as bot:
        
        # Target speed for servos
        vset = 100
        
        # Record start time
        t0 = time()

        refgen = refgen.RefGen(bot)
        regul = regul.Regul(bot)

        regul.set_refgen(refgen)

        refgen.start()
        regul.start()

        # Go one way for 3 seconds
        while True:

            # set speeds
            #bot.set_speeds([vset,vset,vset])
            
            # print position
            print('x:'+str(bot.get_x()))
            print('y:'+str(bot.get_y()))
            print('theta:'+str(bot.get_theta()))

            sleep(1)
