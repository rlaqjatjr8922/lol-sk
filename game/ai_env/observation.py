# generated file

from game.world.map import MAP_DATA


def build_observation(
    me,
    players,
):

    obs = []

    obs.extend([
        me.x,
        me.y,
        int(me.is_tagger),
    ])

    alive_others = [
        player for player in players
        if player != me and player.alive
    ]

    while len(alive_others) < 3:
        alive_others.append(None)

    for player in alive_others[:3]:

        if player is None:
            obs.extend([
                -1,
                -1,
                0,
            ])
        else:
            obs.extend([
                player.x,
                player.y,
                int(player.is_tagger),
            ])

    obs.extend(MAP_DATA)

    return obs