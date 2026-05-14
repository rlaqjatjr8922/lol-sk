# generated file

import os

import torch
import torch.nn.functional as F

from torch.optim import Adam

from ai.ai_1.brain import (
    PolicyNet,
    OBS_SIZE,
    MAX_SEQ_LEN,
)

from ai.ai_1.memory import ReplayBuffer


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "model.pt",
)

ENTROPY_WEIGHT = 0.01
LR = 0.0001


class Trainer:

    def __init__(self):

        self.model = PolicyNet()

        self.optimizer = Adam(
            self.model.parameters(),
            lr=LR,
        )

        self.replay_buffer = ReplayBuffer(
            max_size=10,
        )

    def build_seq_from_steps(
        self,
        steps,
        index,
    ):

        seq_tensor = torch.zeros(
            MAX_SEQ_LEN,
            OBS_SIZE,
            dtype=torch.float32,
        )

        start = max(
            0,
            index - MAX_SEQ_LEN + 1,
        )

        real_seq = [
            step["obs"]
            for step in steps[start:index + 1]
        ]

        if len(real_seq) > 0:

            real_tensor = torch.as_tensor(
                real_seq,
                dtype=torch.float32,
            )

            seq_tensor[-len(real_seq):] = real_tensor

        return seq_tensor

    def train_steps(
        self,
        steps,
        entropy_weight=ENTROPY_WEIGHT,
    ):

        if len(steps) <= 0:
            return 0.0

        advantages = torch.tensor(
            [
                step["reward"]
                for step in steps
            ],
            dtype=torch.float32,
        )

        if len(advantages) > 1:

            advantages = (
                advantages - advantages.mean()
            ) / (
                advantages.std() + 1e-8
            )

        total_loss = 0.0

        self.optimizer.zero_grad()

        for index, step in enumerate(steps):

            obs_seq = self.build_seq_from_steps(
                steps,
                index,
            )

            action = torch.tensor(
                step["action"],
                dtype=torch.long,
            )

            advantage = advantages[index]

            logits = self.model(
                obs_seq
            )

            probs = F.softmax(
                logits,
                dim=-1,
            )

            log_probs = F.log_softmax(
                logits,
                dim=-1,
            )

            log_prob = log_probs[
                action
            ]

            policy_loss = -(
                log_prob * advantage
            )

            entropy = -(
                probs * torch.log(
                    probs + 1e-8
                )
            ).sum()

            loss = (
                policy_loss
                - entropy_weight * entropy
            )

            total_loss = total_loss + loss

        avg_loss = (
            total_loss / len(steps)
        )

        avg_loss.backward()

        torch.nn.utils.clip_grad_norm_(
            self.model.parameters(),
            max_norm=1.0,
        )

        self.optimizer.step()

        return avg_loss.item()

    def train_episode(
        self,
        steps,
        game_count,
    ):

        if len(steps) <= 0:
            return 0.0

        loss = self.train_steps(
            steps,
            entropy_weight=ENTROPY_WEIGHT,
        )

        self.replay_buffer.add_episode(
            steps
        )

        if game_count % 10 == 0:

            replay_steps = self.replay_buffer.sample_episode()

            replay_loss = self.train_steps(
                replay_steps,
                entropy_weight=ENTROPY_WEIGHT,
            )

            print(
                f"[REPLAY] replay_loss={replay_loss:.4f}"
            )

        return loss

    def save(self):

        os.makedirs(
            BASE_DIR,
            exist_ok=True,
        )

        torch.save(
            self.model.state_dict(),
            MODEL_PATH,
        )

        self.replay_buffer.save()

        print("[AI1] model saved")

    def load(self):

        try:

            self.model.load_state_dict(
                torch.load(
                    MODEL_PATH,
                    map_location="cpu",
                )
            )

            print("[AI1] model loaded")

        except Exception:

            print("[AI1] new model")