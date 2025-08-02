# sokobanpy

Sokoban in Python.

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

For details, please refer to the [Homepage](https://github.com/jacklinquan/sokobanpy).
