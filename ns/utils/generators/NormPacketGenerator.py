import random


class NormPacketGenerator:
    def __init__(self, mu, sigma, min_x, max_x):
        self.mu = mu
        self.sigma = sigma
        self.min_x = min_x
        self.max_x = max_x
        self.gen = self.norm_generator()

    def get_next(self):
        return next(self.gen)

    def norm_generator(self):
        while True:
            rand = random.gauss(self.mu, self.sigma)
            if self.min_x <= rand <= self.max_x:
                yield rand
