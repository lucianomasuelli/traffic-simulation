import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
from typing import List, Tuple
from model import IntersectionModel
from entities import Road, Lane, TrafficLightState


class TrafficSimulationVisualizer:
    """
    Visualizes the traffic simulation as a 2D grid with perpendicular roads.

    Road R1 (vertical): North-South direction
    Road R2 (horizontal): West-East direction
    Cars are shown as black cells in their respective lanes.
    """

    def __init__(self, model: IntersectionModel, interval: int = 100):
        """
        Initialize the visualizer.

        Args:
            model: IntersectionModel instance to visualize
            interval: Animation interval in milliseconds (time between frames)
        """
        self.model = model
        self.interval = interval

        # Create figure and axis
        self.fig, self.ax = plt.subplots(figsize=(12, 12))

        # Grid dimensions
        self.L_TOTAL = model.L_TOTAL
        self.intersection_start = model.intersection_start
        self.intersection_end = model.intersection_end

        # Set up the plot
        self._setup_plot()

    def _setup_plot(self):
        """Set up the plot with grid and labels."""
        self.ax.set_xlim(-5, self.L_TOTAL + 5)
        self.ax.set_ylim(-5, self.L_TOTAL + 5)
        self.ax.set_aspect("equal")
        self.ax.grid(True, alpha=0.3, linewidth=0.5)
        self.ax.set_xlabel("Position (cells)", fontsize=12)
        self.ax.set_ylabel("Position (cells)", fontsize=12)
        self.ax.set_title(
            "Traffic Intersection Simulation", fontsize=14, fontweight="bold"
        )

    def _get_road_coordinates(
        self, road: Road, lane: Lane, position: int
    ) -> Tuple[float, float]:
        """
        Convert road position to (x, y) coordinates on the plot.

        Road R1 (vertical):
            - LEFT lane: x = center - 0.5
            - RIGHT lane: x = center + 0.5
            - y = position (from bottom to top)

        Road R2 (horizontal):
            - LEFT lane: y = center + 0.5
            - RIGHT lane: y = center - 0.5
            - x = position (from left to right)
        """
        center = self.L_TOTAL / 2

        if road == Road.R1:  # Vertical road (North-South)
            if lane == Lane.LEFT:
                x = center - 0.5
            else:  # RIGHT
                x = center + 0.5
            y = position
        else:  # Road.R2 - Horizontal road (West-East)
            if lane == Lane.LEFT:
                y = center + 0.5
            else:  # RIGHT
                y = center - 0.5
            x = position

        return x, y

    def _draw_roads(self):
        """Draw the road infrastructure (lanes and intersection)."""
        center = self.L_TOTAL / 2

        # Draw Road R1 (vertical) - two lanes
        for lane_offset in [-0.5, 0.5]:
            x = center + lane_offset
            self.ax.plot([x, x], [0, self.L_TOTAL], "k-", linewidth=2, alpha=0.3)

        # Draw Road R2 (horizontal) - two lanes
        for lane_offset in [-0.5, 0.5]:
            y = center + lane_offset
            self.ax.plot([0, self.L_TOTAL], [y, y], "k-", linewidth=2, alpha=0.3)

        # Highlight intersection zone
        intersection_rect = Rectangle(
            (self.intersection_start - 0.5, self.intersection_start - 0.5),
            self.intersection_end - self.intersection_start,
            self.intersection_end - self.intersection_start,
            linewidth=2,
            edgecolor="orange",
            facecolor="yellow",
            alpha=0.2,
            zorder=0,
        )
        self.ax.add_patch(intersection_rect)

        # Draw stop lines
        stop_line_pos = self.intersection_start - 0.5
        # R1 stop line (horizontal line before intersection)
        self.ax.plot(
            [center - 1, center + 1],
            [stop_line_pos, stop_line_pos],
            "r--",
            linewidth=2,
            alpha=0.5,
        )
        # R2 stop line (vertical line before intersection)
        self.ax.plot(
            [stop_line_pos, stop_line_pos],
            [center - 1, center + 1],
            "r--",
            linewidth=2,
            alpha=0.5,
        )

    def _draw_traffic_lights(self):
        """Draw traffic light indicators."""
        center = self.L_TOTAL / 2
        offset = 3

        # Traffic light for R1 (vertical road) - positioned to the side
        r1_color = (
            "green"
            if self.model.traffic_light[Road.R1] == TrafficLightState.GREEN
            else "red"
        )
        r1_light = plt.Circle(
            (center + offset, self.intersection_start - 2),
            0.8,
            color=r1_color,
            zorder=10,
        )
        self.ax.add_patch(r1_light)
        self.ax.text(
            center + offset,
            self.intersection_start - 4,
            "R1",
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
        )

        # Traffic light for R2 (horizontal road) - positioned to the side
        r2_color = (
            "green"
            if self.model.traffic_light[Road.R2] == TrafficLightState.GREEN
            else "red"
        )
        r2_light = plt.Circle(
            (self.intersection_start - 2, center + offset),
            0.8,
            color=r2_color,
            zorder=10,
        )
        self.ax.add_patch(r2_light)
        self.ax.text(
            self.intersection_start - 4,
            center + offset,
            "R2",
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
        )

    def _draw_vehicles(self):
        """Draw all vehicles as black cells (or red if collided)."""
        for vehicle in self.model.vehicles:
            x, y = self._get_road_coordinates(
                vehicle.road, vehicle.lane, vehicle.position
            )

            # Color: red for collided vehicles, black for normal
            color = "red" if vehicle.collided else "black"

            # Draw vehicle as a square
            vehicle_square = Rectangle(
                (x - 0.4, y - 0.4),
                0.8,
                0.8,
                facecolor=color,
                edgecolor="white",
                linewidth=1,
                zorder=5,
            )
            self.ax.add_patch(vehicle_square)

            # Optionally, show velocity as text inside the cell
            if not vehicle.collided:
                self.ax.text(
                    x,
                    y,
                    str(vehicle.velocity),
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="white",
                    fontweight="bold",
                )

    def _draw_info_text(self):
        """Draw simulation statistics."""
        # Calculate current average metrics
        avg_travel_time = (
            self.model.total_travel_time / self.model.completed_vehicles
            if self.model.completed_vehicles > 0
            else 0
        )
        avg_speed = (
            self.model.total_distance_traveled / self.model.total_travel_time
            if self.model.total_travel_time > 0
            else 0
        )

        info_text = (
            f"Time: {self.model.time_step}\n"
            f"Vehicles: {len(self.model.vehicles)}\n"
            f"Total Vehicles: {self.model.N_vehicles}\n"
            f"Completed: {self.model.completed_vehicles}\n"
            f"Lateral Collisions: {self.model.N_lateral}\n"
            f"Rear-end Collisions: {self.model.N_rear_end}\n"
            f"Throughput: {self.model.throughput}\n"
            f"Avg Travel Time: {avg_travel_time:.2f} steps\n"
            f"Avg Speed: {avg_speed:.2f} cells/step"
        )
        self.ax.text(
            0.02,
            0.98,
            info_text,
            transform=self.ax.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
        )

    def _update_frame(self, frame):
        """Update function for animation - called for each frame."""
        # Clear the axis
        self.ax.clear()
        self._setup_plot()

        # Step the simulation
        self.model.update_traffic_light()
        self.model.inject_vehicle()
        self.model.apply_nasch_rules()

        # Draw everything
        self._draw_roads()
        self._draw_traffic_lights()
        self._draw_vehicles()
        self._draw_info_text()

        return self.ax.patches

    def animate(self, frames: int = 500, save_path: str = None):
        """
        Run the animation.

        Args:
            frames: Number of frames (simulation steps) to run
            save_path: If provided, save animation to this file path (e.g., 'animation.mp4')
        """
        anim = animation.FuncAnimation(
            self.fig,
            self._update_frame,
            frames=frames,
            interval=self.interval,
            blit=False,
            repeat=False,
        )

        if save_path:
            print(f"Saving animation to {save_path}...")
            Writer = (
                animation.writers["pillow"]
                if save_path.endswith(".gif")
                else animation.FFMpegWriter
            )
            writer = Writer(
                fps=10, metadata=dict(artist="Traffic Simulation"), bitrate=1800
            )
            anim.save(save_path, writer=writer)
            print(f"Animation saved to {save_path}")
        else:
            plt.show()

        return anim


