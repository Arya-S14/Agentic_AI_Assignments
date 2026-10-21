"""
Main entry point for the Reactive Light-Seeking Agent.
"""

import logging
import os
import time

from agent import ReactiveAgent
from environment import Environment
from config import MAX_STEPS, LOG_FILE


def setup_logging():
    """
    Configure application logging.
    """

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


def run_simulation(
    randomize=True,
    display=True,
    delay=0.1,
):
    """
    Run a complete agent simulation.
    """

    environment = Environment()

    if randomize:

        environment.randomize_positions()

    else:

        environment.set_positions(
            agent_position=(1, 1),
            light_position=(8, 7),
        )

    agent = ReactiveAgent()

    agent.reset(
        start_position=environment.agent_position
    )

    print("=" * 60)
    print("REACTIVE LIGHT-SEEKING AGENT")
    print("=" * 60)

    print(
        f"Agent starting position: "
        f"{environment.agent_position}"
    )

    print(
        f"Light position: "
        f"{environment.light_position}"
    )

    if display:
        environment.display()

    while not environment.target_reached():

        if agent.steps >= MAX_STEPS:

            print(
                "Maximum step limit reached."
            )

            break

        percept = agent.perceive(environment)

        action = agent.decide(percept)

        agent.act(
            environment,
            action,
        )

        print(
            f"Step {agent.steps:3d} | "
            f"Percept: {percept} | "
            f"Action: {action} | "
            f"Position: "
            f"{environment.agent_position}"
        )

        if display:
            environment.display()

        if delay > 0:
            time.sleep(delay)

    metrics = agent.get_metrics(
        environment
    )

    print("=" * 60)
    print("SIMULATION RESULT")
    print("=" * 60)

    for key, value in metrics.items():
        print(
            f"{key}: {value}"
        )

    return metrics


def main():
    """
    Application entry point.
    """

    setup_logging()

    print()
    print("Choose execution mode:")
    print("1. Terminal simulation")
    print("2. Graphical simulation")
    print("3. Automated evaluation")

    choice = input(
        "\nEnter choice (1/2/3): "
    ).strip()

    if choice == "1":

        run_simulation(
            randomize=True,
            display=True,
            delay=0.1,
        )

    elif choice == "2":

        from ui.app import run_gui

        run_gui()

    elif choice == "3":

        run_evaluation()

    else:

        print(
            "Invalid choice."
        )


def run_evaluation(number_of_runs=100):
    """
    Run multiple randomized simulations
    and calculate aggregate performance.
    """

    successful_runs = 0
    total_steps = 0
    total_efficiency = 0

    print()
    print("=" * 60)
    print(
        f"EVALUATING {number_of_runs} SIMULATIONS"
    )
    print("=" * 60)

    for _ in range(number_of_runs):

        metrics = run_simulation(
            randomize=True,
            display=False,
            delay=0,
        )

        if metrics["success"]:
            successful_runs += 1

        total_steps += metrics["steps"]

        total_efficiency += (
            metrics["efficiency_percent"]
        )

    success_rate = (
        successful_runs
        / number_of_runs
    ) * 100

    average_steps = (
        total_steps
        / number_of_runs
    )

    average_efficiency = (
        total_efficiency
        / number_of_runs
    )

    print()
    print("=" * 60)
    print("FINAL EVALUATION")
    print("=" * 60)

    print(
        f"Runs: {number_of_runs}"
    )

    print(
        f"Successful runs: "
        f"{successful_runs}"
    )

    print(
        f"Success rate: "
        f"{success_rate:.2f}%"
    )

    print(
        f"Average steps: "
        f"{average_steps:.2f}"
    )

    print(
        f"Average efficiency: "
        f"{average_efficiency:.2f}%"
    )


if __name__ == "__main__":
    main()