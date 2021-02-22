import random
from threading import Thread

import keyboard

from state import State


class KBListener:

    def __init__(self, state: State):
        self.state = state
        self.last_presses = ["N/A"] * 2

        keyboard.on_press(self.on_press_key, suppress=True)

    def send_tic(self):
        if random.random() < self.state.tic_percent:
            send_string(f", {self.state.tic}")

    def on_press_key(self, event):
        self.last_presses.pop()
        self.last_presses.insert(0, event.name)

        print(self.state.active, self.state.ny_in_words, self.state.midsentence, self.state.tic,
              self.state.tic_percent, self.last_presses)

        send_even = True

        if self.state.active:
            if self.state.ny_in_words:
                if self.last_presses[1] in "nN":
                    if self.last_presses[0] in "aeiou":
                        send_string("y")
                    elif self.last_presses[0] in "AEIOU":
                        send_string("Y")
            if self.last_presses[1] in ",.:;?!" and (
                    self.last_presses[0] == "enter" or (self.state.midsentence and self.last_presses[0] == "space")):
                keyboard.send("left")
                self.send_tic()
                keyboard.send("right")
            elif self.last_presses[0] == "enter" and self.last_presses[1] != "ctrl":
                self.send_tic()
        if self.last_presses[0] == "enter" and self.last_presses[1] == "ctrl":
            send_even = False
            keyboard.release("ctrl")
            keyboard.send("enter")
            keyboard.press("ctrl")

        if send_even:
            send_event(event)

    @staticmethod
    def thread():
        return Thread(target=keyboard.wait, daemon=True)


def send_event(event):
    key = event.scan_code or event.name
    if event.name == "\x03":
        key = "scroll lock"
    elif event.name == "scroll lock":
        key = 70
    elif len(event.name) > 1:
        key = event.name
    keyboard.press(key) if event.event_type == keyboard.KEY_DOWN else keyboard.release(key)


def send_string(string):
    for i in string:
        keyboard.send(i)
