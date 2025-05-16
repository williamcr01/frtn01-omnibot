import pygame
import time
import sys

from GUI import GUI
from RefGen_For_PID import RefGen
from PID import PID

def handle_events(gui,refgen,pid):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gui.stop()
            refgen.stop()
            pid.stop()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                gui.stop()
                refgen.stop()
                pid.stop()

            for box in gui.input_boxes:
                            if box["active"]:
                                if event.key == pygame.K_RETURN:
                                    values = gui.get_inputs()
                                    refgen.restart()
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
                        # Check if toggle button was clicked
                        if gui.toggle_button["rect"].collidepoint(event.pos):
                            gui.toggle_button["on"] = not gui.toggle_button["on"]
                            gui.toggle_button["label"] = "ON" if gui.toggle_button["on"] else "OFF"
                            refgen.OnOffInput()  # Call the OnOffInput method in RefGen

                        # Handle Restart button
                        if gui.restart_button["rect"].collidepoint(event.pos):
                            refgen.restart()

def main():
    
    refgen = RefGen()
    
    pid = PID(refgen=refgen)
    gui = GUI(refgen=refgen, pid=pid)
    
    refgen.start()
    pid.start()
    gui_thread = gui.start()
    


    while gui.running:
        handle_events(gui,refgen,pid)
        time.sleep(0.01)  # Prevents CPU overload

    gui_thread.join()  # Wait for the GUI thread to finish
    pid.join()  # Wait for the PID thread to finish
    refgen.join()  # Wait for the RefGen thread to finish
    sys.exit(0)  # Exit the program

if __name__ == "__main__":
    main()
