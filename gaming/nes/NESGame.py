from gaming.emulator import NES


class NESGame:

    def __init__(self, show_ui, interactive=False):
        self.emu = NES(self.game_path, self.savegame_path, show_ui, interactive)

    def press_key(self, key):
        self.emu.press_key(key)

    def reset(self):
        self.emu.reset()