def create_and_run_visualization(
    length: int = 200,
    vmax: int = 5,
    t_green: int = 40,
    injection_rate: float = 0.1,
    p_b: float = 0.1,
    p_chg: float = 0.8,
    p_red: float = 0.01,
    p_skid: float = 0.01,
    allow_lane_changes: bool = True,
    frames: int = 500,
    interval: int = 100,
    save_path: str = None,
):
    """
    Convenience function to create and run a visualization.

    Args:
        length: Road length
        vmax: Maximum velocity
        t_green: Green light period
        injection_rate: Vehicle injection rate
        p_b: Random braking probability
        p_chg: Lane change probability
        p_red: Red light violation probability
        p_skid: Braking failure probability
        frames: Number of animation frames
        interval: Time between frames (ms)
        save_path: Path to save animation (optional)
    """
    from parameters import ModelParameters

    # Create model
    params = ModelParameters(
        p_b=p_b,
        p_chg=p_chg,
        p_red=p_red,
        p_skid=p_skid,
        allow_lane_changes=allow_lane_changes,
    )
    model = IntersectionModel(
        length=length,
        vmax=vmax,
        t_green=t_green,
        injection_rate=injection_rate,
        params=params,
    )

    # Create visualizer and run animation
    visualizer = TrafficSimulationVisualizer(model, interval=interval)
    return visualizer.animate(frames=frames, save_path=save_path)


if __name__ == "__main__":
    # Example usage
    print("Starting traffic simulation visualization...")
    create_and_run_visualization(
        length=100,  # Shorter road for better visibility
        vmax=5,
        t_green=30,
        injection_rate=0.15,
        p_b=0.1,
        p_chg=0.8,
        p_red=0.05,
        p_skid=0.05,
        frames=500,
        interval=100,  # 100ms between frames
        save_path=None,  # Set to 'traffic_animation.gif' to save
    )
