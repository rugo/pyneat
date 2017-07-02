import ctypes as ct
from gaming import lib_path
from os.path import join as join_path


class NES:
    # Taken from libretro.h
    KEY_B = 0
    KEY_SELECT = 2
    KEY_START = 3
    KEY_UP = 4
    KEY_DOWN = 5
    KEY_LEFT = 6
    KEY_RIGHT = 7
    KEY_A = 8
    KEYS = [
        KEY_B,
        KEY_SELECT, KEY_START, KEY_UP,
        KEY_DOWN,KEY_LEFT,KEY_RIGHT,KEY_A
    ]

    LIB_FILE_NAME = 'libnesfrontend.so'

    def __init__(self, game_path, serialized_path=None, show_ui=False, interactive=False):
        self.serialized_path = serialized_path.encode()
        self.game_path = game_path.encode()
        self.lib = ct.cdll.LoadLibrary(NES.LIB_FILE_NAME)
        self.lib.nes_init()
        self.lib.nes_load_game(
            ct.c_char_p(self.game_path),
            ct.c_char_p(self.serialized_path)
        )
        if show_ui:
            self.lib.nes_init_ui(interactive)

    def get_ram_byte(self, addr):
        return self.lib.nes_get_ram_byte(addr)

    def press_key(self, key):
        if key not in NES.KEYS:
            raise ValueError("Incorrect key")
        self.lib.press_key(key)

    def run(self):
        self.lib.nes_run()

    def reset(self):
        if self.serialized_path:
            self.lib.nes_reset_game()
