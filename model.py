import random
from entities import Road, Lane, TrafficLightState, Weather, Vehicle
from parameters import ModelParameters
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

        # Simulation objects collections
        # The 'grid' is a dictionary-based representation of the road.
        # {Road.R1: {Lane.LEFT: [None] * L, Lane.RIGHT: [None] * L}, ...}
        self.grid = {r: {l: [None] * self.L for l in Lane} for r in Road}
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

        # Define the intersection cell (the cell right at the crossing)
        self.intersection_cell = self.L // 2

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
        for i in range(vehicle.position + 1, self.L):
            if road[i] is not None:
                return road[i]
        return None  # No vehicle found

    def find_front_gap(self, vehicle: Vehicle) -> int:
        """
        Calculates the distance (gap) to the vehicle ahead.
        This is the number of empty cells *between* this car and the next one.
        If no vehicle is ahead, returns a large value (effectively infinite gap).
        """
        road = self.grid[vehicle.road][vehicle.lane]
        # Iterate from the cell in front of the vehicle to the end
        for i in range(vehicle.position + 1, self.L):
            if road[i] is not None:
                # Found a vehicle, gap is distance to it
                return i - vehicle.position - 1
        # No vehicle found, gap is effectively infinite (return large value)
        # This allows vehicles to accelerate and leave the road
        return self.L * 2  # Large enough gap to not limit velocity

    def apply_nash_rules(self):
        """
        Applies the NaSch update rules and collision logic in three phases:
        1. Calculation: Determine intended moves.
        2. Collision Check: Detect and resolve lateral and rear-end collisions.
        3. Update: Apply final moves to the grid.
        """

        # Stores the intended state {'pos': int, 'vel': int} for each vehicle
        new_vehicles_state = {}
        # Stores vehicles intending to enter the intersection {Road.R1: [v1, v2], R2: [v3]}
        intersection_entrants = {Road.R1: [], Road.R2: []}

        # --- PHASE 1: Calculate intended moves for all vehicles ---

        for vehicle in self.vehicles:
            if vehicle.collided:
                # If already collided, it doesn't move
                new_vehicles_state[vehicle] = {"pos": vehicle.position, "vel": 0}
                continue

            v_i = vehicle.velocity
            # d_i is the gap to the *next vehicle*
            d_i = self.find_front_gap(vehicle)

            # --- NaSch Rules 1 (Acceleration) ---
            v_new = min(v_i + 1, vehicle.v_max)

            # --- NaSch Rules 2 (Deceleration - Car Ahead) ---
            # Slow down to avoid hitting the car in front
            v_new = min(v_new, d_i)

            # --- Intersection Logic (Part of Deceleration) ---
            # g_i is the gap to the *intersection stop line*
            gap_to_intersection = self.intersection_cell - vehicle.position - 1

            # Check if vehicle is approaching a RED light
            if self.traffic_light[vehicle.road] == TrafficLightState.RED:
                # If the car is close enough to cross on its next move...
                # (v_new > gap_to_intersection) means its intended speed will cross the line
                if v_new > gap_to_intersection:
                    # **NEW LOGIC: Decide whether to violate the red light**
                    if random.random() < vehicle.p_red:
                        # **INTENT TO VIOLATE RED LIGHT**
                        # The vehicle *ignores* the red light.
                        # v_new remains as calculated (limited only by car ahead)
                        pass
                    else:
                        # **INTENT TO STOP**
                        # Decelerate to stop *before* the intersection
                        v_new = max(0, gap_to_intersection)  # Stop at the line

            # --- NaSch Rules 3 (Randomization) ---
            if v_new > 0 and random.random() < self.P_B:  # P_B is modified by rain
                v_new -= 1

            # --- Braking Failure Check (Rear-End Collision) ---
            # If the car's *final* velocity (after rules) is *still* greater than
            # the gap to the car in front, a skid (braking failure) might occur.
            if v_new > d_i and random.random() < vehicle.p_skid:
                # Collision occurs!
                self.N_rear_end += 1
                vehicle.collided = True
                front_vehicle = self.find_front_vehicle(vehicle)
                if front_vehicle:
                    front_vehicle.collided = True  # The car in front is also hit

                # Stop at the collision point (cell behind the front car)
                v_new = 0
                new_pos = vehicle.position + d_i
            else:
                # --- Car Motion (Intended) ---
                # This is the normal, collision-free movement
                v_new = min(v_new, d_i)  # Final safety check
                new_pos = vehicle.position + v_new

            # Store the intended move
            new_vehicles_state[vehicle] = {"pos": new_pos, "vel": v_new}

            # --- Check if this move enters the intersection ---
            # A vehicle enters if its old pos was *before* and new pos is *at or after*
            if (
                vehicle.position < self.intersection_cell <= new_pos
                and not vehicle.collided
            ):
                intersection_entrants[vehicle.road].append(vehicle)
                # Increment throughput for vehicles passing through the intersection
                self.throughput += 1

        # --- PHASE 2: Check for Lateral Collisions ---

        # **NEW LOGIC: If *both* roads have vehicles entering the intersection...**
        if intersection_entrants[Road.R1] and intersection_entrants[Road.R2]:
            # print the state of the roads if there is a lateral collision
            self.print_road_state()
            self.N_lateral += 1

            # Mark ALL vehicles entering the intersection as collided
            # This is a simplification; a more complex model would check lane-by-lane
            for road_entrants in intersection_entrants.values():
                for vehicle in road_entrants:
                    if not vehicle.collided:  # Don't re-collide a rear-ended car
                        vehicle.collided = True
                        # The vehicle stops *at* the collision point (the intersection cell)
                        new_vehicles_state[vehicle]["pos"] = self.intersection_cell
                        new_vehicles_state[vehicle]["vel"] = 0

        # --- PHASE 3: Apply Final State and Update Grid ---

        # Clear the grid for the new time step
        self.grid = {r: {l: [None] * self.L for l in Lane} for r in Road}

        vehicles_to_remove = []

        for vehicle in self.vehicles:
            # Get the final state (which may have been modified by collision)
            final_pos = new_vehicles_state[vehicle]["pos"]
            final_vel = new_vehicles_state[vehicle]["vel"]

            if vehicle.collided:
                vehicle.velocity = 0  # Ensure velocity is 0
                # If the collided vehicle is still on the board, place it
                if final_pos < self.L:
                    vehicle.position = final_pos
                    # Place it in the grid so it blocks traffic
                    self.grid[vehicle.road][vehicle.lane][final_pos] = vehicle
                else:
                    # Collided vehicle at or beyond road end - remove it
                    vehicles_to_remove.append(vehicle)

            elif final_pos >= self.L:
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

        self.time_step += 1

    def run_simulation(self, steps: int):
        """Runs the simulation for a number of steps."""
        print(f"--- Running simulation for {steps} steps ---")
        for _ in range(steps):
            self.update_traffic_light()
            self.inject_vehicle()
            self.apply_nash_rules()

            # # print all vehicles' positions and velocities
            # for vehicle in self.vehicles:
            #     print(
            #         f"Time {self.time_step}: Vehicle {vehicle.id} on {vehicle.road.name}-{vehicle.lane.name} at pos {vehicle.position} with vel {vehicle.velocity} {'[COLLIDED]' if vehicle.collided else ''}"
            #     )

            # time.sleep(5)
            # In a real run, you'd collect data here
        print("--- Simulation complete ---")

    def get_metrics(self):
        """Returns the output metrics of the simulation."""
        return {
            "N_lateral": self.N_lateral,
            "N_rear_end": self.N_rear_end,
            "N_vehicles": self.N_vehicles,
            "Throughput": self.throughput,
            "Accident_Ratio_Lateral_to_RearEnd": self.N_lateral
            / (self.N_rear_end + 1e-6),  # Avoid div by zero
        }

    def print_road_state(self):
        """Prints the current state of the roads for debugging."""
        for road in Road:
            print(f"--- Road {road.name} ---")
            for lane in Lane:
                lane_state = ""
                for cell in self.grid[road][lane]:
                    if cell is None:
                        lane_state += ". "
                    else:
                        lane_state += f"{cell.velocity} " if not cell.collided else "X "
                print(f"Lane {lane.name}: {lane_state}")
        print("-----------------------")

    def print_intersection(self):
        """Prints the state of the intersection area for debugging."""
        print(f"--- Intersection State at time {self.time_step} ---")
        for road in Road:
            for lane in Lane:
                cell = self.grid[road][lane][self.intersection_cell]
                if cell is None:
                    status = "Empty"
                else:
                    status = (
                        f"Vehicle {cell.id} {'[COLLIDED]' if cell.collided else ''}"
                    )
                print(f"Road {road.name} Lane {lane.name}: {status}")
        print("-----------------------------------------")
