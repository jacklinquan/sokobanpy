"""MenuTree module."""


class MenuTree:
    UP, RIGHT, DOWN, LEFT = tuple(range(4))

    def __init__(
        self,
        name,
        children=None,
        # View related:
        nrow=None,
        ncol=None,
    ):
        self.name = name
        self.children = children
        self.is_open = False
        self.index = None
        if self.children:
            self.index = 0

        # View related attributes
        self.nrow = nrow
        self.ncol = ncol
        self.view_index = 0

    def __str__(self):
        res = []

        len_item_limit = 65535
        indicator = "->"
        elli = ".."

        path_str = self.get_opened_path()
        if self.ncol:
            len_item_limit = self.ncol - len(indicator)
            if len(path_str) > self.ncol:
                path_str = elli + path_str[-(self.ncol - len(elli)) :]

        res.append(path_str)

        menu_list = self._get_view_list()

        index = self.get_opened_index()
        view_index = self._get_opened_view_index()
        if menu_list:
            for i, item in enumerate(menu_list):
                if len(item) > len_item_limit:
                    half_item_len = (len_item_limit - len(elli)) // 2
                    item = (
                        item[:half_item_len]
                        + elli
                        + item[-(len_item_limit - len(elli) - half_item_len) :]
                    )
                if index - view_index == i:
                    item_str = indicator + item
                else:
                    item_str = " " * len(indicator) + item
                res.append(item_str)

        return "\n".join(res)

    def __repr__(self):
        return f"{self.name} with children {self.children}"

    def _get_opened_view_index(self):
        opened_child = self.get_opened_child()
        return opened_child.view_index

    def _inc_opened_index(self):
        opened_child = self.get_opened_child()
        opened_child.index += 1
        if opened_child.index >= len(opened_child.children):
            opened_child.index = len(opened_child.children) - 1
        opened_child._adjust_view_index()

    def _dec_opened_index(self):
        opened_child = self.get_opened_child()
        opened_child.index -= 1
        if opened_child.index < 0:
            opened_child.index = 0
        opened_child._adjust_view_index()

    def _open_active(self):
        opened_child = self.get_opened_child()
        if opened_child.index is None:
            return
        if opened_child.children[opened_child.index].index is None:
            return
        opened_child.children[opened_child.index].is_open = True
        self._adjust_view_index()

    def _close_opened(self):
        opened_child = self.get_opened_child()
        opened_child.is_open = False
        self._adjust_view_index()

    def _adjust_view_index(self):
        opened_child = self.get_opened_child()
        if opened_child.nrow is None:
            return
        menu_list_nrow = opened_child.nrow - 1
        if opened_child.index < opened_child.view_index:
            opened_child.view_index = opened_child.index
        elif opened_child.index >= opened_child.view_index + menu_list_nrow:
            opened_child.view_index = opened_child.index - menu_list_nrow + 1

    def _get_view_list(self):
        opened_child = self.get_opened_child()
        menu_list = [item.name for item in opened_child.children]
        if opened_child.nrow:
            menu_list = menu_list[
                opened_child.view_index : opened_child.view_index
                + opened_child.nrow
                - 1
            ]
        return menu_list

    @classmethod
    def build_from_list(
        cls,
        menu_list,
        # View related:
        nrow=None,
        ncol=None,
    ):
        len_menu_list = len(menu_list)
        assert len_menu_list > 0
        if len_menu_list == 1:
            return cls(menu_list[0], None, nrow, ncol)
        else:
            return cls(
                menu_list[0],
                [
                    cls.build_from_list(menu_list[i], nrow, ncol)
                    for i in range(1, len_menu_list)
                ],
                nrow,
                ncol,
            )

    @classmethod
    def build_from_dict(
        cls,
        menu_dict,
        # View related:
        nrow=None,
        ncol=None,
    ):
        NAME = "name"
        CHILDREN = "children"

        assert NAME in menu_dict

        if (CHILDREN not in menu_dict) or (not menu_dict[CHILDREN]):
            return cls(menu_dict[NAME], None, nrow, ncol)
        else:
            return cls(
                menu_dict[NAME],
                [
                    cls.build_from_dict(child, nrow, ncol)
                    for child in menu_dict[CHILDREN]
                ],
                nrow,
                ncol,
            )

    def get_opened_child(self):
        if self.index is None:
            return self
        if self.children[self.index].is_open:
            return self.children[self.index].get_opened_child()
        else:
            return self

    def get_active_child(self):
        opened_child = self.get_opened_child()
        if opened_child.index is None:
            return opened_child
        return opened_child.children[opened_child.index]

    def get_opened_index(self):
        opened_child = self.get_opened_child()
        return opened_child.index

    def get_opened_path(self):
        if self.index is None:
            return self.name
        if self.children[self.index].is_open:
            return self.name + "/" + self.children[self.index].get_opened_path()
        else:
            return self.name

    def get_active_path(self):
        if self.index is None:
            return self.name
        if self.children[self.index].is_open:
            return self.name + "/" + self.children[self.index].get_active_path()
        else:
            return self.name + "/" + self.children[self.index].name

    def action(self, direction):
        old_active_path = self.get_active_path()
        if direction == self.UP:
            self._dec_opened_index()
        elif direction == self.RIGHT:
            self._open_active()
        elif direction == self.DOWN:
            self._inc_opened_index()
        elif direction == self.LEFT:
            self._close_opened()
        if self.get_active_path() == old_active_path:
            return False
        return True


