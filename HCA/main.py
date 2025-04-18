from omnibot.tcp import Connection
from time import time, sleep
import refgen as refgen_module
import regul as regul_module

# Insert suitable IP-adress
HOST = "192.168.0.105"
PORT = 9998

with Connection(HOST, PORT) as bot:
        
        # Target speed for servos
        vset = 100
        
        # Record start time
        t0 = time()

        refgen = refgen_module.RefGen()
        regul = regul_module.Regul(bot)
        
        refgen.set_ref(bot.get_x(), bot.get_y())
        regul.set_refgen(refgen)

        refgen.start()
        sleep(1)
        regul.start()
        sleep(1)

        print("threads started")

        #sleep(5)

        # Go one way for 3 seconds
        while True:
            print("connected")
            # set speeds
            #bot.set_speeds([vset,vset,vset])
            
            # print position
            #print('x:'+str(bot.get_x()))
            #print('y:'+str(bot.get_y()))
            #print('theta:'+str(bot.get_theta()))

            sleep(1)
