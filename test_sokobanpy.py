from sokobanpy import SokobanVector, Sokoban


def test_SokobanVector():
    sv1 = SokobanVector(10, 20)
    sv2 = SokobanVector(50, 100)
    sv3 = sv1 + sv2
    sv4 = sv2 - sv1
    sv5 = -sv4

    assert sv1.r == 10 and sv1.c == 20
    assert repr(sv2) == "SokobanVector(r=50, c=100)"
    assert sv3 == SokobanVector(60, 120)
    assert sv4 == SokobanVector(40, 80)
    assert sv5 == SokobanVector(-40, -80)
    assert hash(sv5) == hash((-40, -80))


def test_Sockban():
    game = Sokoban(undo_limit=5)

    assert str(game) == (
        ""
        + "##########\n"
        + "#        #\n"
        + "#  $  +  #\n"
        + "#        #\n"
        + "##########"
    )

    assert game.to_grid() == [
        ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#"],
        ["#", " ", " ", " ", " ", " ", " ", " ", " ", "#"],
        ["#", " ", " ", "$", " ", " ", "+", " ", " ", "#"],
        ["#", " ", " ", " ", " ", " ", " ", " ", " ", "#"],
        ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#"],
    ]

    assert (
        game.covers(SokobanVector(0, 0))
        and game.covers(SokobanVector(0, 9))
        and game.covers(SokobanVector(4, 0))
        and game.covers(SokobanVector(4, 9))
    )

    assert not (
        game.covers(SokobanVector(-1, 0))
        or game.covers(SokobanVector(-1, 9))
        or game.covers(SokobanVector(0, -1))
        or game.covers(SokobanVector(0, 10))
        or game.covers(SokobanVector(4, -1))
        or game.covers(SokobanVector(4, 10))
        or game.covers(SokobanVector(5, 0))
        or game.covers(SokobanVector(5, 9))
    )

    assert all(game.can_move(direction) for direction in Sokoban.DIRECTION_SET)

    assert len(game.history) == 0

    for position in game.find_path(SokobanVector(1, 1)):
        game.move(position - game.player)

    assert game.player == SokobanVector(1, 1)
    assert not game.can_move(Sokoban.LEFT)
    assert not game.can_move(Sokoban.UP)
    assert len(game.history) == 5

    while game.undo():
        pass

    assert len(game.history) == 0

    for position in game.find_path(SokobanVector(3, 8)):
        game.move(position - game.player)

    assert game.player == SokobanVector(3, 8)
    assert not game.can_move(Sokoban.RIGHT)
    assert not game.can_move(Sokoban.DOWN)
    assert len(game.history) == 4

    game = Sokoban()

    for position in game.find_path(SokobanVector(2, 2)):
        game.move(position - game.player)

    assert not game.is_solved()

    for i in range(3):
        game.move(Sokoban.RIGHT)

    assert game.is_solved()
    assert game.nrow == 5 and game.ncol == 10
    assert game.nmove == 9 and game.npush == 3
    assert len(game.history) == 9
