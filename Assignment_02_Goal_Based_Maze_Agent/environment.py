"""
Maze environment for the goal-based search agent.
"""

import random

from config import (
    GRID_WIDTH,
    GRID_HEIGHT,
    DEFAULT_OBSTACLE_DENSITY,
    MAX_GENERATION_ATTEMPTS,
)


class MazeEnvironment:
    """
    Represents a 2D maze environment.

    Cells can either be:
        0 -> free
        1 -> obstacle
    """

    FREE = 0
    OBSTACLE = 1

    def __init__(
        self,
        width=GRID_WIDTH,
        height=GRID_HEIGHT,
        obstacle_density=DEFAULT_OBSTACLE_DENSITY,
    ):
        self.width = width
        self.height = height
        self.obstacle_density = obstacle_density

        self.start = (0, 0)
        self.goal = (
            self.width - 1,
            self.height - 1,
        )

        self.grid = []

        self.generate_random_maze()

    def generate_random_maze(self):
        """
        Generate a random maze.

        The method keeps generating until a solvable
        maze is produced or the maximum number of
        attempts is reached.
        """

        for _ in range(MAX_GENERATION_ATTEMPTS):

            self.grid = [
                [
                    self.OBSTACLE
                    if random.random()
                    < self.obstacle_density
                    else self.FREE
                    for _ in range(self.width)
                ]
                for _ in range(self.height)
            ]

            self.grid[
                self.start[1]
            ][self.start[0]] = self.FREE

            self.grid[
                self.goal[1]
            ][self.goal[0]] = self.FREE

            if self._has_basic_path():

                return

        self.generate_default_maze()

    def generate_default_maze(self):
        """
        Generate a guaranteed-solvable maze.
        """

        self.grid = [
            [self.FREE for _ in range(self.width)]
            for _ in range(self.height)
        ]

        # Create some structured obstacles.
        for y in range(2, self.height - 2):

            if y != 6:

                self.grid[y][4] = self.OBSTACLE

        for y in range(3, self.height - 1):

            if y != 10:

                self.grid[y][9] = self.OBSTACLE

        for x in range(5, self.width - 2):

            if x != 11:

                self.grid[8][x] = self.OBSTACLE

        self.grid[
            self.start[1]
        ][self.start[0]] = self.FREE

        self.grid[
            self.goal[1]
        ][self.goal[0]] = self.FREE

    def _has_basic_path(self):
        """
        Basic BFS used internally to check whether
        the generated maze is solvable.

        This is environment validation, not the agent's
        public search implementation.
        """

        queue = [self.start]

        visited = {self.start}

        while queue:

            current = queue.pop(0)

            if current == self.goal:
                return True

            for neighbor in self.get_neighbors(current):

                if (
                    neighbor not in visited
                    and self.is_walkable(neighbor)
                ):

                    visited.add(neighbor)

                    queue.append(neighbor)

        return False

    def is_inside(self, position):
        """
        Check whether a coordinate is inside the maze.
        """

        x, y = position

        return (
            0 <= x < self.width
            and 0 <= y < self.height
        )

    def is_walkable(self, position):
        """
        Check whether a position is inside the maze
        and not an obstacle.
        """

        if not self.is_inside(position):
            return False

        x, y = position

        return (
            self.grid[y][x]
            == self.FREE
        )

    def get_neighbors(self, position):
        """
        Return neighboring positions.

        Order is fixed so BFS/DFS results are reproducible.
        """

        x, y = position

        possible_moves = [
            (x, y - 1),  # UP
            (x + 1, y),  # RIGHT
            (x, y + 1),  # DOWN
            (x - 1, y),  # LEFT
        ]

        return [
            neighbor
            for neighbor in possible_moves
            if self.is_inside(neighbor)
        ]

    def get_movable_neighbors(self, position):
        """
        Return only walkable neighbors.
        """

        return [
            neighbor
            for neighbor in self.get_neighbors(position)
            if self.is_walkable(neighbor)
        ]

    def set_grid(self, grid):
        """
        Set a custom grid.

        Useful for testing.
        """

        height = len(grid)

        if height == 0:
            raise ValueError(
                "Grid cannot be empty."
            )

        width = len(grid[0])

        if any(
            len(row) != width
            for row in grid
        ):
            raise ValueError(
                "All grid rows must have equal length."
            )

        self.grid = [
            list(row)
            for row in grid
        ]

        self.height = height
        self.width = width

        self.start = (0, 0)

        self.goal = (
            width - 1,
            height - 1,
        )

        self.grid[0][0] = self.FREE

        self.grid[
            height - 1
        ][
            width - 1
        ] = self.FREE