"""Sokoban in Python

- Author: Quan Lin
- License: MIT
"""

from collections import deque


__version__ = "1.1.0"

DEFAULT_LEVEL_STRING = (
    ""
    + "##########\n"
    + "#        #\n"
    + "#  $  +  #\n"
    + "#        #\n"
    + "##########\n"
)


class SokobanVector:
    """Represents a position or directional offset on a Sokoban board.

    Encapsulates a 2D coordinate (row and column) and supports vector-style
    operations like addition, negation, equality, and hashing.

    Attributes:
        r (int): Row index of the position.
        c (int): Column index of the position.
    """

    def __init__(self, r, c):
        """Initialize a SokobanVector instance.

        Args:
            r (int): Row index or row component of a direction vector.
            c (int): Column index or column component of a direction vector.
        """
        self.r = r
        self.c = c

    def __repr__(self):
        """Return a human-readable string representation.

        Returns:
            str: String in the form "SokobanVector(r=<row>, c=<col>)".
        """
        return f"{self.__class__.__name__}(r={self.r}, c={self.c})"

    def __add__(self, other):
        """Add two SokobanVector vectors element-wise.

        Args:
            other (SokobanVector): Another position or offset.

        Returns:
            SokobanVector: New instance whose row and column are the sums.

        Raises:
            TypeError: If `other` is not a SokobanVector instance.
        """
        if not isinstance(other, self.__class__):
            raise TypeError(
                "unsupported operand type(s) for +: "
                + f"'{self.__class__.__name__}' "
                + f"and '{other.__class__.__name__}'"
            )
        return self.__class__(self.r + other.r, self.c + other.c)

    def __sub__(self, other):
        """Subtract another SokobanVector from this SokobanVector.

        Args:
            other (SokobanVector): Another position or offset.

        Returns:
            SokobanVector: New instance whose row and column are the results.

        Raises:
            TypeError: If `other` is not a SokobanVector instance.
        """
        if not isinstance(other, self.__class__):
            raise TypeError(
                "unsupported operand type(s) for -: "
                + f"'{self.__class__.__name__}' "
                + f"and '{other.__class__.__name__}'"
            )
        return self.__class__(self.r - other.r, self.c - other.c)

    def __neg__(self):
        """Invert this vector (negate both row and column).

        Returns:
            SokobanVector: New instance with both components negated.
        """
        return self.__class__(-self.r, -self.c)

    def __eq__(self, other):
        """Check equality by comparing row and column.

        Args:
            other (object): Object to compare.

        Returns:
            bool: True if `other` is a SokobanVector with the same r and c.
        """
        return (
            isinstance(other, self.__class__)
            and (self.r == other.r)
            and (self.c == other.c)
        )

    def __hash__(self):
        """Compute a hash so positions can be used in sets and dict keys.

        Returns:
            int: Hash of the (row, column) tuple.
        """
        return hash((self.r, self.c))


