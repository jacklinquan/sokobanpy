"""A Simple Python module for ASCII application.

- Author: Quan Lin
- License: MIT
"""

from time import time
from msvcrt import kbhit, getwch

import colorama


class Screen:
    def __init__(self, w=48, h=16):
        self.w = w  # Screen width
        self.h = h  # Screen height

        self.space_char = " "  # The charactor representing empty space
        # Create a buffer for the screen
        self._buf = [[self.space_char for x in range(self.w)] for y in range(self.h)]
        colorama.init()  # Enable `clear screen` and `move cursor` sequences

    def __str__(self):
        return "\n".join(["".join(line) for line in self._buf])

    def fill(self, c):
        self._buf = [[c for x in range(self.w)] for y in range(self.h)]

    def to_origin(self):
        print("\x1b[1;1H", end="")

    def clear(self):
        print("\x1b[2J", end="")

    def pixel(self, px, py, c="\u2588"):
        if 0 <= px < self.w and 0 <= py < self.h:
            self._buf[py][px] = c

    def blit(self, px, py, rep):
        for y, row in enumerate(rep):
            for x, c in enumerate(row):
                if c != self.space_char:
                    self.pixel(px + x, py + y, c)

    def flip(self, debug_info=None):
        self.to_origin()

        print(self)

        if debug_info:
            print(debug_info)

        print(end="", flush=True)

        self.fill(self.space_char)


class Sprite:
    UP, LEFT, DOWN, RIGHT = tuple(range(4))

    def __init__(self):
        self.manager = None  # The manager of this sprite

        self.x = 0  # X position in float
        self.y = 0  # Y position in float
        self.w = 0  # Width of this sprite
        self.h = 0  # Height of this sprite

        self.reps = [["\u2588\u2588"]]  # Default sprite reps
        self.rep_idx = 0  # Representative index

        self.vx = 0  # X velocity in float
        self.vy = 0  # Y velocity in float
        self._layer = 0  # The layer this sprite is located in
        self.is_overlay = False  # Overlay is not influenced by camera target
        self.name = ""  # Sprite name
        self.killed = False  # Flag for being killed or not
        self._frames_to_kill = None  # Number of frames to kill this sprite

    def _frame_routine(self):
        self.x += self.vx
        self.y += self.vy

        if self._frames_to_kill is not None:
            self._frames_to_kill -= 1
            if self._frames_to_kill <= 0:
                self.killed = True

        self.update()

    def get_px(self):
        return int(self.x)  # int(self.x + 0.5)

    def get_py(self):
        return int(self.y)  # int(self.y + 0.5)

    def get_layer(self):
        return self._layer

    def set_layer(self, layer):
        self._layer = layer
        if self.manager:
            self.manager._sort_sprites_by_layer()

    def get_rep(self):
        if not self.reps:
            return None
        return self.reps[self.rep_idx]

    def clamp_position(self, up=None, left=None, down=None, right=None):
        if (right is not None) and (self.x > right - self.w):
            self.x = right - self.w
        if (left is not None) and (self.x < left):
            self.x = left
        if (down is not None) and (self.y > down - self.h):
            self.y = down - self.h
        if (up is not None) and (self.y < up):
            self.y = up

    def kill(self):
        self.killed = True

    def kill_after_x_frames(self, num):
        self._frames_to_kill = num

    def check_collision(self, other):
        if isinstance(other, Sprite) and (other is not self):
            diff_x = (self.x + self.w / 2) - (other.x + other.w / 2)
            diff_y = (self.y + self.h / 2) - (other.y + other.h / 2)
            margin_dx = abs(diff_x) - ((self.w + other.w) / 2)
            margin_dy = abs(diff_y) - ((self.h + other.h) / 2)

            if margin_dx < 0 and margin_dy < 0:
                abs_margin_dy = abs(margin_dy)
                abs_margin_dx = abs(margin_dx)
                is_at_top_or_bottom = abs_margin_dy <= abs_margin_dx
                if diff_y >= 0:
                    if diff_x >= 0:
                        # `other` is top-left to `self`
                        if is_at_top_or_bottom:
                            return (Sprite.UP, abs_margin_dy)
                        else:
                            return (Sprite.LEFT, abs_margin_dx)
                    else:
                        # `other` is top-right to `self`
                        if is_at_top_or_bottom:
                            return (Sprite.UP, abs_margin_dy)
                        else:
                            return (Sprite.RIGHT, abs_margin_dx)
                else:
                    if diff_x >= 0:
                        # `other` is bottom-left to `self`
                        if is_at_top_or_bottom:
                            return (Sprite.DOWN, abs_margin_dy)
                        else:
                            return (Sprite.LEFT, abs_margin_dx)
                    else:
                        # `other` is bottom-right to `self`
                        if is_at_top_or_bottom:
                            return (Sprite.DOWN, abs_margin_dy)
                        else:
                            return (Sprite.RIGHT, abs_margin_dx)

        return None

    def check_collision_by_pixel(self, other):
        if isinstance(other, Sprite) and (other is not self):
            px = self.get_px()
            py = self.get_py()
            rep = self.get_rep()
            other_px = other.get_px()
            other_py = other.get_py()
            other_rep = other.get_rep()
            space_char = self.manager.screen.space_char
            if rep and other_rep:
                pos_set = {
                    (px + x, py + y)
                    for y, row in enumerate(rep)
                    for x, c in enumerate(row)
                    if c != space_char
                }
                o_pos_set = {
                    (other_px + x, other_py + y)
                    for y, row in enumerate(other_rep)
                    for x, c in enumerate(row)
                    if c != space_char
                }

                if pos_set & o_pos_set:
                    return True

        return False

    def update(self):
        pass


