"""
Main entry point for Assignment 2.
"""

import logging
import os

from agent import GoalBasedAgent
from environment import MazeEnvironment
from config import LOG_FILE


def setup_logging():

    os.makedirs(
        os.path.dirname(LOG_FILE),
        exist_ok=True,
    )

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(message)s"
        ),
    )


def print_maze(
    environment,
    path=None,
    visited=None,
):
    """
    Print maze to terminal.

    Symbols:

    S = Start
    G = Goal
    # = Obstacle
    * = Final path
    + = Explored cell
    . = Free cell
    """

    path = set(path or [])
    visited = set(visited or [])

    print()

    for y in range(
        environment.height
    ):

        row = []

        for x in range(
            environment.width
        ):

            position = (x, y)

            if position == environment.start:

                symbol = "S"

            elif position == environment.goal:

                symbol = "G"

            elif position in path:

                symbol = "*"

            elif (
                position in visited
            ):

                symbol = "+"

            elif not environment.is_walkable(
                position
            ):

                symbol = "#"

            else:

                symbol = "."

            row.append(symbol)

        print(" ".join(row))

    print()


def run_single_search(
    algorithm="BFS"
):

    environment = MazeEnvironment()

    agent = GoalBasedAgent()

    result = agent.search(
        environment,
        algorithm,
    )

    print()
    print("=" * 70)
    print(
        f"GOAL-BASED MAZE AGENT - {algorithm}"
    )
    print("=" * 70)

    print(
        f"Start: {environment.start}"
    )

    print(
        f"Goal: {environment.goal}"
    )

    print()

    print_maze(
        environment,
        result.path,
        result.visited_order,
    )

    print(
        f"Algorithm: "
        f"{result.algorithm}"
    )

    print(
        f"Success: "
        f"{result.success}"
    )

    print(
        f"Nodes explored: "
        f"{result.nodes_explored}"
    )

    print(
        f"Path length: "
        f"{result.path_length}"
    )

    if result.success:

        print(
            f"Path: "
            f"{result.path}"
        )

    else:

        print(
            "No path to goal exists."
        )


def compare_algorithms():

    environment = MazeEnvironment()

    bfs_agent = GoalBasedAgent()

    dfs_agent = GoalBasedAgent()

    bfs_result = bfs_agent.search(
        environment,
        "BFS",
    )

    dfs_result = dfs_agent.search(
        environment,
        "DFS",
    )

    print()
    print("=" * 70)
    print("BFS vs DFS COMPARISON")
    print("=" * 70)

    print(
        f"Start: "
        f"{environment.start}"
    )

    print(
        f"Goal: "
        f"{environment.goal}"
    )

    print()

    print(
        f"{'Metric':<25}"
        f"{'BFS':<20}"
        f"{'DFS':<20}"
    )

    print("-" * 65)

    print(
        f"{'Success':<25}"
        f"{str(bfs_result.success):<20}"
        f"{str(dfs_result.success):<20}"
    )

    print(
        f"{'Nodes explored':<25}"
        f"{bfs_result.nodes_explored:<20}"
        f"{dfs_result.nodes_explored:<20}"
    )

    print(
        f"{'Path length':<25}"
        f"{bfs_result.path_length:<20}"
        f"{dfs_result.path_length:<20}"
    )

    print()

    if (
        bfs_result.success
        and dfs_result.success
    ):

        if (
            bfs_result.path_length
            < dfs_result.path_length
        ):

            print(
                "BFS found the shorter path."
            )

        elif (
            dfs_result.path_length
            < bfs_result.path_length
        ):

            print(
                "DFS found the shorter path "
                "for this particular maze."
            )

        else:

            print(
                "Both algorithms found paths "
                "of equal length."
            )

        print()

        print(
            "BFS is guaranteed to find the "
            "shortest path in an unweighted grid."
        )

        print(
            "DFS does not guarantee the shortest path."
        )


def run_gui():

    from ui.app import run_gui as launch_gui

    launch_gui()


def main():

    setup_logging()

    print()
    print("=" * 60)
    print("GOAL-BASED MAZE NAVIGATION AGENT")
    print("=" * 60)

    print()
    print("1. BFS terminal simulation")
    print("2. DFS terminal simulation")
    print("3. Compare BFS and DFS")
    print("4. Graphical simulation")

    choice = input(
        "\nEnter choice (1/2/3/4): "
    ).strip()

    if choice == "1":

        run_single_search(
            "BFS"
        )

    elif choice == "2":

        run_single_search(
            "DFS"
        )

    elif choice == "3":

        compare_algorithms()

    elif choice == "4":

        run_gui()

    else:

        print(
            "Invalid choice."
        )


if __name__ == "__main__":
    main()