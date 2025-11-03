import random
from entities import Road, Lane, TrafficLightState, Vehicle
from parameters import ModelParameters
from typing import Tuple
import time

# ----------------------------------------------------
# Intersection Model Class
# ----------------------------------------------------


class IntersectionModel:
    """
    Main simulation managing roads, vehicles, traffic light, and accidents.
    It's an extension of the Nagel-Schreckenberg model.
    """

    def __init__(
        self,
        length: int,
        vmax: int,
        t_green: int,
        injection_rate: float,
        params: ModelParameters,
    ):
        """
        Initialize the intersection model.

        Args:
            length: Road length (cells)
            vmax: Maximum speed (cells/time step)
            t_green: Green light period (time steps)
            injection_rate: Probability of vehicle injection
            params: Model parameters (p_b, p_chg, p_red, p_skid)
        """
        # Simulation Parameters
        self.L = length
        self.V_MAX_BASE = vmax  # Base max velocity for new vehicles
        self.T_GREEN = t_green
        self.INJECTION_RATE = injection_rate

        # Model parameters
        self.params = params
        self.P_B = params.p_b
        self.P_CHG = params.p_chg
        self.P_RED = params.p_red
        self.P_SKID = params.p_skid
        self.lane_changing_enabled = params.allow_lane_changes

        # Intersection dimensions
        self.INTERSECTION_SIZE = (
            2  # Number of cells each lane occupies in the intersection
        )
        # Total road length including intersection space
        self.L_TOTAL = self.L + self.INTERSECTION_SIZE

        # Simulation objects collections
        # The 'grid' is a dictionary-based representation of the road.
        self.grid = {r: {l: [None] * self.L_TOTAL for l in Lane} for r in Road}
        self.vehicles = []  # List of all active Vehicle objects
        self.next_vehicle_id = 0
        self.time_step = 0

        # Traffic Light
        self.traffic_light = {
            Road.R1: TrafficLightState.GREEN,
            Road.R2: TrafficLightState.RED,
        }

        # Output Variables (Metrics to Measure)
        self.N_lateral = 0  # Total count of lateral collisions (red light violation)
        self.N_rear_end = 0  # Total count of rear-end collisions (braking failure)
        self.N_vehicles = 0  # Total number of vehicles that have circulated
        self.throughput = (
            0  # Number of vehicles that have passed through the intersection
        )

        # Define the intersection zone
        # Stop line is at the position before the intersection starts
        self.intersection_start = self.L // 2
        self.intersection_end = self.intersection_start + self.INTERSECTION_SIZE

    def update_traffic_light(self):
        """Updates the traffic light state every T_GREEN time steps."""
        # Full cycle T = 2 * T_GREEN
        if (self.time_step % self.T_GREEN) == 0:
            # Switch lights
            if self.traffic_light[Road.R1] == TrafficLightState.GREEN:
                self.traffic_light[Road.R1] = TrafficLightState.RED
                self.traffic_light[Road.R2] = TrafficLightState.GREEN
            else:
                self.traffic_light[Road.R1] = TrafficLightState.GREEN
                self.traffic_light[Road.R2] = TrafficLightState.RED

    def inject_vehicle(self):
        """Tries to inject a new vehicle into the system."""
        # Implementation of vehicle injection with INJECTION_RATE 'a'
        # Should choose a road (R1/R2) and a lane (LEFT/RIGHT) if the starting cell (position 0) is free.

        # Try to inject with probability INJECTION_RATE
        if random.random() > self.INJECTION_RATE:
            return  # No injection this time step

        # Randomly choose a road and lane
        road = random.choice(list(Road))
        lane = random.choice(list(Lane))

        # Check if the starting position (cell 0) is free
        if self.grid[road][lane][0] is not None:
            return  # Starting position is occupied, cannot inject

        # Create a new vehicle
        new_vehicle = Vehicle(
            vehicle_id=self.next_vehicle_id,
            road=road,
            lane=lane,
            vmax=self.V_MAX_BASE,
            p_red=self.P_RED,
            p_skid=self.P_SKID,
        )

        # Increment vehicle ID counter
        self.next_vehicle_id += 1
        self.N_vehicles += 1

        # Add vehicle to the grid and vehicle list
        self.grid[road][lane][0] = new_vehicle
        self.vehicles.append(new_vehicle)

    def find_front_vehicle(self, vehicle: Vehicle) -> Vehicle | None:
        """Finds the vehicle object directly ahead in the same lane."""
        road = self.grid[vehicle.road][vehicle.lane]
        # Search from the cell in front of the vehicle to the end
        for i in range(vehicle.position + 1, self.L_TOTAL):
            if road[i] is not None:
                return road[i]
        return None  # No vehicle found

    def find_front_gap(
        self, vehicle: Vehicle, road: Road = None, lane: Lane = None
    ) -> Tuple[int, str]:
        """
        Calculates the distance (gap) to the vehicle ahead.
        This is the number of empty cells *between* this car and the next one.
        If no vehicle is ahead, returns a large value (effectively infinite gap).
        Also considers the intersection stop line as a barrier if the light is red.

        The second output indicates why the gap is limited

        Args:
            vehicle: The vehicle for which to calculate the gap
            road: Optional road to check (defaults to vehicle's current road)
            lane: Optional lane to check (defaults to vehicle's current lane)
        """
        target_road = road if road is not None else vehicle.road
        target_lane = lane if lane is not None else vehicle.lane
        road_grid = self.grid[target_road][target_lane]

        # Check if there's a red light ahead and vehicle hasn't passed the intersection yet
        if (
            self.traffic_light[target_road] == TrafficLightState.RED
            and vehicle.position < self.intersection_start
        ):
            # Gap to the stop line (position before intersection)
            gap_to_intersection = self.intersection_start - vehicle.position - 1

            # Check for vehicles between current position and intersection
            for i in range(vehicle.position + 1, self.intersection_start):
                if road_grid[i] is not None:
                    # Found a vehicle before the intersection
                    return i - vehicle.position - 1, "vehicle"

            if gap_to_intersection == 0:
                return 0, "red_light"

            if random.random() < vehicle.p_red:
                # Vehicle decides to violate the red light
                return self.L_TOTAL * 2, "empty"
            else:
                return gap_to_intersection, "red_light"

        # Normal case: look for vehicles ahead (either green light or already past intersection)
        # Iterate from the cell in front of the vehicle to the end
        for i in range(vehicle.position + 1, self.L_TOTAL):
            if road_grid[i] is not None:
                # Found a vehicle, gap is distance to it
                return i - vehicle.position - 1, "vehicle"

        return self.L_TOTAL * 2, "empty"

    def find_back_gap(self, vehicle: Vehicle, lane: Lane = None) -> int:
        """
        Calculates the distance (gap) to the vehicle behind in the specified lane.
        This is the number of empty cells *between* this car and the one behind.
        If no vehicle is behind, returns a large value.

        Args:
            vehicle: The vehicle for which to calculate the gap
            lane: Optional lane to check (defaults to vehicle's current lane)
        """
        target_lane = lane if lane is not None else vehicle.lane
        road = self.grid[vehicle.road][target_lane]

        # Iterate from the cell behind the vehicle to the start
        for i in range(vehicle.position - 1, -1, -1):
            if road[i] is not None:
                # Found a vehicle, gap is distance to it
                return vehicle.position - i - 1

        return self.L_TOTAL * 2  # No vehicle found

    def get_other_lane(self, lane: Lane) -> Lane:
        """Returns the opposite lane."""
        return Lane.RIGHT if lane == Lane.LEFT else Lane.LEFT

    def can_change_lane(self, vehicle: Vehicle) -> bool:
        """
        Checks if a lane change is safe and advantageous for the vehicle.

        Safety conditions:
        1. No vehicle in the target cell (same position in other lane)
        2. No vehicle behind in other lane can crash into us

        Advantageous condition:
        1. The front gap in the other lane is larger than in current lane

        Returns:
            True if lane change is safe and advantageous, False otherwise
        """
        other_lane = self.get_other_lane(vehicle.lane)
        other_lane_grid = self.grid[vehicle.road][other_lane]

        # Safety check 1: Cell at same position must be empty
        if other_lane_grid[vehicle.position] is not None:
            return False

        # Safety check 2: Check vehicles behind in the other lane
        back_gap_other = self.find_back_gap(vehicle, lane=other_lane)

        # Find the vehicle behind in the other lane
        for i in range(vehicle.position - 1, -1, -1):
            if other_lane_grid[i] is not None:
                vehicle_behind = other_lane_grid[i]
                # Check if that vehicle could crash into us
                # The vehicle behind is safe if its velocity is less than or equal to the gap
                if vehicle_behind.velocity > back_gap_other:
                    return False
                break

        # Advantageous check: Compare front gaps
        current_gap, current_reason = self.find_front_gap(vehicle)
        other_gap, other_reason = self.find_front_gap(vehicle, lane=other_lane)

        # Only change if other lane has a better gap
        return other_gap > current_gap

    def attempt_lane_change(
        self,
        vehicle: Vehicle,
    ):
        """
        Attempts to change lane for a vehicle if conditions are met.
        This should be called before velocity calculations.

        Args:
            vehicle: The vehicle attempting to change lanes
        """
        # Only attempt lane change if enabled
        if not self.lane_changing_enabled:
            return

        # Don't change lanes if already collided
        if vehicle.collided:
            return

        # Check current front gap and reason
        _, reason = self.find_front_gap(vehicle)

        # Only consider lane change if blocked by a vehicle
        if reason != "vehicle":
            return

        # Check if lane change is safe and advantageous
        if self.can_change_lane(vehicle):
            # Perform the lane change
            other_lane = self.get_other_lane(vehicle.lane)

            # Remove from current lane
            self.grid[vehicle.road][vehicle.lane][vehicle.position] = None

            # Update vehicle's lane
            vehicle.lane = other_lane

            # Place in new lane
            self.grid[vehicle.road][other_lane][vehicle.position] = vehicle

    def apply_nasch_rules(self):
        """
        Applies the NaSch update rules and collision logic in four phases:
        0. Lane Changing: Evaluate and perform lane changes if advantageous (if enabled).
        1. Calculation: Determine intended moves.
        2. Collision Check: Detect and resolve lateral and rear-end collisions.
        3. Update: Apply final moves to the grid.
        """

        if self.lane_changing_enabled:
            for vehicle in self.vehicles:
                self.attempt_lane_change(vehicle)

        # Stores the intended state {'pos': int, 'vel': int} for each vehicle
        new_vehicles_state = {}
        # Stores vehicles intending to enter the intersection {Road.R1: [v1, v2], R2: [v3]}
        intersection_entrants = {Road.R1: [], Road.R2: []}

        # --- PHASE 1: Calculate intended moves for all vehicles ---
        for vehicle in self.vehicles:
            v_i = vehicle.velocity
            d_i, reason = self.find_front_gap(vehicle)

            # --- Rule 1 (acceleration) ---
            v_new = min(v_i + 1, vehicle.v_max)

            # --- Rule 2 (safety distance) ---
            if v_new > d_i:
                ## -- CASE A: there is a vehicle in front, check for braking failure -- ##
                # Only check for rear-end collision if the gap is limited by a vehicle, not by a red light
                if reason == "vehicle":
                    front_vehicle = self.find_front_vehicle(vehicle)
                    if (
                        front_vehicle
                        and v_new <= front_vehicle.velocity + d_i
                        and random.random() < vehicle.p_skid
                    ):
                        front_vehicle.collided = True

                        self.N_rear_end += 1
                        vehicle.collided = True

                        # The vehicle fails to slow down and hits the car in front.
                        # Its new position will be the cell *behind* the front car.
                        new_pos = vehicle.position + d_i
                        v_new = 0
                    else:
                        v_new = d_i
                ## -- CASE B: Gap is limited by red light or end of road, just slow down
                else:
                    v_new = d_i

            # --- Rule 3 (random braking) ---
            if v_new > 0 and random.random() < self.P_B:
                v_new -= 1

            new_pos = vehicle.position + v_new
            new_vehicles_state[vehicle] = {"pos": new_pos, "vel": v_new}

            # --- Check if this move enters the intersection ---
            if (
                vehicle.position < self.intersection_start <= new_pos
                and not vehicle.collided
            ):
                intersection_entrants[vehicle.road].append(vehicle)
                self.throughput += 1

        # --- PHASE 2: Check for Lateral Collisions ---
        if intersection_entrants[Road.R1] and intersection_entrants[Road.R2]:
            self.N_lateral += 1

            # Mark ALL vehicles entering the intersection as collided
            # Only vehicles that actually entered (violators) should collide
            # Vehicles stopped before the intersection are safe
            for road_entrants in intersection_entrants.values():
                for vehicle in road_entrants:
                    if not vehicle.collided:
                        vehicle.collided = True
                        # The vehicle stops *at* the collision point (inside the intersection)
                        # Place them at the start of the intersection zone
                        new_vehicles_state[vehicle]["pos"] = self.intersection_start
                        new_vehicles_state[vehicle]["vel"] = 0

        # --- PHASE 3: Apply Final State and Update Grid ---
        self.grid = {r: {l: [None] * self.L_TOTAL for l in Lane} for r in Road}

        vehicles_to_remove = []

        for vehicle in self.vehicles:
            # Get the final state (which may have been modified by collision)
            final_pos = new_vehicles_state[vehicle]["pos"]
            final_vel = new_vehicles_state[vehicle]["vel"]

            if vehicle.collided:
                vehicle.velocity = 0
                # If the collided vehicle is still on the board, place it
                if final_pos < self.L_TOTAL:
                    vehicle.position = final_pos
                    # Place it in the grid so it blocks traffic
                    self.grid[vehicle.road][vehicle.lane][final_pos] = vehicle
                else:
                    # Collided vehicle at or beyond road end - remove it
                    vehicles_to_remove.append(vehicle)

            elif final_pos >= self.L_TOTAL:
                # Vehicle successfully completed the road and leaves the system
                vehicles_to_remove.append(vehicle)

            else:
                # Vehicle moves to new cell (normal movement)
                vehicle.position = final_pos
                vehicle.velocity = final_vel
                self.grid[vehicle.road][vehicle.lane][final_pos] = vehicle

        # Remove vehicles that have left the road
        for vehicle in vehicles_to_remove:
            self.vehicles.remove(vehicle)

            # remove vehicles from intersection entrants if they were marked
            for road in intersection_entrants:
                if vehicle in intersection_entrants[road]:
                    intersection_entrants[road].remove(vehicle)

        self.time_step += 1

    def run_simulation(self, steps: int):
        """Runs the simulation for a number of steps."""
        self.steps = steps

        t1 = time.time()
        for _ in range(steps):
            self.update_traffic_light()
            self.inject_vehicle()
            self.apply_nasch_rules()

        t2 = time.time()
        self.simulation_time = t2 - t1

    def get_metrics(self):
        """Returns the output metrics of the simulation."""
        return {
            "n_lateral": self.N_lateral,
            "n_rear_end": self.N_rear_end,
            "n_vehicles": self.N_vehicles,
            "throughput": self.throughput,
            "lateral_to_rear_end_ratio": (
                self.N_lateral / self.N_rear_end if self.N_rear_end > 0 else 0
            ),
            "time": self.simulation_time,
        }

    def get_params(self):
        """Returns the model parameters."""
        return {
            "length": self.L,
            "vmax": self.V_MAX_BASE,
            "t_green": self.T_GREEN,
            "injection_rate": self.INJECTION_RATE,
            "p_b": self.P_B,
            "p_chg": self.P_CHG,
            "p_red": self.P_RED,
            "p_skid": self.P_SKID,
            "steps": self.steps,
        }

    def print_road_state(self):
        """Prints the current state of the roads for debugging with intersection highlighted."""
        print(f"\n{'='*80}")
        print(f"Time Step: {self.time_step}")
        print(
            f"Traffic Lights - R1: {self.traffic_light[Road.R1].name}, R2: {self.traffic_light[Road.R2].name}"
        )
        print(f"{'='*80}")

        for road in Road:
            print(f"\n--- Road {road.name} ---")
            for lane in Lane:
                lane_state = ""
                for i, cell in enumerate(self.grid[road][lane]):
                    # Mark intersection zone
                    if i == self.intersection_start:
                        lane_state += "| "  # Start of intersection

                    if cell is None:
                        lane_state += ". "
                    else:
                        lane_state += (
                            f"{cell.velocity} "
                            if not cell.collided
                            else f"X-{cell.velocity} "
                        )

                    if i == self.intersection_end - 1:
                        lane_state += "| "  # End of intersection

                # Add position markers
                position_markers = ""
                for i in range(self.L_TOTAL):
                    if i == self.intersection_start:
                        position_markers += "| "
                    position_markers += f"{i%10} "
                    if i == self.intersection_end - 1:
                        position_markers += "| "

                print(f"Lane {lane.name:5}: {lane_state}")
                if lane == Lane.RIGHT:  # Print markers only once per road
                    print(f"{'':11} {position_markers}")

        print(f"\n{'='*80}\n")

    def print_intersection(self):
        """Prints the state of the intersection area for debugging."""
        print(f"--- Intersection State at time {self.time_step} ---")
        print(
            f"Intersection zone: cells [{self.intersection_start}, {self.intersection_end})"
        )
        for road in Road:
            print(f"\nRoad {road.name} (Light: {self.traffic_light[road].name}):")
            for lane in Lane:
                print(f"  Lane {lane.name}:")
                for i in range(self.intersection_start, self.intersection_end):
                    cell = self.grid[road][lane][i]
                    if cell is None:
                        status = "Empty"
                    else:
                        status = f"Vehicle {cell.id} (v={cell.velocity}) {'[COLLIDED]' if cell.collided else ''}"
                    print(f"    Cell {i}: {status}")
        print("-----------------------------------------")
