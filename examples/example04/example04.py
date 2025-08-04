"""Sokoban game (text based)

'w': up
'a': left
's': down
'd': right or enter
'u': undo
'm': menu
'q': quit
"""

from pathlib import Path
from xml.etree import ElementTree

from text_engine import Screen, Sprite, Manager
from menu_tree import MenuTree
from sokobanpy import Sokoban


SCREEN_WIDTH = 48
SCREEN_HEIGHT = 16
COLLECTIONS_PATH = Path("level_collections")
COLLECTION_SUFFIX = ".slc"


class Menu(Sprite):
    def __init__(self):
        super().__init__()
        self.init_menu()

    def init_menu(self):
        self.collections = [
            item
            for item in COLLECTIONS_PATH.iterdir()
            if item.suffix == COLLECTION_SUFFIX
        ]

        NAME = "name"
        CHILDREN = "children"
        menu_dict = {NAME: "MENU", CHILDREN: []}
        for collection in self.collections:
            root = ElementTree.fromstring(collection.read_text())
            collection_dict = {NAME: collection.stem, CHILDREN: []}
            menu_dict[CHILDREN].append(collection_dict)
            for level in root.findall("./LevelCollection/Level"):
                collection_dict[CHILDREN].append({NAME: level.get("Id")})

        self.menutree = MenuTree.build_from_dict(
            menu_dict,
            SCREEN_HEIGHT,
            SCREEN_WIDTH,
        )
        self.update()

    def update(self):
        self.reps = [str(self.menutree).split("\n")]


class SokobanBoard(Sprite):
    def __init__(self, level_string):
        super().__init__()
        self.sokoban = Sokoban(level_string, undo_limit=256)
        self.update()

    def update(self):
        display = (
            str(self.sokoban)
            .replace(Sokoban.SPACE, "  ")
            .replace(Sokoban.WALL, "\u2588\u2588")
            .replace(Sokoban.GOAL, "::")
            .replace(Sokoban.BOX, "()")
            .replace(Sokoban.BOX_IN_GOAL, "[]")
            .replace(Sokoban.PLAYER, "@@")
            .replace(Sokoban.PLAYER_IN_GOAL, "++")
        )
        self.reps = [display.split("\n")]


class SokobanGame(Manager):
    STATE_MENU = 1
    STATE_PLAY = 2

    def __init__(self):
        super().__init__()

        self.screen = Screen(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.target_fps = 5

        self.menu = None
        self.init_menu()

    def init_menu(self):
        self.state = self.STATE_MENU
        self.kill_sprites()
        if self.menu is None:
            self.menu = Menu()
        self.add_sprite(self.menu)

    def init_play(self):
        _, collection_stem, level_id = self.menu.menutree.get_active_path().split("/")
        collection = COLLECTIONS_PATH / (collection_stem + COLLECTION_SUFFIX)
        self.state = self.STATE_PLAY
        self.kill_sprites()
        root = ElementTree.fromstring(collection.read_text())

        # level_string = "\n".join(
        #     line.text
        #     for line in root.findall(f"./LevelCollection/Level[@Id='{level_id}']/L")
        # )
        level = root.findall("./LevelCollection/Level")[
            self.menu.menutree.get_opened_index()
        ]
        level_string = "\n".join(line.text for line in level.findall("./L"))

        self.sokoban_board = SokobanBoard(level_string)
        self.add_sprite(self.sokoban_board)

    def update(self):
        if self.state == self.STATE_MENU:
            if self.get_pressed_key() == "q":
                self.exit()
                self.set_debug_info("Quit!" + " " * SCREEN_WIDTH)
            elif self.get_pressed_key() == "w":
                self.menu.menutree.action(MenuTree.UP)
            elif self.get_pressed_key() == "a":
                self.menu.menutree.action(MenuTree.LEFT)
            elif self.get_pressed_key() == "s":
                self.menu.menutree.action(MenuTree.DOWN)
            elif self.get_pressed_key() == "d":
                if not self.menu.menutree.action(MenuTree.RIGHT):
                    self.init_play()

            self.menu.update()
            self.set_debug_info(
                f"{self.menu.menutree.get_active_path()}" + " " * SCREEN_WIDTH
            )

        elif self.state == self.STATE_PLAY:
            if self.get_pressed_key() == "q":
                self.exit()
                self.set_debug_info("Quit!" + " " * SCREEN_WIDTH)
            elif self.get_pressed_key() == "m":
                self.init_menu()
            elif not self.sokoban_board.sokoban.is_solved():
                if self.get_pressed_key() == "w":
                    self.sokoban_board.sokoban.move(Sokoban.UP)
                elif self.get_pressed_key() == "a":
                    self.sokoban_board.sokoban.move(Sokoban.LEFT)
                elif self.get_pressed_key() == "s":
                    self.sokoban_board.sokoban.move(Sokoban.DOWN)
                elif self.get_pressed_key() == "d":
                    self.sokoban_board.sokoban.move(Sokoban.RIGHT)
                elif self.get_pressed_key() == "u":
                    self.sokoban_board.sokoban.undo()

            self.sokoban_board.update()
            if self.sokoban_board.sokoban.is_solved():
                self.set_debug_info("Solved!" + " " * SCREEN_WIDTH)
            else:
                self.set_debug_info(
                    f"nmove={self.sokoban_board.sokoban.nmove}"
                    + f", npush={self.sokoban_board.sokoban.npush}"
                    + " " * SCREEN_WIDTH
                )
        else:
            self.init_menu()


if __name__ == "__main__":
    SokobanGame().run()
