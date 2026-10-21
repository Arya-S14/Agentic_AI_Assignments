"""
Automated tests for the Reactive Light-Seeking Agent.
"""

from agent import ReactiveAgent
from environment import Environment
from sensor import LightSensor


def test_valid_position():

    environment = Environment()

    assert environment.is_valid_position(
        (0, 0)
    )

    assert environment.is_valid_position(
        (9, 9)
    )


def test_invalid_position():

    environment = Environment()

    assert not environment.is_valid_position(
        (-1, 0)
    )

    assert not environment.is_valid_position(
        (10, 10)
    )


def test_target_detection():

    environment = Environment()

    environment.set_positions(
        (5, 5),
        (5, 5),
    )

    assert environment.target_reached()


def test_sensor_right():

    sensor = LightSensor()

    percept = sensor.sense(
        (2, 2),
        (5, 2),
    )

    assert percept["horizontal"] == "RIGHT"


def test_sensor_left():

    sensor = LightSensor()

    percept = sensor.sense(
        (5, 2),
        (2, 2),
    )

    assert percept["horizontal"] == "LEFT"


def test_sensor_up():

    sensor = LightSensor()

    percept = sensor.sense(
        (2, 5),
        (2, 2),
    )

    assert percept["vertical"] == "UP"


def test_sensor_down():

    sensor = LightSensor()

    percept = sensor.sense(
        (2, 2),
        (2, 5),
    )

    assert percept["vertical"] == "DOWN"


def test_sensor_reached():

    sensor = LightSensor()

    percept = sensor.sense(
        (5, 5),
        (5, 5),
    )

    assert percept["status"] == "REACHED"


def test_agent_decision():

    agent = ReactiveAgent()

    assert agent.decide({
        "horizontal": "RIGHT",
        "vertical": "DOWN",
        "status": "SEARCHING",
    }) == "RIGHT"

    assert agent.decide({
        "horizontal": "LEFT",
        "vertical": "UP",
        "status": "SEARCHING",
    }) == "LEFT"

    assert agent.decide({
        "horizontal": None,
        "vertical": "UP",
        "status": "SEARCHING",
    }) == "UP"


def test_agent_stops_at_target():

    agent = ReactiveAgent()

    action = agent.decide({
        "horizontal": None,
        "vertical": None,
        "status": "REACHED",
    })

    assert action == "STAY"


def test_agent_reaches_target():

    environment = Environment()

    environment.set_positions(
        (0, 0),
        (3, 3),
    )

    agent = ReactiveAgent()

    agent.reset(
        environment.agent_position
    )

    max_iterations = 20

    for _ in range(max_iterations):

        if environment.target_reached():
            break

        percept = agent.perceive(
            environment
        )

        action = agent.decide(
            percept
        )

        agent.act(
            environment,
            action,
        )

    assert environment.target_reached()

    assert agent.steps == 6