def menu_tree_list_example():
    # fmt: off
    menu = MenuTree.build_from_list(
        ["menu",
            ["submenu_0",
                ["submenu_0_0"],
                ["submenu_0_1"],
            ],
            ["submenu_1",
                ["submenu_1_0"],
                ["submenu_1_1",
                    ["submenu_1_1_0"],
                    ["submenu_name_is_long_1_1_1"],
                ],
            ],
            ["submenu_2",
                ["submenu_2_0"],
                ["submenu_2_1"],
            ],
            ["submenu_3"],
            ["submenu_name_is_long_4"],
            ["submenu 5"],
            ["submenu_6"],
            ["submenu_7"],
            ["submenu_8"],
            ["submenu_9"],
        ],
        8,
        16,
    )
    # fmt: on

    while True:
        print("Screen----------")
        print(menu)
        print("----------------")
        action = input("w: UP, d: RIGHT, s: DOWN, a: LEFT > ")
        if action == "w":
            res = menu.action(menu.UP)
        elif action == "d":
            res = menu.action(menu.RIGHT)
        elif action == "s":
            res = menu.action(menu.DOWN)
        elif action == "a":
            res = menu.action(menu.LEFT)
        else:
            res = None
        print(res)
        print(menu.get_opened_path())
        print(menu.get_active_path())


def menu_tree_dict_example():
    NAME = "name"
    CHILDREN = "children"
    # fmt: off
    menu = MenuTree.build_from_dict(
        {NAME: "menu", CHILDREN: [
            {NAME: "submenu_0", CHILDREN: [
                {NAME: "submenu_0_0"},
                {NAME: "submenu_0_1"},],
            },
            {NAME: "submenu_1", CHILDREN: [
                {NAME: "submenu_1_0"},
                {NAME: "submenu_1_1", CHILDREN: [
                    {NAME: "submenu_1_1_0"},
                    {NAME: "submenu_name_is_long_1_1_1"},],
                },],
            },
            {NAME: "submenu_2", CHILDREN: [
                {NAME: "submenu_2_0"},
                {NAME: "submenu_2_1"},],
            },
            {NAME: "submenu_3"},
            {NAME: "submenu_name_is_long_4"},
            {NAME: "submenu 5"},
            {NAME: "submenu_6"},
            {NAME: "submenu_7"},
            {NAME: "submenu_8"},
            {NAME: "submenu_9"},],
        },
        8,
        16,
    )
    # fmt: on

    while True:
        print("Screen----------")
        print(menu)
        print("----------------")
        action = input("w: UP, d: RIGHT, s: DOWN, a: LEFT > ")
        if action == "w":
            res = menu.action(menu.UP)
        elif action == "d":
            res = menu.action(menu.RIGHT)
        elif action == "s":
            res = menu.action(menu.DOWN)
        elif action == "a":
            res = menu.action(menu.LEFT)
        else:
            res = None
        print(res)
        print(menu.get_opened_path())
        print(menu.get_active_path())


if __name__ == "__main__":
    # menu_tree_list_example()
    menu_tree_dict_example()
