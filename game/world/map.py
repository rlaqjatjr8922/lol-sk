# generated file

from game.world.config import (
    MAP_WIDTH,
    MAP_HEIGHT,
)


# 0 = 빈칸
# 1 = 벽
MAP_DATA = [
    1,1,1,1,1,1,1,
    1,0,0,0,0,0,1,
    1,0,0,0,0,0,1,
    1,0,0,0,0,0,1,
    1,0,0,0,0,0,1,
    1,0,0,0,0,0,1,
    1,1,1,1,1,1,1,
]


def in_bounds(x, y):

    return (
        0 <= x < MAP_WIDTH
        and 0 <= y < MAP_HEIGHT
    )


def get_index(x, y):

    return y * MAP_WIDTH + x


def get_tile(x, y):

    x = int(x)
    y = int(y)

    if not in_bounds(x, y):
        return 1

    return MAP_DATA[
        get_index(x, y)
    ]


def set_tile(x, y, value):

    x = int(x)
    y = int(y)

    if not in_bounds(x, y):
        return

    MAP_DATA[
        get_index(x, y)
    ] = value


def is_wall(x, y):

    return get_tile(x, y) == 1