class Manager:
    def __init__(self):
        self.screen = None  # The screen of this app
        self.camera_target = None  # The camera target for the screen

        self.target_fps = 20  # The target FPS
        self.actual_fps = 0  # The actual FPS
        self._frame_start_time = time()  # The initial start time

        self._sprite_list = []  # A list holding all the available sprites
        self._pressed_key = None  # The current pressed key
        self._debug_info = None  # Debugging information
        self._running = True  # Flag to keep this app running

    def _remove_killed_sprites(self):
        self._sprite_list = [
            sprite for sprite in self._sprite_list if not sprite.killed
        ]

    def _sort_sprites_by_layer(self):
        self._sprite_list.sort(key=lambda x: x.get_layer())

    def _frame_routine(self):
        self._pressed_key = getwch() if kbhit() else None

        # Sprites frame routine
        for sprite in self._sprite_list:
            sprite._frame_routine()

        self.update()

        self._remove_killed_sprites()

        # Screen frame routine
        for sprite in self._sprite_list:
            rep = sprite.get_rep()
            if rep:
                x = sprite.x
                y = sprite.y
                if self.camera_target and not sprite.is_overlay:
                    ct = self.camera_target
                    sc = self.screen
                    x += (sc.w - ct.w) / 2 - ct.x
                    y += (sc.h - ct.w) / 2 - ct.y
                self.screen.blit(int(x), int(y), rep)
        self.screen.flip(debug_info=self._debug_info)

    def _frame_tick(self):
        end_time = time()
        duration = end_time - self._frame_start_time
        if duration >= 1 / self.target_fps:
            self.actual_fps = round(1 / duration)
            self._frame_start_time = end_time
            return True
        return False

    def get_pressed_key(self):
        return self._pressed_key

    def add_sprite(self, sprite):
        sprite.killed = False
        self._sprite_list.append(sprite)
        self._sort_sprites_by_layer()
        sprite.manager = self

    def get_sprites(self, cls=Sprite, name=None):
        return [
            sprite
            for sprite in self._sprite_list
            if isinstance(sprite, cls) and ((not name) or (sprite.name == name))
        ]

    def kill_sprites(self, cls=Sprite, name=None):
        for sprite in self._sprite_list:
            if isinstance(sprite, cls) and ((not name) or (sprite.name == name)):
                sprite.kill()

    def set_debug_info(self, debug_info):
        self._debug_info = debug_info

    def exit(self):
        self._running = False

    def run(self):
        self.screen.clear()

        while self._running:
            # Manager frame routine
            self._frame_routine()

            # Try to achieve the target FPS
            while not self._frame_tick():
                pass

    def update(self):
        pass