class Sokoban:
    """Sokoban puzzle game representation and logic.

    This class manages the game board, including walls, goals, boxes, and the player,
    and supports loading levels, rendering the board, executing moves, undoing moves,
    and checking for a solved state.

    Attributes:
        player (SokobanVector): Current player position.
        walls (set[SokobanVector]): Positions of walls.
        goals (set[SokobanVector]): Positions of goals.
        boxes (set[SokobanVector]): Positions of boxes.
        nrow (int): Number of rows in the level.
        ncol (int): Number of columns in the level.
        nmove (int): Number of moves made.
        npush (int): Number of box pushes made.
        history (deque): Move history for undo.
        undo_limit (int | None): Maximum undo history size.
    """

    SPACE = " "
    WALL = "#"
    GOAL = "."
    BOX = "$"
    BOX_IN_GOAL = "*"
    PLAYER = "@"
    PLAYER_IN_GOAL = "+"
    CHAR_SET = {SPACE, WALL, GOAL, BOX, BOX_IN_GOAL, PLAYER, PLAYER_IN_GOAL}

    RIGHT = SokobanVector(0, 1)
    DOWN = SokobanVector(1, 0)
    LEFT = -RIGHT
    UP = -DOWN
    DIRECTION_SET = {RIGHT, DOWN, LEFT, UP}

    def __init__(self, level_string=DEFAULT_LEVEL_STRING, undo_limit=None):
        """Initialize Sokoban from a level string.

        Parses the given `level_string` into the internal state and sets an optional undo limit.

        Args:
            level_string (str): Multi-line string defining the initial board layout.
            undo_limit (int | None): Maximum number of moves to store for undo; None for unlimited.
        """
        self.undo_limit = undo_limit
        self._from_string(level_string)

    def __str__(self):
        """Return a string representation of the current board."""
        grid = self.to_grid()
        return "\n".join(["".join(line) for line in grid])

    def _reset(self):
        """Clear all board elements and undo history."""
        self.player = None
        self.walls = set()
        self.goals = set()
        self.boxes = set()
        self.nrow = 0
        self.ncol = 0
        self.nmove = 0
        self.npush = 0
        self.history = deque((), self.undo_limit)

    def _from_grid(self, grid):
        """Load board state from a 2D list of characters.

        Args:
            grid (list[list[str]]): 2D array of Sokoban symbols.
        """
        self._reset()

        for r, row in enumerate(grid):
            for c, char in enumerate(row):
                pos = SokobanVector(r, c)
                if char == self.WALL:
                    self.walls.add(pos)
                elif char == self.GOAL:
                    self.goals.add(pos)
                elif char == self.BOX:
                    self.boxes.add(pos)
                elif char == self.BOX_IN_GOAL:
                    self.goals.add(pos)
                    self.boxes.add(pos)
                elif char == self.PLAYER:
                    self.player = pos
                elif char == self.PLAYER_IN_GOAL:
                    self.goals.add(pos)
                    self.player = pos

        self.nrow = len(grid)
        self.ncol = max(len(row) for row in grid)

    def _from_string(self, level_string):
        """Parse and load a level from a Sokoban level string.

        Args:
            level_string (str): Multi-line string containing Sokoban characters.
        """
        # Remove space on the right and non-sokoban lines.
        grid = [
            [char for char in line.rstrip()]
            for line in level_string.split("\n")
            if all(char in self.CHAR_SET for char in line.rstrip())
        ]
        # Remove empty rows.
        grid = [row for row in grid if "".join(row).rstrip()]
        # Number of indent
        num_indent = min(len(row) - len("".join(row).lstrip()) for row in grid)
        # # Dedent
        grid = [row[num_indent:] for row in grid]
        # Initialize from the prepared grid
        self._from_grid(grid)

    def to_grid(self):
        """Render the current game state as a 2D grid of characters.

        Returns:
            list[list[str]]: 2D array representing the board layout.
        """
        grid = [[self.SPACE for c in range(self.ncol)] for r in range(self.nrow)]

        for wall in self.walls:
            grid[wall.r][wall.c] = self.WALL

        for goal in self.goals:
            grid[goal.r][goal.c] = self.GOAL

        for box in self.boxes:
            if box in self.goals:
                grid[box.r][box.c] = self.BOX_IN_GOAL
            else:
                grid[box.r][box.c] = self.BOX

        if self.player is not None:
            if self.player in self.goals:
                grid[self.player.r][self.player.c] = self.PLAYER_IN_GOAL
            else:
                grid[self.player.r][self.player.c] = self.PLAYER

        return grid

    def covers(self, position):
        """Check if a position is within board bounds.

        Args:
            position (SokobanVector): Position to check.

        Returns:
            bool: True if position is on the board; False otherwise.
        """
        return (0 <= position.r < self.nrow) and (0 <= position.c < self.ncol)

    def can_move(self, direction):
        """Return whether the player can move in the given direction.

        Args:
            direction (SokobanVector): Direction vector.

        Returns:
            bool: True if move is legal; False otherwise.
        """
        if self.player is None:
            return False

        new_player = self.player + direction
        new_box = new_player + direction

        if (new_player in self.walls) or (not self.covers(new_player)):
            return False
        elif new_player in self.boxes:
            if (new_box in (self.boxes | self.walls)) or (not self.covers(new_box)):
                return False
            else:
                return True
        else:
            return True

    def move(self, direction):
        """Move the player in a direction, pushing a box if necessary.

        Args:
            direction (SokobanVector): Direction vector.

        Returns:
            bool: True if move executed; False if illegal.
        """
        if not self.can_move(direction):
            return False

        old_player = self.player
        self.player = self.player + direction
        self.nmove += 1

        if self.player in self.boxes:
            self.boxes.discard(self.player)
            new_box = self.player + direction
            self.boxes.add(new_box)
            self.npush += 1
            self.history.append((old_player, self.player, new_box))
        else:
            self.history.append((old_player, self.player, None))

        return True

    def undo(self):
        """Undo the last move, restoring previous positions.

        Returns:
            bool: True if an undo was performed; False if no history.
        """
        if not self.history:
            return False

        old_player, new_player, new_box = self.history.pop()
        self.player = old_player
        self.nmove -= 1

        if new_box:
            self.boxes.discard(new_box)
            self.boxes.add(new_player)
            self.npush -= 1

        return True

    def is_solved(self):
        """Check if all boxes are on goal positions.

        Returns:
            bool: True if the puzzle is solved; False otherwise.
        """
        return self.goals == self.boxes

    def find_path(self, target_pos):
        """Find a path of empty spaces from the player to target using BFS.

        Args:
            target_pos (SokobanVector): Destination position.

        Returns:
            list[SokobanVector] | None: Sequence of positions to move through, or None if unreachable.
        """
        if self.player is None:
            return None

        if not self.covers(target_pos):
            return None

        grid = self.to_grid()
        if grid[target_pos.r][target_pos.c] != self.SPACE:
            return None

        queue = deque([(self.player, [])], self.nrow + self.ncol)
        explored = set()

        while queue:
            curr_pos, curr_path = queue.popleft()
            if curr_pos == target_pos:
                return curr_path

            for direction in self.DIRECTION_SET:
                new_pos = curr_pos + direction
                if (
                    self.covers(new_pos)
                    and grid[new_pos.r][new_pos.c] == self.SPACE
                    and (new_pos not in explored)
                ):
                    new_path = curr_path + [new_pos]
                    queue.append((new_pos, new_path))
                    explored.add(new_pos)

        return None
