# sokobanpy

[![PyPI version][pypi_img]][pypi_link]
[![Downloads][downloads_img]][downloads_link]

  [pypi_img]: https://badge.fury.io/py/sokobanpy.svg
  [pypi_link]: https://badge.fury.io/py/sokobanpy
  [downloads_img]: https://pepy.tech/badge/sokobanpy
  [downloads_link]: https://pepy.tech/project/sokobanpy

[Documentation](https://jacklinquan.github.io/sokobanpy)

Sokoban in Python.

- Author: Quan Lin
- License: MIT

---

## What is Sokoban?

Sokoban is a classic puzzle game
where the player pushes boxes onto designated goal positions within a warehouse-like environment.
The game is played on a grid, and each element is represented by a standard character:

- `"#"`: Wall
- `"@"`: Player (Sokoban)
- `"$"`: Box
- `"."`: Goal
- `"*"`: Box on a goal
- `"+"`: Player on a goal
- `" "`: Empty space

### Objective
Move all boxes (`"$"`) onto the goal positions (`"."`) using the player (`"@"`).
Boxes can only be pushed (not pulled), and only one box can be pushed at a time.
The player cannot move through walls or boxes.

### How to play
Use directional controls to move the player.
Strategically plan moves to avoid pushing boxes into corners or against walls
where they can't be retrieved.
The puzzle is solved when all boxes are on goal tiles (`"*"`).

---

## Installation

```shell
pip install sokobanpy
```

---

## Usage

A simple example:

```python
from sokobanpy import Sokoban
level_string = (
    ""
    + "##########\n"
    + "#        #\n"
    + "#  $  +  #\n"
    + "#        #\n"
    + "##########\n"
)
game = Sokoban(level_string, undo_limit=256)
while True:
    print(game)
    print(f"nmove={game.nmove}, npush={game.npush}")
    if game.is_solved():
        print("Level Solved!")
        break
    action = input("Player Action (w,a,s,d,u,q): ")
    if action == "w":
        game.move(Sokoban.UP)
    elif action == "a":
        game.move(Sokoban.LEFT)
    elif action == "s":
        game.move(Sokoban.DOWN)
    elif action == "d":
        game.move(Sokoban.RIGHT)
    elif action == "u":
        game.undo()
    elif action == "q":
        break
```

There are more examples in
[examples](https://github.com/jacklinquan/sokobanpy/tree/main/examples)
directory.
