"""
Automated tests for BFS, DFS and the goal-based agent.
"""

from environment import MazeEnvironment
from search import SearchAlgorithms
from agent import GoalBasedAgent


def test_start_and_goal_are_walkable():

    environment = MazeEnvironment()

    assert environment.is_walkable(
        environment.start
    )

    assert environment.is_walkable(
        environment.goal
    )


def test_bfs_finds_simple_path():

    environment = MazeEnvironment(
        width=3,
        height=3,
        obstacle_density=0,
    )

    result = SearchAlgorithms.bfs(
        environment
    )

    assert result.success

    assert result.path[0] == (
        0,
        0,
    )

    assert result.path[-1] == (
        2,
        2,
    )


def test_bfs_shortest_path():

    environment = MazeEnvironment(
        width=3,
        height=3,
        obstacle_density=0,
    )

    result = SearchAlgorithms.bfs(
        environment
    )

    assert result.path_length == 4


def test_dfs_finds_path():

    environment = MazeEnvironment(
        width=3,
        height=3,
        obstacle_density=0,
    )

    result = SearchAlgorithms.dfs(
        environment
    )

    assert result.success

    assert result.path[0] == (
        0,
        0,
    )

    assert result.path[-1] == (
        2,
        2,
    )


def test_bfs_and_dfs_success():

    environment = MazeEnvironment(
        width=5,
        height=5,
        obstacle_density=0,
    )

    bfs_result = (
        SearchAlgorithms.bfs(
            environment
        )
    )

    dfs_result = (
        SearchAlgorithms.dfs(
            environment
        )
    )

    assert bfs_result.success

    assert dfs_result.success


def test_obstacles_are_respected():

    environment = MazeEnvironment(
        width=3,
        height=3,
        obstacle_density=0,
    )

    custom_grid = [
        [0, 1, 0],
        [0, 1, 0],
        [0, 0, 0],
    ]

    environment.set_grid(
        custom_grid
    )

    result = SearchAlgorithms.bfs(
        environment
    )

    assert result.success

    for position in result.path:

        x, y = position

        assert custom_grid[y][x] == 0


def test_goal_based_agent():

    environment = MazeEnvironment(
        width=4,
        height=4,
        obstacle_density=0,
    )

    agent = GoalBasedAgent()

    result = agent.search(
        environment,
        "BFS",
    )

    assert result.success

    assert agent.success

    assert (
        agent.get_path_length()
        == 6
    )


def test_invalid_algorithm():

    environment = MazeEnvironment(
        width=3,
        height=3,
        obstacle_density=0,
    )

    agent = GoalBasedAgent()

    try:

        agent.search(
            environment,
            "INVALID",
        )

        assert False

    except ValueError:

        assert True