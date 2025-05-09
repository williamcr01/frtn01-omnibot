from threading import Lock

mutex = Lock()


def bot_get_coord(bot):
    mutex.acquire()
    x = bot.get_x()
    y = bot.get_y()
    theta = bot.get_theta()
    mutex.release()
    return (x, y, theta)
