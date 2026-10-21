# Reactive Light-Seeking Agent

## 1. Problem Statement

The objective of this project is to design and implement a reactive intelligent agent that operates in a two-dimensional grid environment and moves toward a light source using current sensory information.

The agent continuously perceives the location of the light, selects an appropriate movement action using condition-action rules, and executes the action in the environment.

---

## 2. Objective

The primary objectives are:

- Implement a reactive intelligent agent.
- Create a discrete 2D grid environment.
- Implement a light-direction sensor.
- Implement condition-action decision rules.
- Move the agent toward the light.
- Prevent movement outside the environment.
- Track agent performance.
- Provide a graphical simulation interface.
- Test the implementation using automated tests.

---

## 3. AI Concept

This project demonstrates a reactive agent.

A reactive agent selects actions primarily according to its current percept rather than constructing an explicit plan of future states.

The fundamental loop is:

Perceive → Decide → Act → Perceive

---

## 4. PEAS Description

### Performance Measure

The agent is evaluated using:

- Target-reaching success.
- Number of steps.
- Theoretical optimal number of steps.
- Movement efficiency.
- Invalid movement attempts.

### Environment

A finite 2D grid containing:

- Agent.
- Light source.
- Empty cells.

### Actuators

The agent can perform:

- UP
- DOWN
- LEFT
- RIGHT
- STAY

### Sensors

The light sensor detects the relative direction of the light source.

---

## 5. Architecture

The system follows:

Environment
↓
Sensor
↓
Percept
↓
Reactive Agent
↓
Action
↓
Environment

---

## 6. Reactive Rules

The agent follows these rules:

IF the light is to the right:
    move right

IF the light is to the left:
    move left

IF the light is below:
    move down

IF the light is above:
    move up

IF the agent has reached the light:
    stay

---

## 7. Performance

For an unobstructed grid, the theoretical minimum number of movements is calculated using Manhattan distance:

D = |x2 - x1| + |y2 - y1|

Efficiency is calculated as:

Efficiency = Optimal Steps / Actual Steps × 100

---

## 8. Features

- 2D grid simulation.
- Reactive decision making.
- Random environment generation.
- Reset functionality.
- Start/Pause controls.
- Single-step execution.
- Adjustable simulation speed.
- Performance metrics.
- Movement history.
- Logging.
- Automated testing.
- Graphical interface.
- Terminal simulation.
- Multi-run evaluation.

---

## 9. Running the Project

Install dependencies:

pip install -r requirements.txt

Run the application:

python main.py

The application provides three modes:

1. Terminal simulation.
2. Graphical simulation.
3. Automated evaluation.

---

## 10. Testing

Run:

pytest

The test suite validates:

- Grid boundaries.
- Sensor behaviour.
- Target detection.
- Agent decision rules.
- Agent movement.
- Target reaching.

---

## 11. Limitations

The basic agent:

- Does not learn from experience.
- Does not use search.
- Does not construct an explicit plan.
- Assumes reliable sensor information.
- Does not consider obstacles.

---

## 12. Future Enhancements

Potential extensions include:

- Obstacles.
- Multiple light sources.
- Moving targets.
- Noisy sensors.
- Variable light intensity.
- Reinforcement learning.
- Natural-language control.
- LLM-based command interpretation.
- Multi-agent environments.

---

## 13. Conclusion

The project demonstrates the fundamental architecture of a reactive intelligent agent. The agent perceives the current environment, applies predefined condition-action rules, and performs an action that moves it toward the target.

The project establishes the foundation for more advanced intelligent-agent architectures such as goal-based, utility-based, learning, memory-based, tool-using, and multi-agent systems.