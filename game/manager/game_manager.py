# generated file

import random

from game.world.config import DT
from game.entity.character import Character
from game.ai_env.reward import calculate_reward


class GameManager:

    def __init__(self):

        self.players = []

        self.game_over = False
        self.winner = None

        spawn_points = [
            (1.5, 1.5),
            (5.5, 1.5),
            (1.5, 5.5),
            (5.5, 5.5),
        ]

        random.shuffle(spawn_points)

        for i in range(4):

            x, y = spawn_points[i]

            player = Character(
                number=i + 1,
                x=x,
                y=y,
                ai_index=i + 1,
            )

            self.players.append(player)

        self.tagger = random.choice(self.players)
        self.tagger.is_tagger = True

    def update(self, dt=DT):

        if self.game_over:
            return

        players = self.players

        for player in players:
            player.reset_flags()

        start = random.randrange(len(players))

        for i in range(len(players)):

            player = players[
                (start + i) % len(players)
            ]

            if not player.alive:
                continue

            player.update(
                dt,
                players,
            )

        self.check_tag()
        self.apply_rewards(dt)
        self.check_dead()
        self.check_game_over()

    def check_tag(self):

        tagger = self.tagger

        if not tagger.alive:
            return

        if tagger.stun_timer > 0:
            return

        players = self.players
        start = random.randrange(len(players))

        for i in range(len(players)):

            player = players[
                (start + i) % len(players)
            ]

            if not player.alive:
                continue

            if player == tagger:
                continue

            if self.distance(tagger, player) < 1.5:

                tagger.tagged_someone = True
                player.got_tagged = True

                player.stun_timer = 1.0

                tagger.is_tagger = False
                player.is_tagger = True

                self.tagger = player

                break

    def apply_rewards(self, dt):

        for player in self.players:

            if not player.alive:
                continue

            reward = calculate_reward(
                me=player,
                tagged_someone=player.tagged_someone,
                got_tagged=player.got_tagged,
                dt=dt,
            )

            player.reward += reward

            if (
                player.number == 1
                and len(player.memory) > 0
            ):
                player.memory[-1]["reward"] += reward

    def check_dead(self):

        for player in self.players:

            if player.alive and player.hp <= 0:

                player.alive = False

                if player.is_tagger:

                    player.is_tagger = False

                    alive_players = [
                        p for p in self.players
                        if p.alive
                    ]

                    if alive_players:
                        self.tagger = random.choice(alive_players)
                        self.tagger.is_tagger = True

    def check_game_over(self):

        alive_players = [
            p for p in self.players
            if p.alive
        ]

        if len(alive_players) <= 1:

            self.game_over = True

            if alive_players:
                self.winner = alive_players[0]
            else:
                self.winner = None

    def distance(self, a, b):

        dx = a.x - b.x
        dy = a.y - b.y

        return (
            dx * dx
            + dy * dy
        ) ** 0.5