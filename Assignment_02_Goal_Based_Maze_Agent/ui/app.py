"""
Graphical interface for the Goal-Based Maze Agent.
"""

import tkinter as tk
from tkinter import ttk

from agent import GoalBasedAgent
from environment import MazeEnvironment
from config import (
    GRID_WIDTH,
    GRID_HEIGHT,
    CELL_SIZE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    ANIMATION_DELAY,
)


class MazeAgentGUI:

    def __init__(self, root):

        self.root = root

        self.root.title(
            WINDOW_TITLE
        )

        self.root.resizable(
            False,
            False,
        )

        self.environment = (
            MazeEnvironment()
        )

        self.agent = (
            GoalBasedAgent()
        )

        self.selected_algorithm = "BFS"

        self.visited_animation = []

        self.path_animation = []

        self.animation_index = 0

        self.path_index = 0

        self.running = False

        self.animation_phase = "idle"

        self.create_interface()

        self.draw_maze()

        self.update_information()

    def create_interface(self):

        main_frame = ttk.Frame(
            self.root
        )

        main_frame.pack(
            padx=10,
            pady=10,
        )

        title = ttk.Label(
            main_frame,
            text=(
                "GOAL-BASED MAZE "
                "NAVIGATION AGENT"
            ),
            font=(
                "Arial",
                18,
                "bold",
            ),
        )

        title.pack(
            pady=5
        )

        content = ttk.Frame(
            main_frame
        )

        content.pack()

        self.canvas = tk.Canvas(
            content,
            width=GRID_WIDTH * CELL_SIZE,
            height=GRID_HEIGHT * CELL_SIZE,
            bg="white",
        )

        self.canvas.grid(
            row=0,
            column=0,
            rowspan=2,
            padx=10,
        )

        control_frame = ttk.Frame(
            content
        )

        control_frame.grid(
            row=0,
            column=1,
            sticky="n",
            padx=10,
        )

        ttk.Label(
            control_frame,
            text="Search Algorithm",
            font=(
                "Arial",
                11,
                "bold",
            ),
        ).pack(
            pady=(0, 5)
        )

        self.algorithm_combo = ttk.Combobox(
            control_frame,
            values=[
                "BFS",
                "DFS",
            ],
            state="readonly",
            width=15,
        )

        self.algorithm_combo.set(
            "BFS"
        )

        self.algorithm_combo.pack(
            pady=5
        )

        self.algorithm_combo.bind(
            "<<ComboboxSelected>>",
            self.change_algorithm,
        )

        ttk.Button(
            control_frame,
            text="SOLVE",
            command=self.solve,
            width=18,
        ).pack(
            pady=5
        )

        ttk.Button(
            control_frame,
            text="COMPARE BFS / DFS",
            command=self.compare,
            width=18,
        ).pack(
            pady=5
        )

        ttk.Button(
            control_frame,
            text="STEP",
            command=self.step,
            width=18,
        ).pack(
            pady=5
        )

        ttk.Button(
            control_frame,
            text="NEW MAZE",
            command=self.new_maze,
            width=18,
        ).pack(
            pady=5
        )

        ttk.Button(
            control_frame,
            text="RESET",
            command=self.reset,
            width=18,
        ).pack(
            pady=5
        )

        ttk.Separator(
            control_frame,
            orient="horizontal",
        ).pack(
            fill="x",
            pady=10,
        )

        self.algorithm_label = ttk.Label(
            control_frame,
            text="Algorithm: BFS",
        )

        self.algorithm_label.pack(
            pady=3
        )

        self.start_label = ttk.Label(
            control_frame,
            text="",
        )

        self.start_label.pack(
            pady=3
        )

        self.goal_label = ttk.Label(
            control_frame,
            text="",
        )

        self.goal_label.pack(
            pady=3
        )

        self.explored_label = ttk.Label(
            control_frame,
            text="",
        )

        self.explored_label.pack(
            pady=3
        )

        self.path_label = ttk.Label(
            control_frame,
            text="",
        )

        self.path_label.pack(
            pady=3
        )

        self.status_label = ttk.Label(
            control_frame,
            text="",
            font=(
                "Arial",
                11,
                "bold",
            ),
        )

        self.status_label.pack(
            pady=10
        )

        legend = ttk.Label(
            control_frame,
            text=(
                "S = Start\n"
                "G = Goal\n"
                "# = Obstacle\n"
                "+ = Explored\n"
                "* = Final Path"
            ),
            justify="left",
        )

        legend.pack(
            pady=10
        )

    def change_algorithm(
        self,
        event=None,
    ):

        self.selected_algorithm = (
            self.algorithm_combo.get()
        )

        self.algorithm_label.config(
            text=(
                f"Algorithm: "
                f"{self.selected_algorithm}"
            )
        )

        self.reset()

    def draw_maze(
        self,
        explored=None,
        path=None,
    ):

        explored = set(
            explored or []
        )

        path = set(
            path or []
        )

        self.canvas.delete(
            "all"
        )

        for y in range(
            GRID_HEIGHT
        ):

            for x in range(
                GRID_WIDTH
            ):

                position = (x, y)

                x1 = x * CELL_SIZE
                y1 = y * CELL_SIZE

                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                if not self.environment.is_walkable(
                    position
                ):

                    fill = "black"

                elif position in path:

                    fill = "green"

                elif position in explored:

                    fill = "lightblue"

                else:

                    fill = "white"

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=fill,
                    outline="gray",
                )

        sx, sy = (
            self.environment.start
        )

        gx, gy = (
            self.environment.goal
        )

        self.canvas.create_oval(
            sx * CELL_SIZE + 8,
            sy * CELL_SIZE + 8,
            (sx + 1) * CELL_SIZE - 8,
            (sy + 1) * CELL_SIZE - 8,
            fill="blue",
        )

        self.canvas.create_text(
            sx * CELL_SIZE
            + CELL_SIZE / 2,
            sy * CELL_SIZE
            + CELL_SIZE / 2,
            text="S",
            fill="white",
            font=(
                "Arial",
                14,
                "bold",
            ),
        )

        self.canvas.create_oval(
            gx * CELL_SIZE + 8,
            gy * CELL_SIZE + 8,
            (gx + 1) * CELL_SIZE - 8,
            (gy + 1) * CELL_SIZE - 8,
            fill="gold",
        )

        self.canvas.create_text(
            gx * CELL_SIZE
            + CELL_SIZE / 2,
            gy * CELL_SIZE
            + CELL_SIZE / 2,
            text="G",
            fill="black",
            font=(
                "Arial",
                14,
                "bold",
            ),
        )

    def update_information(self):

        self.start_label.config(
            text=(
                f"Start: "
                f"{self.environment.start}"
            )
        )

        self.goal_label.config(
            text=(
                f"Goal: "
                f"{self.environment.goal}"
            )
        )

        self.explored_label.config(
            text=(
                f"Nodes explored: "
                f"{self.agent.nodes_explored}"
            )
        )

        self.path_label.config(
            text=(
                f"Path length: "
                f"{self.agent.get_path_length()}"
            )
        )

        if self.agent.success:

            status = "GOAL FOUND"

        elif self.running:

            status = "SEARCHING..."

        else:

            status = "READY"

        self.status_label.config(
            text=(
                f"Status: {status}"
            )
        )

    def solve(self):

        self.running = False

        self.agent.reset()

        self.selected_algorithm = (
            self.algorithm_combo.get()
        )

        result = self.agent.search(
            self.environment,
            self.selected_algorithm,
        )

        self.visited_animation = (
            result.visited_order
        )

        self.path_animation = (
            result.path
        )

        self.animation_index = 0

        self.path_index = 0

        self.running = True

        self.animate_search()

    def animate_search(self):

        if not self.running:

            return

        if (
            self.animation_index
            < len(
                self.visited_animation
            )
        ):

            current_explored = (
                self.visited_animation[
                    : self.animation_index + 1
                ]
            )

            self.draw_maze(
                explored=current_explored
            )

            self.animation_index += 1

            self.update_information()

            self.root.after(
                ANIMATION_DELAY,
                self.animate_search,
            )

            return

        self.running = False

        self.draw_maze(
            explored=self.visited_animation,
            path=self.path_animation,
        )

        self.update_information()

    def step(self):

        if not self.agent.path:

            self.agent.search(
                self.environment,
                self.selected_algorithm,
            )

        next_position = (
            self.agent.get_next_position()
        )

        if next_position is None:

            self.draw_maze(
                path=self.agent.path
            )

            self.update_information()

            return

        path_so_far = (
            self.agent.path[
                : self.agent.path_index + 1
            ]
        )

        self.draw_maze(
            path=path_so_far
        )

        self.update_information()

    def compare(self):

        bfs_agent = (
            GoalBasedAgent()
        )

        dfs_agent = (
            GoalBasedAgent()
        )

        bfs_result = bfs_agent.search(
            self.environment,
            "BFS",
        )

        dfs_result = dfs_agent.search(
            self.environment,
            "DFS",
        )

        message = (
            "BFS vs DFS\n\n"
            f"BFS:\n"
            f"  Success: "
            f"{bfs_result.success}\n"
            f"  Nodes explored: "
            f"{bfs_result.nodes_explored}\n"
            f"  Path length: "
            f"{bfs_result.path_length}\n\n"
            f"DFS:\n"
            f"  Success: "
            f"{dfs_result.success}\n"
            f"  Nodes explored: "
            f"{dfs_result.nodes_explored}\n"
            f"  Path length: "
            f"{dfs_result.path_length}"
        )

        self.status_label.config(
            text=message
        )

    def new_maze(self):

        self.running = False

        self.environment = (
            MazeEnvironment()
        )

        self.agent.reset()

        self.draw_maze()

        self.update_information()

    def reset(self):

        self.running = False

        self.agent.reset()

        self.draw_maze()

        self.update_information()

    def run(self):

        self.root.mainloop()


def run_gui():

    root = tk.Tk()

    app = MazeAgentGUI(
        root
    )

    app.run()


if __name__ == "__main__":

    run_gui()