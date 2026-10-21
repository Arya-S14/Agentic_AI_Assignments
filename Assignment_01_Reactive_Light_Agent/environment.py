"""
2D grid environment for the reactive agent.
"""

import random

from config import (
    GRID_WIDTH,
    GRID_HEIGHT,
    EMPTY_SYMBOL,
    AGENT_SYMBOL,
    LIGHT_SYMBOL,
)


class Environment:
    """
    Represents the 2D world in which the agent operates.
    """

    ACTIONS = {
        "UP": (0, -1),
        "DOWN": (0, 1),
        "LEFT": (-1, 0),
        "RIGHT": (1, 0),
        "STAY": (0, 0),
    }

    def __init__(self, width=GRID_WIDTH, height=GRID_HEIGHT):
        self.width = width
        self.height = height

        self.agent_position = (0, 0)
        self.light_position = (width - 1, height - 1)

    def set_positions(self, agent_position, light_position):
        """
        Set the positions of the agent and light.
        """

        if not self.is_valid_position(agent_position):
            raise ValueError(
                f"Invalid agent position: {agent_position}"
            )

        if not self.is_valid_position(light_position):
            raise ValueError(
                f"Invalid light position: {light_position}"
            )

        self.agent_position = agent_position
        self.light_position = light_position

    def randomize_positions(self):
        """
        Randomly place the agent and light on different cells.
        """

        self.agent_position = self._random_position()

        self.light_position = self._random_position()

        while self.light_position == self.agent_position:
            self.light_position = self._random_position()

    def _random_position(self):
        """
        Generate a random valid grid position.
        """

        return (
            random.randint(0, self.width - 1),
            random.randint(0, self.height - 1),
        )

    def is_valid_position(self, position):
        """
        Check whether a position lies within the grid.
        """

        x, y = position

        return (
            0 <= x < self.width
            and 0 <= y < self.height
        )

    def get_new_position(self, action):
        """
        Calculate the position resulting from an action.
        """

        if action not in self.ACTIONS:
            raise ValueError(f"Unknown action: {action}")

        dx, dy = self.ACTIONS[action]

        x, y = self.agent_position

        return x + dx, y + dy

    def move_agent(self, action):
        """
        Attempt to move the agent.

        Returns:
            True  -> movement was successful
            False -> movement was invalid
        """

        new_position = self.get_new_position(action)

        if not self.is_valid_position(new_position):
            return False

        self.agent_position = new_position

        return True

    def target_reached(self):
        """
        Determine whether the agent has reached the light.
        """

        return self.agent_position == self.light_position

    def manhattan_distance(self):
        """
        Calculate Manhattan distance between agent and light.
        """

        ax, ay = self.agent_position
        lx, ly = self.light_position

        return abs(lx - ax) + abs(ly - ay)

    def get_grid(self):
        """
        Return a 2D representation of the environment.
        """

        grid = [
            [EMPTY_SYMBOL for _ in range(self.width)]
            for _ in range(self.height)
        ]

        ax, ay = self.agent_position
        lx, ly = self.light_position

        grid[ay][ax] = AGENT_SYMBOL
        grid[ly][lx] = LIGHT_SYMBOL

        return grid

    def display(self):
        """
        Display the environment in the terminal.
        """

        print()

        grid = self.get_grid()

        for row in grid:
            print(" ".join(row))

        print()