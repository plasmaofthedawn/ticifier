import random
from threading import Thread

import keyboard

from state import State

PUNCTUATION = ",.:;?!"


class UnpressCtrl:
    def __init__(self, key_states):
        self.key_states = key_states.copy()

    def __enter__(self):
        if self.key_states["left ctrl"]:
            keyboard.release("ctrl")
        if self.key_states["right ctrl"]:
            keyboard.release("right ctrl")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.key_states["left ctrl"]:
            keyboard.press("ctrl")
        if self.key_states["right ctrl"]:
            keyboard.press("right ctrl")


class UnpressShift:
    def __init__(self, key_states):
        self.key_states = key_states.copy()

    def __enter__(self):
        if self.key_states["left shift"]:
            keyboard.release("shift")
        if self.key_states["right shift"]:
            keyboard.release("right shift")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.key_states["left shift"]:
            keyboard.press("shift")
        if self.key_states["right shift"]:
            keyboard.press("right shift")


class KBListener:

    def __init__(self, state: State):

        self.state = state
        self.last_presses = ["N/A"] * 3

        # need this because keyboard will send the wrong value when needed for some reason
        self.key_states = {
            "left ctrl": False,
            "right ctrl": False,
            "left shift": False,
            "right shift": False
        }

        keyboard.on_release(self.on_release_key)
        keyboard.on_press(self.on_press_key, suppress=True)

    def send_tic(self):
        if random.random() < self.state.tic_percent:
            with UnpressShift(self.key_states):
                send_string(", ")

            send_string(self.state.tic)

    def on_release_key(self, event):

        if event.name == "ctrl":
            self.key_states["left ctrl"] = False
        elif event.name == "right ctrl":
            self.key_states["right ctrl"] = False
        elif event.name == "shift":
            self.key_states["left shift"] = False
        elif event.name == "right shift":
            self.key_states["right shift"] = False

    def on_press_key(self, event):
        self.last_presses.pop()
        self.last_presses.insert(0, event.name)

        print(self.state.active, self.state.ny_in_words, self.state.midsentence, self.state.tic,
              self.state.tic_percent, self.last_presses, self.key_states)

        send_even = True

        if event.name == "ctrl":
            self.key_states["left ctrl"] = True
        elif event.name == "right ctrl":
            self.key_states["right ctrl"] = True
        elif event.name == "shift":
            self.key_states["left shift"] = True
        elif event.name == "right shift":
            self.key_states["right shift"] = True

        if self.state.active:
            if self.state.ny_in_words:
                if self.last_presses[1] in "nN":
                    if self.last_presses[0] in "aeiou":
                        send_string("y")
                    elif self.last_presses[0] in "AEIOU":
                        send_string("Y")
            if self.last_presses[1] in PUNCTUATION and self.last_presses[2] not in PUNCTUATION and (
                    self.last_presses[0] == "enter" or (self.state.midsentence and self.last_presses[0] == "space")):
                with UnpressShift(self.key_states):
                    keyboard.send("left")

                self.send_tic()

                with UnpressShift(self.key_states):
                    keyboard.send("right")
            elif self.last_presses[0] == "enter" and not (self.key_states["left ctrl"] or self.key_states["right ctrl"]):
                self.send_tic()
        if self.last_presses[0] == "enter" and (self.key_states["left ctrl"] or self.key_states["right ctrl"]):
            send_even = False
            with UnpressCtrl(self.key_states):
                keyboard.send("enter")

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
