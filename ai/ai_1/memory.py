# generated file

import os
import pickle
import random


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

BUFFER_PATH = os.path.join(
    BASE_DIR,
    "replay_buffer.pkl",
)


class ReplayBuffer:

    def __init__(
        self,
        max_size=10000,
    ):

        self.max_size = max_size

        self.episodes = []

        self.load()

    def add_episode(
        self,
        steps,
    ):

        self.episodes.append(
            steps
        )

        if len(self.episodes) > self.max_size:

            self.episodes = self.episodes[
                -self.max_size:
            ]

    def sample_episode(self):

        if len(self.episodes) <= 0:
            return []

        return random.choice(
            self.episodes
        )

    def save(self):

        with open(
            BUFFER_PATH,
            "wb",
        ) as f:

            pickle.dump(
                self.episodes,
                f,
            )

        print(
            f"[AI1] replay saved "
            f"episodes={len(self.episodes)}"
        )

    def load(self):

        if not os.path.exists(BUFFER_PATH):
            return

        try:

            with open(
                BUFFER_PATH,
                "rb",
            ) as f:

                self.episodes = pickle.load(f)

            print(
                f"[AI1] replay loaded "
                f"episodes={len(self.episodes)}"
            )

        except Exception:

            self.episodes = []

            print(
                "[AI1] replay load failed"
            )

    def __len__(self):

        return len(self.episodes)