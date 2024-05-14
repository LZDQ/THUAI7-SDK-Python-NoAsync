from typing import Optional, Tuple
import numpy as np

from agent.agent_hack import Agent
from agent.messages import Position

from utils import *

class Glitch2Pow:

    def __init__(self, agent: Agent):
        """
        x should be 2^k
        y is arbitrary
        This class manages to spawn at (x-eps, y) and glitch into (x, y)
        Please make sure that (x-1, y) is not wall
        """
        self.agent = agent

    def choose_origin(self, wall: Optional[Tuple[int, int]] = None):
        if not wall:
            x = 1
            obstacle = convert_map(self.agent.map)
            y = next(y for y in range(256) if not obstacle[x-1, y] and (x == 256 or obstacle[x, y]))
        else:
            x, y = wall
        self.wall = (x, y)
        self.k = round(np.log2(x))
        x = x - 2.0 ** (self.k-53)
        y = y + 0.5
        self.agent.choose_origin(Position(x, y))
        self.origin = (x, y)
        print(f"Chose origin at {x, y}")

    def move(self):
        x, y = self.origin
        dx = 50 * (2.0 ** (self.k-54-3))
        dy = 0.125
        nx, ny = x+dx, y+dy
        self.agent.move(Position(nx, ny))
        print(f"Trying glitch at {nx, ny}")
