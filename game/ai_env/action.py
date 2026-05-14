# generated file

import math


DIAGONAL = 1 / math.sqrt(2)


# action_id:
# 0 = 정지
# 1 = 위
# 2 = 아래
# 3 = 왼쪽
# 4 = 오른쪽
# 5 = 왼위
# 6 = 오른위
# 7 = 왼아래
# 8 = 오른아래
ACTION_TABLE = [
    (0, 0),
    (0, -1),
    (0, 1),
    (-1, 0),
    (1, 0),
    (-DIAGONAL, -DIAGONAL),
    (DIAGONAL, -DIAGONAL),
    (-DIAGONAL, DIAGONAL),
    (DIAGONAL, DIAGONAL),
]


def action_to_move(action_id):

    if action_id < 0 or action_id >= len(ACTION_TABLE):
        return 0, 0

    return ACTION_TABLE[action_id]