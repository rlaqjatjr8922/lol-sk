# generated file

import importlib

from game.ai_env.observation import build_observation
from game.ai_env.action import action_to_move
from game.world.collision import move_with_collision


class Character:

    def __init__(
        self,
        number,
        x,
        y,
        ai_index,
    ):

        self.number = number
        self.name = f"AI {number}"

        self.x = float(x)
        self.y = float(y)

        self.speed = 4.0

        self.hp = 100

        self.alive = True
        self.is_tagger = False

        self.reward = 0.0

        self.tagged_someone = False
        self.got_tagged = False

        self.stun_timer = 0.0

        # AI1 학습 데이터
        self.memory = []

        module = importlib.import_module(
            f"ai.ai_{ai_index}.brain"
        )

        self.brain = module.Brain()

    def update(
        self,
        dt,
        players,
    ):

        if not self.alive:
            return

        # 스턴이면 이동/판단 안 함
        if self.stun_timer > 0:

            self.stun_timer -= dt

            if self.stun_timer < 0:
                self.stun_timer = 0

            return

        obs = build_observation(
            self,
            players,
        )

        action = self.brain.decide(obs)

        dx, dy = action_to_move(action)

        move_with_collision(
            self,
            dx * self.speed * dt,
            dy * self.speed * dt,
        )

        # AI1만 행동 저장
        # reward는 GameManager.apply_rewards()에서 나중에 넣음
        if self.number == 1:

            self.memory.append({
                "obs": obs,
                "action": action,
                "reward": 0.0,
            })

    def reset_flags(self):

        self.tagged_someone = False
        self.got_tagged = False