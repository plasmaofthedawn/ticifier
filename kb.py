import random
from threading import Thread

import keyboard

from state import State


class KBListener:

    def __init__(self, state: State):

        def set_ctrl_pressed(new):
            self.ctrl_pressed = new

        def set_shift_pressed(new):
            self.shift_pressed = new

        self.state = state
        self.last_presses = ["N/A"] * 2

        # need this because keyboard will send the wrong value when needed for some reason
        self.ctrl_pressed = keyboard.is_pressed("ctrl")
        self.shift_pressed = keyboard.is_pressed("shift")

        keyboard.on_release_key("ctrl", lambda _: set_ctrl_pressed(False))
        keyboard.on_release_key("shift", lambda _: set_shift_pressed(False))
        keyboard.on_press(self.on_press_key, suppress=True)

    def send_tic(self):
        if random.random() < self.state.tic_percent:
            old_shift = self.shift_pressed
            if old_shift:
                keyboard.release("shift")
            send_string(", ")
            if old_shift:
                keyboard.press("shift")
            send_string(self.state.tic)

    def on_press_key(self, event):
        self.last_presses.pop()
        self.last_presses.insert(0, event.name)

        print(self.state.active, self.state.ny_in_words, self.state.midsentence, self.state.tic,
              self.state.tic_percent, self.ctrl_pressed, self.last_presses)

        send_even = True

        if self.last_presses[0] == "ctrl":
            self.ctrl_pressed = True
        elif self.last_presses[0] == "shift":
            self.shift_pressed = True

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
        if self.last_presses[0] == "enter" and self.ctrl_pressed:
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
    # scroll lock fix
    if event.name == "\x03":
        key = "scroll lock"
    elif event.name == "scroll lock":
        key = 70
    # numpad fix
    elif 71 <= event.scan_code <= 82:
        key = event.name
    # windows key (and others) fix
    elif len(event.name) > 1:
        key = event.name
    keyboard.press(key) if event.event_type == keyboard.KEY_DOWN else keyboard.release(key)


def send_string(string):
    for i in string:
        keyboard.send(i)
