"""
Configuration settings for the Reactive Light-Seeking Agent.
"""

GRID_WIDTH = 10
GRID_HEIGHT = 10

CELL_SIZE = 60

WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE + 150

FPS = 60

SIMULATION_SPEED = 5

MAX_STEPS = 500

AGENT_SYMBOL = "A"
LIGHT_SYMBOL = "L"

EMPTY_SYMBOL = "."

WINDOW_TITLE = "Reactive Light-Seeking Agent"

LOG_FILE = "logs/agent.log"