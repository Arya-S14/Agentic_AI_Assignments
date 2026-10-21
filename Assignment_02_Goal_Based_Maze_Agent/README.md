# Goal-Based Maze Navigation Agent

## 1. Problem Statement

The objective of this project is to implement a goal-based intelligent agent that navigates a two-dimensional maze from a predefined starting state to a target goal state.

The agent uses classical search algorithms to construct a path before executing it.

Two search strategies are implemented:

- Breadth-First Search (BFS)
- Depth-First Search (DFS)

---

## 2. Objective

The objectives of this project are:

- Implement a goal-based intelligent agent.
- Represent a maze as a state space.
- Define initial and goal states.
- Implement BFS.
- Implement DFS.
- Reconstruct the resulting path.
- Visualize search behaviour.
- Compare BFS and DFS.
- Measure search performance.
- Handle obstacles.
- Handle randomized environments.
- Test the implementation automatically.

---

## 3. AI Concept

This project demonstrates a goal-based agent.

Unlike a purely reactive agent, the goal-based agent considers possible future states and performs search to determine a sequence of actions that can achieve the goal.

The basic architecture is:

Current State
↓
Goal
↓
Search
↓
Plan
↓
Action Sequence
↓
Goal

---

## 4. PEAS Description

### Performance Measure

The agent is evaluated using:

- Whether the goal is reached.
- Number of nodes explored.
- Path length.
- Search efficiency.

### Environment

A discrete two-dimensional maze containing:

- Free cells.
- Obstacles.
- Start state.
- Goal state.

### Actuators

The agent can conceptually move:

- UP
- DOWN
- LEFT
- RIGHT

### Sensors

The agent has access to the maze state required for search, including:

- Current position.
- Available neighboring cells.
- Goal position.
- Obstacles.

---

## 5. State Representation

Each grid coordinate represents a state.

For example:

(3, 5)

represents the cell at x = 3 and y = 5.

---

## 6. Actions

From a valid cell, the agent may move:

UP
DOWN
LEFT
RIGHT

provided that the resulting cell is inside the maze and not an obstacle.

---

## 7. Breadth-First Search

BFS explores states level by level.

It uses a queue.

General procedure:

1. Insert the start state into the queue.
2. Remove the first state.
3. Check whether it is the goal.
4. Generate valid neighboring states.
5. Add unexplored states to the queue.
6. Continue until the goal is found or the queue becomes empty.

For an unweighted grid, BFS guarantees a shortest path when one exists.

---

## 8. Depth-First Search

DFS explores one branch as deeply as possible before backtracking.

It uses a stack.

General procedure:

1. Insert the start state into the stack.
2. Remove the top state.
3. Check whether it is the goal.
4. Generate valid neighboring states.
5. Add unexplored states to the stack.
6. Continue until the goal is found or the stack becomes empty.

DFS does not guarantee a shortest path.

---

## 9. BFS vs DFS

| Property | BFS | DFS |
|---|---|---|
| Data structure | Queue | Stack |
| Complete | Yes for finite graph | Yes for finite graph with visited tracking |
| Shortest path in unweighted grid | Yes | No |
| Memory requirement | Usually higher | Usually lower |
| Search behaviour | Level by level | Depth first |
| Path quality | Optimal for unweighted grid | Not necessarily optimal |

---

## 10. Performance Metrics

The implementation measures:

- Success.
- Nodes explored.
- Path length.
- Start position.
- Goal position.

The number of explored states indicates the search effort.

Path length measures the quality of the resulting solution.

---

## 11. Features

- BFS.
- DFS.
- Random maze generation.
- Guaranteed fallback maze.
- Obstacles.
- Goal detection.
- Path reconstruction.
- Search visualization.
- Search animation.
- BFS/DFS comparison.
- Step-by-step path execution.
- Reset functionality.
- New maze generation.
- Terminal mode.
- Graphical interface.
- Automated tests.
- Logging.

---

## 12. Installation

Install the required dependency:

pip install -r requirements.txt

---

## 13. Running

Run:

python main.py

The application provides:

1. BFS terminal simulation.
2. DFS terminal simulation.
3. BFS/DFS comparison.
4. Graphical simulation.

---

## 14. Testing

Run:

pytest

The tests validate:

- Valid states.
- Start and goal states.
- BFS.
- DFS.
- Shortest-path behaviour.
- Obstacles.
- Goal-based agent behaviour.
- Invalid algorithm handling.

---

## 15. Limitations

The current implementation assumes:

- A known maze.
- Deterministic movement.
- Static obstacles.
- A known goal.
- An unweighted grid.

The basic implementation does not include:

- Heuristic search.
- Dynamic obstacles.
- Unknown environments.
- Weighted terrain.
- Learning.

---

## 16. Future Enhancements

Potential extensions include:

- A* search.
- Greedy Best-First Search.
- Weighted terrain.
- Dynamic obstacles.
- Moving goals.
- Partial observability.
- Reinforcement learning.
- LLM-based natural-language maze commands.
- Multi-agent maze navigation.

---

## 17. Conclusion

The project demonstrates a goal-based intelligent agent using classical search algorithms.

The agent identifies a goal state, explores the available state space, constructs a sequence of actions, and uses that sequence to reach the target.

The comparison between BFS and DFS demonstrates the effect of different search strategies on exploration effort and solution quality.