# generated file

import os

import torch
import torch.nn as nn
import torch.nn.functional as F


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "model.pt",
)

OBS_SIZE = 61
ACTION_SIZE = 9
MAX_SEQ_LEN = 256
EMBED_SIZE = 128
NHEAD = 4
NUM_LAYERS = 2


class PolicyNet(nn.Module):

    def __init__(self):

        super().__init__()

        self.input_layer = nn.Linear(
            OBS_SIZE,
            EMBED_SIZE,
        )

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=EMBED_SIZE,
            nhead=NHEAD,
            dim_feedforward=256,
            batch_first=True,
        )

        self.transformer = nn.TransformerEncoder(
            encoder_layer,
            num_layers=NUM_LAYERS,
        )

        self.output_layer = nn.Sequential(
            nn.Linear(EMBED_SIZE, 128),
            nn.ReLU(),
            nn.Linear(128, ACTION_SIZE),
        )

    def forward(self, x):

        if x.dim() == 2:
            x = x.unsqueeze(0)

        x = self.input_layer(x)

        x = self.transformer(x)

        last = x[:, -1, :]

        logits = self.output_layer(last)

        return logits.squeeze(0)


class Brain:

    def __init__(self):

        self.model = PolicyNet()
        self.model.eval()

        self.seq_tensor = torch.zeros(
            MAX_SEQ_LEN,
            OBS_SIZE,
            dtype=torch.float32,
        )

        self.ordered_tensor = torch.zeros(
            MAX_SEQ_LEN,
            OBS_SIZE,
            dtype=torch.float32,
        )

        self.obs_tensor = torch.zeros(
            OBS_SIZE,
            dtype=torch.float32,
        )

        self.ptr = 0
        self.count = 0

        self.load_model()

    def load_model(self):

        if os.path.exists(MODEL_PATH):

            try:

                try:
                    state = torch.load(
                        MODEL_PATH,
                        map_location="cpu",
                        weights_only=True,
                    )
                except TypeError:
                    state = torch.load(
                        MODEL_PATH,
                        map_location="cpu",
                    )

                self.model.load_state_dict(state)

                print("[AI1] model loaded")

            except Exception:

                print("[AI1] model mismatch -> new model")

        else:

            print("[AI1] new model")

    def update_sequence(self, obs):

        self.obs_tensor.copy_(
            torch.as_tensor(
                obs,
                dtype=torch.float32,
            )
        )

        self.seq_tensor[self.ptr].copy_(
            self.obs_tensor
        )

        self.ptr = (
            self.ptr + 1
        ) % MAX_SEQ_LEN

        if self.count < MAX_SEQ_LEN:
            self.count += 1

    def build_ordered_sequence(self):

        self.ordered_tensor.zero_()

        if self.count <= 0:
            return self.ordered_tensor

        if self.count < MAX_SEQ_LEN:

            self.ordered_tensor[
                -self.count:
            ].copy_(
                self.seq_tensor[
                    :self.count
                ]
            )

        else:

            first_len = MAX_SEQ_LEN - self.ptr

            self.ordered_tensor[
                :first_len
            ].copy_(
                self.seq_tensor[
                    self.ptr:
                ]
            )

            if self.ptr > 0:

                self.ordered_tensor[
                    first_len:
                ].copy_(
                    self.seq_tensor[
                        :self.ptr
                    ]
                )

        return self.ordered_tensor

    def decide(self, obs):

        if len(obs) != OBS_SIZE:

            raise ValueError(
                f"[AI1] obs size mismatch: {len(obs)} != {OBS_SIZE}"
            )

        self.update_sequence(obs)

        seq = self.build_ordered_sequence()

        with torch.inference_mode():

            logits = self.model(
                seq
            )

            probs = F.softmax(
                logits,
                dim=-1,
            )

            action = torch.multinomial(
                probs,
                num_samples=1,
            ).item()

        return action