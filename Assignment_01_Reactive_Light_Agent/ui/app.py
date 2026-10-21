"""
Graphical interface for the Reactive Light-Seeking Agent.
"""

import tkinter as tk
from tkinter import ttk

from agent import ReactiveAgent
from environment import Environment
from config import (
    GRID_WIDTH,
    GRID_HEIGHT,
    CELL_SIZE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
)


class ReactiveAgentGUI:

    def __init__(self, root):

        self.root = root

        self.root.title(
            WINDOW_TITLE
        )

        self.root.resizable(
            False,
            False,
        )

        self.environment = Environment()

        self.agent = ReactiveAgent()

        self.running = False

        self.paused = False

        self.after_id = None

        self.speed = 500

        self.environment.randomize_positions()

        self.agent.reset(
            self.environment.agent_position
        )

        self.create_interface()

        self.draw_grid()

        self.update_information()

    def create_interface(self):

        title = ttk.Label(
            self.root,
            text="REACTIVE LIGHT-SEEKING AGENT",
            font=("Arial", 18, "bold"),
        )

        title.pack(
            pady=10
        )

        self.canvas = tk.Canvas(
            self.root,
            width=WINDOW_WIDTH,
            height=GRID_HEIGHT * CELL_SIZE,
            bg="white",
        )

        self.canvas.pack(
            padx=10
        )

        info_frame = ttk.Frame(
            self.root
        )

        info_frame.pack(
            pady=10
        )

        self.position_label = ttk.Label(
            info_frame,
            text="",
            font=("Arial", 11),
        )

        self.position_label.grid(
            row=0,
            column=0,
            padx=10,
        )

        self.light_label = ttk.Label(
            info_frame,
            text="",
            font=("Arial", 11),
        )

        self.light_label.grid(
            row=0,
            column=1,
            padx=10,
        )

        self.direction_label = ttk.Label(
            info_frame,
            text="",
            font=("Arial", 11),
        )

        self.direction_label.grid(
            row=1,
            column=0,
            padx=10,
        )

        self.steps_label = ttk.Label(
            info_frame,
            text="",
            font=("Arial", 11),
        )

        self.steps_label.grid(
            row=1,
            column=1,
            padx=10,
        )

        self.status_label = ttk.Label(
            info_frame,
            text="",
            font=("Arial", 11, "bold"),
        )

        self.status_label.grid(
            row=2,
            column=0,
            columnspan=2,
            pady=5,
        )

        button_frame = ttk.Frame(
            self.root
        )

        button_frame.pack(
            pady=10
        )

        ttk.Button(
            button_frame,
            text="START",
            command=self.start,
        ).grid(
            row=0,
            column=0,
            padx=5,
        )

        ttk.Button(
            button_frame,
            text="PAUSE",
            command=self.pause,
        ).grid(
            row=0,
            column=1,
            padx=5,
        )

        ttk.Button(
            button_frame,
            text="STEP",
            command=self.single_step,
        ).grid(
            row=0,
            column=2,
            padx=5,
        )

        ttk.Button(
            button_frame,
            text="RESET",
            command=self.reset,
        ).grid(
            row=0,
            column=3,
            padx=5,
        )

        ttk.Button(
            button_frame,
            text="RANDOMIZE",
            command=self.randomize,
        ).grid(
            row=0,
            column=4,
            padx=5,
        )

        speed_frame = ttk.Frame(
            self.root
        )

        speed_frame.pack(
            pady=5
        )

        ttk.Label(
            speed_frame,
            text="Speed:",
        ).pack(
            side="left"
        )

        self.speed_combo = ttk.Combobox(
            speed_frame,
            values=[
                "Slow",
                "Medium",
                "Fast",
            ],
            state="readonly",
            width=10,
        )

        self.speed_combo.set(
            "Medium"
        )

        self.speed_combo.pack(
            side="left",
            padx=5,
        )

        self.speed_combo.bind(
            "<<ComboboxSelected>>",
            self.change_speed,
        )

    def draw_grid(self):

        self.canvas.delete(
            "all"
        )

        for x in range(GRID_WIDTH + 1):

            position = x * CELL_SIZE

            self.canvas.create_line(
                position,
                0,
                position,
                GRID_HEIGHT * CELL_SIZE,
            )

        for y in range(GRID_HEIGHT + 1):

            position = y * CELL_SIZE

            self.canvas.create_line(
                0,
                position,
                GRID_WIDTH * CELL_SIZE,
                position,
            )

        ax, ay = (
            self.environment.agent_position
        )

        lx, ly = (
            self.environment.light_position
        )

        self.canvas.create_oval(
            ax * CELL_SIZE + 10,
            ay * CELL_SIZE + 10,
            (ax + 1) * CELL_SIZE - 10,
            (ay + 1) * CELL_SIZE - 10,
            fill="blue",
        )

        self.canvas.create_text(
            ax * CELL_SIZE + CELL_SIZE / 2,
            ay * CELL_SIZE + CELL_SIZE / 2,
            text="A",
            fill="white",
            font=("Arial", 16, "bold"),
        )

        self.canvas.create_oval(
            lx * CELL_SIZE + 10,
            ly * CELL_SIZE + 10,
            (lx + 1) * CELL_SIZE - 10,
            (ly + 1) * CELL_SIZE - 10,
            fill="gold",
        )

        self.canvas.create_text(
            lx * CELL_SIZE + CELL_SIZE / 2,
            ly * CELL_SIZE + CELL_SIZE / 2,
            text="L",
            fill="black",
            font=("Arial", 16, "bold"),
        )

    def update_information(self):

        percept = self.agent.perceive(
            self.environment
        )

        if percept["status"] == "REACHED":

            direction = "REACHED"

        elif percept["horizontal"]:

            direction = percept["horizontal"]

        else:

            direction = percept["vertical"]

        self.position_label.config(
            text=(
                f"Agent: "
                f"{self.environment.agent_position}"
            )
        )

        self.light_label.config(
            text=(
                f"Light: "
                f"{self.environment.light_position}"
            )
        )

        self.direction_label.config(
            text=(
                f"Percept: {direction}"
            )
        )

        self.steps_label.config(
            text=(
                f"Steps: {self.agent.steps}"
            )
        )

        if self.environment.target_reached():

            status = "TARGET REACHED"

        elif self.running:

            status = "SEARCHING..."

        elif self.paused:

            status = "PAUSED"

        else:

            status = "READY"

        self.status_label.config(
            text=f"Status: {status}"
        )

    def execute_step(self):

        if self.environment.target_reached():

            self.running = False

            self.update_information()

            return

        percept = self.agent.perceive(
            self.environment
        )

        action = self.agent.decide(
            percept
        )

        self.agent.act(
            self.environment,
            action,
        )

        self.draw_grid()

        self.update_information()

    def start(self):

        if self.environment.target_reached():

            return

        self.running = True

        self.paused = False

        self.run_loop()

    def run_loop(self):

        if not self.running:

            return

        if self.paused:

            return

        if self.environment.target_reached():

            self.running = False

            self.update_information()

            return

        self.execute_step()

        self.after_id = self.root.after(
            self.speed,
            self.run_loop,
        )

    def pause(self):

        self.running = False

        self.paused = True

        self.update_information()

    def single_step(self):

        self.running = False

        self.paused = True

        self.execute_step()

    def reset(self):

        self.running = False

        self.paused = False

        self.environment.set_positions(
            agent_position=(1, 1),
            light_position=(8, 7),
        )

        self.agent.reset(
            self.environment.agent_position
        )

        self.draw_grid()

        self.update_information()

    def randomize(self):

        self.running = False

        self.paused = False

        self.environment.randomize_positions()

        self.agent.reset(
            self.environment.agent_position
        )

        self.draw_grid()

        self.update_information()

    def change_speed(self, event=None):

        value = self.speed_combo.get()

        if value == "Slow":

            self.speed = 1000

        elif value == "Medium":

            self.speed = 500

        elif value == "Fast":

            self.speed = 150

    def run(self):

        self.root.mainloop()


def run_gui():

    root = tk.Tk()

    app = ReactiveAgentGUI(
        root
    )

    app.run()


if __name__ == "__main__":

    run_gui()