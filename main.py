import pygame
import time

from GUI import GUI

def handle_events(gui):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gui.stop()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_0:
                gui.stop()
        elif event.type == pygame.MOUSEBUTTONDOWN:
                    print("Mouse button clicked at", event.pos)  # Print the position where clicked

def main():
    gui = GUI()
    gui_thread = gui.start()

    while gui.running:
        handle_events(gui)
        time.sleep(0.01)  # Prevents CPU overload

    gui_thread.join()  # Wait for the GUI thread to finish

if __name__ == "__main__":
    main()
