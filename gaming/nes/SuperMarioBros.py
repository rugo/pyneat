from collections import namedtuple
from gaming.nes.NESGame import NESGame
from gaming import res_path
from os.path import join as join_path


Enemy = namedtuple('Enemy', ['x', 'y', 'id'])


class SuperMarioBros(NESGame):
    game_path = join_path(res_path, "mario_bros.nes")
    savegame_path = join_path(res_path, "mario_bros.nes-savegame")

    def __init__(self, show_ui, sight_y_up, sight_y_down, sight_x, interactive=False):
        super(SuperMarioBros, self).__init__(show_ui, interactive)
        self.sight_y_up = sight_y_up
        self.sight_y_down = sight_y_down
        self.sight_x = sight_x
        self.x = self.y = self.screen = self.block_x = self.block_y = 0
        self._calc_x()
        self._calc_y()
        self._calc_block_pos()

    def _calc_x(self):
        a = self.emu.get_ram_byte(0x6D)
        b = self.emu.get_ram_byte(0x86)
        self.x = (a << 8) + b

    def fitness(self):
        return self.x

    def is_alive(self):
        return self.emu.get_ram_byte(0x75A) >= 2

    @staticmethod
    def get_screen(x):
        """
        Calculate screen by x pos in level.
        """
        return (x // 256) % 2

    def run(self):
        self.emu.run()
        self._calc_x()
        self._calc_y()
        self._calc_block_pos()

    def _calc_block_pos(self):
        self.screen, self.block_x, self.block_y = SuperMarioBros.level_pos_to_blocknum(self.x, self.y)

    @staticmethod
    def level_pos_to_blocknum(x, y):
        x_in_b = ((x % 256) // 16)  # pos within screen
        return (x // 256) % 2, x_in_b, (y - 16) // 16

    def get_blockbuf_value_by_lvl(self, x, y):
        """
        Calc the blockbuf value based on block(x, y)! The chosen screen is relative to Marios position.
        The Block buffer consists of two 16*13 buffers.
        Depending on the position in the screen it is possible that
        mario sees into the other screen. Thats why this method
        accepts blockbuf positions within the range 32*13. It basically
        constructs one big screen.
        """
        block_screen_carry = x // 16  # either 0 or 1
        # Check if the wanted block (x,y) is in the current screen
        block_screen = (self.screen + block_screen_carry) % 2
        # block num within screen
        new_x = x % 16
        # The offset is the screen number(0 or 1) * 208 (16*13 blocks per screen)
        # + the x and y coordinates
        offset = 208 * block_screen + new_x + y * 16
        return self.emu.get_ram_byte(0x500 + offset)

    def draw_debug_map(self):
        buf = [self.emu.get_ram_byte(0x500 + x) for x in range(0, 414 + 1)]
        # player pos
        posx = (self.x % 256) // 16
        posy = ((self.y - 16) // 16)
        mod = bool((self.x // 256) % 2)
        buf[208 * mod + posx + 16 * posy] = 66
        mn = not mod
        # enemy pos
        enemies = []
        for i in range(5):
            if self.emu.get_ram_byte(0xF + i):
                eposx = (self.emu.get_ram_byte(0x6E + i) << 8) + self.emu.get_ram_byte(0x87 + i)
                neposx = ((eposx % 256) // 16)
                emod = bool((eposx // 256) % 2)
                eposy = self.emu.get_ram_byte(0xCF + i)
                if eposy:
                    eposy -= 16
                neposy = eposy // 16
                enemies.append((neposx + emod * 16, neposy))
                if neposy:
                    print("Enemy {}: {}x{}".format(i, neposx, neposy))
                    buf[208 * emod + neposx + 16 * neposy] = 11
        for i in range(208 // 16):
            for x in buf[208 * mod + i * 16:208 * mod + i * 16 + 16]:
                if x:
                    print("%03d" % x, end=" ")
                else:
                    print("   ", end=" ")
            print(" | ", end="")
            for x in buf[208 * mn + i * 16:208 * mn + i * 16 + 16]:
                if x:
                    print("%03d" % x, end=" ")
                else:
                    print("   ", end=" ")
            print()

    def get_enemies(self):
        """
        Returns a list of max 5 enemies drawn on both screens with
        x and y coordinates WITHIN the double blockbuf (32*13) and the enemies id.
        """
        # We have max 5 enemies
        enemies = []
        for i in range(5):
            if self.emu.get_ram_byte(0xF + i):  # enemy number i is loaded
                # enemy id
                enemy_id = self.emu.get_ram_byte(0x16 + i)
                # pos in level
                enemy_x = (self.emu.get_ram_byte(0x6E + i) << 8) + self.emu.get_ram_byte(0x87 + i)
                enemy_y = self.emu.get_ram_byte(0xCF + i)
                if enemy_y:
                    enemy_y -= 16
                enemy_screen, enemy_xb, enemy_yb = SuperMarioBros.level_pos_to_blocknum(enemy_x, enemy_y)
                enemies.append(Enemy(16 * enemy_screen + enemy_xb, enemy_yb, enemy_id))
                # TODO: filter out posy = 0 ?
        return enemies

    def get_inputs(self):
        input_vals = []
        # Go over blocks in radius
        for k in range(-self.sight_y_up+ 1, self.sight_y_down+ 1):
            for j in range(self.sight_x):
                input_vals.append(self.get_blockbuf_value_by_lvl(self.block_x + j + 1, self.block_y + k))
        # Add enemies
        y_border = (self.block_y - (self.sight_y_up)) + 1
        for enemy in self.get_enemies():
            if self.screen * 16 + self.block_x < enemy.x <= self.screen * 16 + self.block_x + self.sight_x:
                if enemy.y > y_border and enemy.y < y_border + self.sight_y_up + self.sight_y_down:
                    arr_x = enemy.x - (self.screen * 16 + self.block_x) - 1
                    if y_border < 0:
                        arr_y = (self.sight_y_up -1) * self.sight_x # Very ugly hack. set enemy infront of mario in case marios sights
                        # goes outside frame. TODO: fix this.
                    else:
                        arr_y = (enemy.y - y_border) * self.sight_x
                    idx = arr_x + arr_y
                    input_vals[idx] = enemy.id
        return input_vals

    def get_normalized_inputs(self):
        inp = self.get_inputs()
        norm_inp = []
        for i in inp:
            if i == 6:
                norm_inp.append(-1)
            elif i >= 80:
                norm_inp.append(1)
            elif i == 0:
                norm_inp.append(0)
            else:
                norm_inp.append(1)
        return norm_inp

    def _calc_y(self):
        # pos on screen is at 0xCE, 0xB5 holds viewport
        # pos 0 = on top of the screen
        if self.emu.get_ram_byte(0x00B5) != 1:
            self.y = 0
        self.y = self.emu.get_ram_byte(0xCE)