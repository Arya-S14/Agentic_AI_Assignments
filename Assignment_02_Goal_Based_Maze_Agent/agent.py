"""
Goal-based maze navigation agent.
"""

import logging

from search import SearchAlgorithms


class GoalBasedAgent:

    def __init__(self):

        self.current_position = None

        self.goal = None

        self.path = []

        self.visited_order = []

        self.algorithm = None

        self.nodes_explored = 0

        self.success = False

        self.path_index = 0

    def search(
        self,
        environment,
        algorithm="BFS",
    ):
        """
        Search for a path to the goal.
        """

        algorithm = algorithm.upper()

        self.current_position = (
            environment.start
        )

        self.goal = environment.goal

        self.algorithm = algorithm

        self.path_index = 0

        if algorithm == "BFS":

            result = (
                SearchAlgorithms.bfs(
                    environment
                )
            )

        elif algorithm == "DFS":

            result = (
                SearchAlgorithms.dfs(
                    environment
                )
            )

        else:

            raise ValueError(
                "Algorithm must be BFS or DFS."
            )

        self.path = result.path

        self.visited_order = (
            result.visited_order
        )

        self.nodes_explored = (
            result.nodes_explored
        )

        self.success = result.success

        logging.info(
            "Algorithm=%s | Success=%s | "
            "Nodes=%s | Path Length=%s",
            algorithm,
            result.success,
            result.nodes_explored,
            result.path_length,
        )

        return result

    def reset(self):

        self.current_position = None

        self.goal = None

        self.path = []

        self.visited_order = []

        self.algorithm = None

        self.nodes_explored = 0

        self.success = False

        self.path_index = 0

    def get_next_position(self):

        if not self.success:
            return None

        if self.path_index >= len(
            self.path
        ) - 1:
            return None

        self.path_index += 1

        self.current_position = (
            self.path[
                self.path_index
            ]
        )

        return self.current_position

    def get_path_length(self):

        if not self.success:
            return 0

        return max(
            len(self.path) - 1,
            0,
        )

    def get_metrics(self):

        return {
            "algorithm": self.algorithm,
            "success": self.success,
            "nodes_explored": self.nodes_explored,
            "path_length": self.get_path_length(),
            "start": self.path[0]
            if self.path
            else None,
            "goal": self.path[-1]
            if self.path
            else self.goal,
        }