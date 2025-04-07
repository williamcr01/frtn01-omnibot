import pygame
import time

from GUI import GUI

def handle_events(gui):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gui.stop()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                gui.stop()
            for box in gui.input_boxes:
                            if box["active"]:
                                if event.key == pygame.K_RETURN:
                                    values = gui.get_inputs()
                                    print("All current values:", values)
                                elif event.key == pygame.K_BACKSPACE:
                                    box["text"] = box["text"][:-1]
                                elif event.unicode.isdigit() or event.unicode in ['.', '-', '+']:
                                    box["text"] += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN:
                        for box in gui.input_boxes:
                            if box["rect"].collidepoint(event.pos):
                                box["active"] = True

                                box["color"] = gui.blue
                            else:
                                box["active"] = False
                                box["color"] = gui.white

def main():
    gui = GUI()
    gui_thread = gui.start()

    while gui.running:
        handle_events(gui)
        time.sleep(0.01)  # Prevents CPU overload

    gui_thread.join()  # Wait for the GUI thread to finish

if __name__ == "__main__":
    main()
