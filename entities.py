from enum import Enum


class Road(Enum):
    """Represents the two perpendicular roads of the intersection."""

    R1 = 1  # Vertical Axis (North-South)
    R2 = 2  # Horizontal Axis (West-East)


class Lane(Enum):
    """Represents the two lanes of a road."""

    LEFT = 0
    RIGHT = 1


class TrafficLightState(Enum):
    """Traffic light state for a road (R1 or R2)."""

    RED = 0
    GREEN = 1


class Weather(Enum):
    """Weather condition for the simulation."""

    NORMAL = 0
    RAINY = 1  # "Rainy day" state (global modifier)


# ----------------------------------------------------
# Vehicle Class
# ----------------------------------------------------


class Vehicle:
    """Represents a single vehicle in the model."""

    def __init__(self, vehicle_id, road: Road, lane: Lane, vmax, p_red, p_skid):
        self.id = vehicle_id
        self.road = road  # R1 or R2
        self.lane = lane  # LEFT or RIGHT
        self.position = 0
        self.velocity = 0
        self.v_max = vmax

        # Individual parameters (can be modified by weather)
        self.p_red = p_red
        self.p_skid = p_skid

        # Collision status
        self.collided = False
