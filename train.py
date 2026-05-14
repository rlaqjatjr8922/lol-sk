# generated file

import torch
import torch.nn.functional as F

from game.manager.game_manager import GameManager
from game.world.config import DT
from ai.ai_1.trainer import Trainer


def get_ai1(game):

    for player in game.players:

        if player.number == 1:
            return player

    return None


def main():

    trainer = Trainer()

    trainer.load()

    game_count = 0

    while True:

        game_count += 1

        game = GameManager()

        while not game.game_over:

            game.update(DT)

        ai1 = get_ai1(game)

        if ai1 and len(ai1.memory) > 0:

            steps = ai1.memory

            loss = trainer.train_episode(
                steps,
                game_count,
            )

            trainer.save()

            with torch.no_grad():

                seq = trainer.build_seq_from_steps(
                    steps,
                    len(steps) - 1,
                )

                x = torch.tensor(
                    seq,
                    dtype=torch.float32,
                )

                logits = trainer.model(x)

                probs = F.softmax(
                    logits,
                    dim=-1,
                )

            probs = probs.tolist()

            max_prob = max(probs)

            min_prob = min(probs)

            steps_count = len(steps)

        else:

            loss = 0.0

            max_prob = 0.0

            min_prob = 0.0

            steps_count = 0

        winner_name = (
            game.winner.name
            if game.winner
            else "None"
        )

        print(
            f"[GAME] "
            f"{game_count}판 "
            f"winner={winner_name} "
            f"steps={steps_count} "
            f"loss={loss:.4f} "
            f"max={max_prob:.6f} "
            f"min={min_prob:.6f} "
            f"episodes={len(trainer.replay_buffer)}"
        )


if __name__ == "__main__":

    main()