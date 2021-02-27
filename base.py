import ctypes
import sys
import time
import tkinter as tk
import tkinter.simpledialog as sd
from os import path
from threading import Thread

from SysTrayMenu import SysTrayIcon
from kb import KBListener
from state import State

MessageBox = ctypes.windll.user32.MessageBoxW


class MenuTray:
    def __init__(self, state: State):
        self.show_tic_box = False
        self.show_chance_box = False

        self.state = state

        self.icon_path = get_path("icon.ico")
        self.disabled_icon_path = get_path("disabled.ico")

    def create_menu_options(self):
        def toggle_active(icon: SysTrayIcon):
            self.state.active = not self.state.active
            icon.icon = self.icon_path if self.state.active else self.disabled_icon_path
            icon.refresh_icon()

        def toggle_ny(_):
            self.state.ny_in_words = not self.state.ny_in_words
            self.state.save()

        def toggle_midsentence(_):
            self.state.midsentence = not self.state.midsentence
            self.state.save()

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
        print("Icon path:", self.icon_path)
        return Thread(target=SysTrayIcon,
                      args=(self.icon_path, "Ticifier v2.0", self.create_menu_options(), self.state))


def get_path(strpath: str):
    bundle_dir = getattr(sys, '_MEIPASS', path.abspath(path.dirname(__file__)))
    return path.abspath(path.join(bundle_dir, strpath))


active = True


def main():
    root = tk.Tk()
    root.withdraw()

    state = State.load()

    KBListener(state).thread().start()

    menu = MenuTray(state)
    (icon_thread := menu.thread()).start()

    root = tk.Tk()
    root.withdraw()

    print("Starting")

    while icon_thread.is_alive():

        time.sleep(.2)

        if menu.show_tic_box:
            old_active = state.active
            state.active = False
            a = sd.askstring("Input new tic", f"Input new tic. Current is {state.tic}.")
            if a and a != "":
                state.tic = a
                state.save()

                MessageBox(None, f"Tic has been updated to be {state.tic}.", 'Tic updated', 0)

            menu.show_tic_box = False
            state.active = old_active

        elif menu.show_chance_box:
            old_active = state.active
            state.active = False

            a = sd.askfloat("Input new chance",
                            f"Input new chance (0%-100%): Current is {round(state.tic_percent * 100, 2)}%")
            if a is not None and 0 <= a <= 100:
                state.tic_percent = a / 100

                MessageBox(None, f"Chance has been updated to be \"{a}%\".", "Chance updated", 0)

            menu.show_chance_box = False
            state.active = old_active


if __name__ == '__main__':
    main()
