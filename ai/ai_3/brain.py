# generated file

import random


class Brain:

    def __init__(self):

        self.action = random.randint(0, 8)
        self.timer = random.randint(20, 60)

    def decide(self, obs):

        self.timer -= 1

        if self.timer <= 0:

            self.action = random.randint(0, 8)
            self.timer = random.randint(20, 60)

        return self.action