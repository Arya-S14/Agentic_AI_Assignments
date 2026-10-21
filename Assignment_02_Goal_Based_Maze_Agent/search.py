"""
Search algorithms for the goal-based maze agent.
"""

from collections import deque
import logging


class SearchResult:

    def __init__(
        self,
        success,
        path,
        visited_order,
        nodes_explored,
        algorithm,
    ):

        self.success = success

        self.path = path

        self.visited_order = visited_order

        self.nodes_explored = nodes_explored

        self.algorithm = algorithm

    @property
    def path_length(self):

        if not self.success:
            return 0

        return max(
            len(self.path) - 1,
            0,
        )


class SearchAlgorithms:

    @staticmethod
    def bfs(environment):

        logging.info(
            "Starting BFS search."
        )

        start = environment.start
        goal = environment.goal

        queue = deque([start])

        visited = {start}

        parent = {
            start: None
        }

        visited_order = []

        while queue:

            current = queue.popleft()

            visited_order.append(
                current
            )

            if current == goal:

                path = SearchAlgorithms._reconstruct_path(
                    parent,
                    goal,
                )

                logging.info(
                    "BFS found goal."
                )

                return SearchResult(
                    success=True,
                    path=path,
                    visited_order=visited_order,
                    nodes_explored=len(
                        visited_order
                    ),
                    algorithm="BFS",
                )

            for neighbor in (
                environment.get_movable_neighbors(
                    current
                )
            ):

                if neighbor not in visited:

                    visited.add(
                        neighbor
                    )

                    parent[
                        neighbor
                    ] = current

                    queue.append(
                        neighbor
                    )

        logging.info(
            "BFS could not find goal."
        )

        return SearchResult(
            success=False,
            path=[],
            visited_order=visited_order,
            nodes_explored=len(
                visited_order
            ),
            algorithm="BFS",
        )

    @staticmethod
    def dfs(environment):

        logging.info(
            "Starting DFS search."
        )

        start = environment.start
        goal = environment.goal

        stack = [start]

        visited = {start}

        parent = {
            start: None
        }

        visited_order = []

        while stack:

            current = stack.pop()

            visited_order.append(
                current
            )

            if current == goal:

                path = SearchAlgorithms._reconstruct_path(
                    parent,
                    goal,
                )

                logging.info(
                    "DFS found goal."
                )

                return SearchResult(
                    success=True,
                    path=path,
                    visited_order=visited_order,
                    nodes_explored=len(
                        visited_order
                    ),
                    algorithm="DFS",
                )

            neighbors = (
                environment.get_movable_neighbors(
                    current
                )
            )

            # Reverse so that the first neighbor
            # in the defined ordering is processed first.
            for neighbor in reversed(
                neighbors
            ):

                if neighbor not in visited:

                    visited.add(
                        neighbor
                    )

                    parent[
                        neighbor
                    ] = current

                    stack.append(
                        neighbor
                    )

        logging.info(
            "DFS could not find goal."
        )

        return SearchResult(
            success=False,
            path=[],
            visited_order=visited_order,
            nodes_explored=len(
                visited_order
            ),
            algorithm="DFS",
        )

    @staticmethod
    def _reconstruct_path(
        parent,
        goal,
    ):

        path = []

        current = goal

        while current is not None:

            path.append(
                current
            )

            current = parent[
                current
            ]

        path.reverse()

        return path