from sokobanpy import Sokoban

LEVEL_FILE_PATH = "level.txt"


def main():
    with open(LEVEL_FILE_PATH) as file:
        level_string = file.read()

    game = Sokoban(level_string, undo_limit=256)

    while True:
        display = (
            str(game)
            .replace(game.SPACE, "  ")
            .replace(game.WALL, "\u2588\u2588")
            .replace(game.GOAL, "::")
            .replace(game.BOX, "()")
            .replace(game.BOX_IN_GOAL, "[]")
            .replace(game.PLAYER, "@@")
            .replace(game.PLAYER_IN_GOAL, "++")
        )
        print(display)
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


if __name__ == "__main__":
    main()
