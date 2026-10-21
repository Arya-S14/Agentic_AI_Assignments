"""
Reactive Light-Seeking Agent.
"""

import logging

from sensor import LightSensor


class ReactiveAgent:
    """
    A simple reactive agent.

    The agent:
        1. Perceives the environment.
        2. Applies condition-action rules.
        3. Performs the selected action.
    """

    def __init__(self):
        self.sensor = LightSensor()

        self.steps = 0

        self.history = []

        self.start_position = None

        self.total_invalid_actions = 0

    def reset(self, start_position=None):
        """
        Reset the internal agent state.
        """

        self.steps = 0
        self.history = []
        self.total_invalid_actions = 0
        self.start_position = start_position

    def perceive(self, environment):
        """
        Sense the environment.
        """

        percept = self.sensor.sense(
            environment.agent_position,
            environment.light_position,
        )

        logging.info(
            "PERCEPT: %s",
            percept,
        )

        return percept

    def decide(self, percept):
        """
        Apply reactive condition-action rules.

        Priority:
            1. Stop if target reached.
            2. Correct horizontal position.
            3. Correct vertical position.
            4. Stay if no movement is required.
        """

        if percept["status"] == "REACHED":
            return "STAY"

        if percept["horizontal"] is not None:
            return percept["horizontal"]

        if percept["vertical"] is not None:
            return percept["vertical"]

        return "STAY"

    def act(self, environment, action):
        """
        Execute an action in the environment.
        """

        old_position = environment.agent_position

        moved = environment.move_agent(action)

        if moved:
            self.steps += 1
        else:
            self.total_invalid_actions += 1

        new_position = environment.agent_position

        record = {
            "step": self.steps,
            "old_position": old_position,
            "action": action,
            "new_position": new_position,
            "moved": moved,
        }

        self.history.append(record)

        logging.info(
            "ACTION: %s | FROM: %s | TO: %s | MOVED: %s",
            action,
            old_position,
            new_position,
            moved,
        )

        return moved

    def calculate_optimal_steps(
        self,
        start_position,
        target_position,
    ):
        """
        Calculate the theoretical minimum number of steps
        in an unobstructed grid.
        """

        start_x, start_y = start_position
        target_x, target_y = target_position

        return (
            abs(target_x - start_x)
            + abs(target_y - start_y)
        )

    def calculate_efficiency(
        self,
        start_position,
        target_position,
    ):
        """
        Calculate movement efficiency.
        """

        optimal_steps = self.calculate_optimal_steps(
            start_position,
            target_position,
        )

        if self.steps == 0:
            return 100.0

        return (
            optimal_steps / self.steps
        ) * 100

    def get_metrics(self, environment):
        """
        Return simulation performance metrics.
        """

        if self.start_position is None:

            if self.history:
                self.start_position = (
                    self.history[0]["old_position"]
                )

            else:
                self.start_position = (
                    environment.agent_position
                )

        optimal_steps = self.calculate_optimal_steps(
            self.start_position,
            environment.light_position,
        )

        efficiency = self.calculate_efficiency(
            self.start_position,
            environment.light_position,
        )

        return {
            "success": environment.target_reached(),
            "steps": self.steps,
            "optimal_steps": optimal_steps,
            "efficiency_percent": round(
                efficiency,
                2,
            ),
            "invalid_actions": self.total_invalid_actions,
            "start_position": self.start_position,
            "final_position": environment.agent_position,
            "target_position": environment.light_position,
        }