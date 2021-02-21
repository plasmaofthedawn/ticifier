from os import path
import random
import sys
import time
import tkinter as tk
import tkinter.simpledialog as sd
from threading import Thread

import keyboard

from SysTrayMenu import SysTrayIcon

tic_percent = .6
last_presses = ["N/A"] * 2

tic = "kuma"
ny_in_words = False
midsentence = True

active = True
stop = False


class MenuTray:
    def __init__(self):
        self.show_tic_box = False
        self.show_chance_box = False

    def create_menu_options(self):
        def toggle_active(icon: SysTrayIcon):
            global active
            active = not active
            icon.toggles["Active"] = active

        def toggle_ny(icon: SysTrayIcon):
            global ny_in_words
            ny_in_words = not ny_in_words
            icon.toggles['"ny" in words'] = ny_in_words

        def toggle_midsentence(icon: SysTrayIcon):
            global midsentence
            midsentence = not midsentence
            icon.toggles["Midsentence"] = midsentence

        def change_tic(_):
            self.show_tic_box = True

        def change_chance(_):
            self.show_chance_box = True

        return (("Toggle", None, toggle_active),
                ('"ny" in words', None, toggle_ny),
                ("Midsentence", None, toggle_midsentence),
                ("Change Tic", None, change_tic),
                ("Change Chance", None, change_chance))

    def thread(self):

        bundle_dir = getattr(sys, '_MEIPASS', path.abspath(path.dirname(__file__)))
        icon_path = path.abspath(path.join(bundle_dir, 'icon.ico'))
        print("Icon path:", icon_path)
        return Thread(target=SysTrayIcon, args=(icon_path, "Ticifier v2.0", self.create_menu_options()))


def main():
    global active, tic, tic_percent

    root = tk.Tk()
    root.withdraw()

    keyboard.on_press(on_press_key, suppress=True)

    kb_thread = Thread(target=keyboard.wait, daemon=True)
    kb_thread.start()

    menu = MenuTray()
    icon_thread = menu.thread()
    icon_thread.start()

    root = tk.Tk()
    root.withdraw()

    print("Starting")

    while icon_thread.is_alive():

        time.sleep(.2)

        if menu.show_tic_box:
            old_active = active
            active = False
            a = sd.askstring("Input new tic:", "Input new tic:")
            if a and a != "":
                tic = a
            menu.show_tic_box = False
            active = old_active
        elif menu.show_chance_box:
            old_active = active
            active = False

            a = sd.askfloat("Input new chance", "Input new chance (0-100)")
            if a is not None and 0 <= a <= 100:
                tic_percent = a / 100

            menu.show_chance_box = False
            active = old_active


def send_tic():
    if random.random() < tic_percent:
        send_string(f", {tic}")


def send_event(event):
    key = event.scan_code or event.name
    if len(event.name) > 1:
        key = event.name
    keyboard.press(key) if event.event_type == keyboard.KEY_DOWN else keyboard.release(key)


def send_string(string):
    for i in string:
        keyboard.send(i)


def on_press_key(event):
    last_presses.pop()
    last_presses.insert(0, event.name)

    print(active, ny_in_words, midsentence, tic, tic_percent, last_presses)

    send_even = True

    if active:
        if ny_in_words:
            if last_presses[1] in "nN":
                if last_presses[0] in "aeiou":
                    send_string("y")
                elif last_presses[0] in "AEIOU":
                    send_string("Y")
        if last_presses[1] in ",.:;?!" and (last_presses[0] == "enter" or (midsentence and last_presses[0] == "space")):
            keyboard.send("left")
            send_tic()
            keyboard.send("right")
        elif last_presses[0] == "enter" and last_presses[1] != "ctrl":
            send_tic()
    if last_presses[0] == "enter" and last_presses[1] == "ctrl":
        send_even = False
        keyboard.release("ctrl")
        keyboard.send("enter")
        keyboard.press("ctrl")

    if send_even:
        send_event(event)


if __name__ == '__main__':
    main()
