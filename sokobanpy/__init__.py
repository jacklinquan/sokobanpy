"""Sokoban in Python

- Author: Quan Lin
- License: MIT

Example:
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
"""

from .sokobanpy import (
    __version__,
    SokobanVector,
    Sokoban,
)

__all__ = [
    "SokobanVector",
    "Sokoban",
]
