from collections import namedtuple
from gaming.nes.NESGame import NESGame
from gaming import res_path
from os.path import join as join_path
from os import linesep


Enemy = namedtuple('Enemy', ['x', 'y', 'id'])


class SuperMarioBros(NESGame):
    BLOCK_COLS = 18
    BLOCK_ROWS = 13

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
        return SuperMarioBros.get_screen(x), x_in_b, (y - 16) // 16

    def get_blockbuf_value(self, x, y):
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
        return enemies

    def get_inputs(self):
        input_vals = []
        enemies = self.get_enemies()

        # Go over blocks in radius
        for k in range(-self.sight_y_up+ 1, self.sight_y_down+ 1):
            for j in range(self.sight_x):
                y_block = self.block_y + k
                x_block = self.block_x + j + 1
                if y_block < 0 or y_block > SuperMarioBros.BLOCK_ROWS:
                    input_vals.append(0)  # if we see higher/lower than the screen, we see 0.
                else:
                    blockbuf_val = self.get_blockbuf_value(x_block, y_block)
                    input_vals.append(blockbuf_val)  # add it to input
                    if blockbuf_val == 0:
                        for enemy in enemies:  # check for enemies if there was no block
                            if enemy.y == y_block and enemy.x == x_block:
                                input_vals[-1] = enemy.id
                                break
        return input_vals

    def pretty_inputs_string(self):
        """
        :return: printable version of input in rows and columns
        """
        inputs = self.get_inputs()
        rows = []
        for i in range(self.sight_y_up + self.sight_y_down):
            rows.append(str(inputs[self.sight_x*i:(i + 1) * self.sight_x]))
        return linesep.join(rows)

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