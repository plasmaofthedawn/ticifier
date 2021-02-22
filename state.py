import os
import json

SETTINGS_FOLDER = os.path.join(os.getenv('APPDATA'), "ticifier")
SETTINGS_FILEPATH = os.path.join(SETTINGS_FOLDER, "config.json")


class State:

    def __init__(self, tic_percent: float, tic: str, ny_in_words: bool, midsentence: bool):

        self.tic_percent = tic_percent

        self.tic = tic
        self.ny_in_words = ny_in_words
        self.midsentence = midsentence

        self.active = True

    @staticmethod
    def defaults():
        return State(.6, "kuma", False, True)

    def to_dict(self):
        return {
            "tic_percent": self.tic_percent,
            "tic": self.tic,
            "ny_in_words": self.ny_in_words,
            "midsentence": self.midsentence
        }

    def menu_states(self):
        return {
            "Toggle": self.active,
            '"ny" in words': self.ny_in_words,
            "Midsentence": self.midsentence
        }

    @staticmethod
    def from_dict(dict_settings: dict):
        return State(dict_settings["tic_percent"], dict_settings["tic"],
                     dict_settings["ny_in_words"], dict_settings["midsentence"])

    @staticmethod
    def get_file(write=False):
        if not os.path.exists(SETTINGS_FOLDER):
            os.makedirs(SETTINGS_FOLDER)
        try:
            return open(SETTINGS_FILEPATH, "w" if write else "r")
        except FileNotFoundError:
            State.defaults().save()
            return open(SETTINGS_FILEPATH, "w" if write else "r")

    def save(self):
        json.dump(self.to_dict(), State.get_file(write=True))

    @staticmethod
    def load():
        return State.from_dict(json.load(State.get_file()))


if __name__ == '__main__':
    settings = State.load()  # defaults to default
    settings.tic = "poi"
    print(settings.to_dict())
    settings.save()

    settings2 = State.load()
    print(settings2.to_dict())
