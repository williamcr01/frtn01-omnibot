from omnibot.tcp import Connection
from time import time, sleep

# Insert suitable IP-adress
HOST = "192.168.0.105"
PORT = 9998

with Connection(HOST, PORT) as bot:
        
        # Target speed for servos
        vset = 50
        
        # Record start time
        t0 = time()

        # Go one way for 3 seconds
        while True:

            # set speeds
            #bot.set_speeds([vset,vset,vset])
            
            # print position
            print('x:'+str(bot.get_x()))
            print('y:'+str(bot.get_y()))
            print('theta:'+str(bot.get_theta()))

            sleep(1)
