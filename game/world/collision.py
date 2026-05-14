# generated file

from game.world.map import is_wall
from game.world.config import PLAYER_SIZE


def can_move_to(x, y):

    half = PLAYER_SIZE / 2

    points = [
        (x - half, y - half),
        (x + half, y - half),
        (x - half, y + half),
        (x + half, y + half),
    ]

    for px, py in points:

        if is_wall(px, py):
            return False

    return True


def move_with_collision(
    entity,
    dx,
    dy,
):

    new_x = entity.x + dx

    if can_move_to(
        new_x,
        entity.y,
    ):
        entity.x = new_x

    new_y = entity.y + dy

    if can_move_to(
        entity.x,
        new_y,
    ):
        entity.y = new_y