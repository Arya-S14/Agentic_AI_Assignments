"""
Sensor system for the reactive light-seeking agent.
"""


class LightSensor:
    """
    Detects the relative position of the light source.
    """

    def sense(self, agent_position, light_position):
        """
        Return a percept describing where the light is.
        """

        agent_x, agent_y = agent_position
        light_x, light_y = light_position

        if agent_position == light_position:
            return {
                "horizontal": None,
                "vertical": None,
                "status": "REACHED",
            }

        horizontal = None
        vertical = None

        if light_x > agent_x:
            horizontal = "RIGHT"

        elif light_x < agent_x:
            horizontal = "LEFT"

        if light_y > agent_y:
            vertical = "DOWN"

        elif light_y < agent_y:
            vertical = "UP"

        return {
            "horizontal": horizontal,
            "vertical": vertical,
            "status": "SEARCHING",
        }