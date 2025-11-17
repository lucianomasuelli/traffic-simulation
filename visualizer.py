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

    def __init__(self, model: IntersectionModel, interval: int = 100, dpi: int = 150):
        """
        Initialize the visualizer.

        Args:
            model: IntersectionModel instance to visualize
            interval: Animation interval in milliseconds (time between frames)
            dpi: Dots per inch for the figure (higher = better resolution)
        """
        self.model = model
        self.interval = interval
        self.dpi = dpi

        # Calculate scaling factor based on DPI (baseline is 100 DPI)
        self.scale = dpi / 100.0

        # Create figure and axis
        self.fig, self.ax = plt.subplots(figsize=(16, 16), dpi=dpi)

        # Grid dimensions
        self.L_TOTAL = model.L_TOTAL
        self.intersection_start = model.intersection_start
        self.intersection_end = model.intersection_end

        # Visual settings that scale with DPI
        self.cell_size = 3.0 * self.scale  # Size of each cell (car size)
        self.lane_width = 4.0 * self.scale  # Width of each lane

        # Color cycling for vehicles
        self.vehicle_colors = [
            "#FF6B6B",  # Red
            "#1EE7DA",  # Teal
            "#2711CC",  # Blue
            "#E8551B",  # Light Salmon
            "#2CC514",  # Mint
            "#E9C123",  # Yellow
            "#AF4ED8",  # Purple
            "#67BEED",  # Light Blue
            "#F8B739",  # Orange
            "#52B788",  # Green
        ]
        self.color_index = 0
        self.vehicle_color_map = {}  # Maps vehicle id to color

        # Set up the plot
        self._setup_plot()

    def _setup_plot(self):
        """Set up the plot with grid and labels."""
        self.ax.set_xlim(-5, self.L_TOTAL + 5)
        self.ax.set_ylim(-5, self.L_TOTAL + 5)
        self.ax.set_aspect("equal")
        # Remove grid for cleaner visualization
        self.ax.grid(False)
        self.ax.set_xlabel(
            "Position (cells)", fontsize=int(14 * self.scale), fontweight="bold"
        )
        self.ax.set_ylabel(
            "Position (cells)", fontsize=int(14 * self.scale), fontweight="bold"
        )
        self.ax.set_title(
            "Traffic Intersection Simulation",
            fontsize=int(16 * self.scale),
            fontweight="bold",
        )

    def _get_road_coordinates(
        self, road: Road, lane: Lane, position: int
    ) -> Tuple[float, float]:
        """
        Convert road position to (x, y) coordinates on the plot.

        Road R1 (vertical):
            - LEFT lane: x = center - lane_width/2
            - RIGHT lane: x = center + lane_width/2
            - y = position (from bottom to top)

        Road R2 (horizontal):
            - LEFT lane: y = center + lane_width/2
            - RIGHT lane: y = center - lane_width/2
            - x = position (from left to right)
        """
        center = self.L_TOTAL / 2

        if road == Road.R1:  # Vertical road (North-South)
            if lane == Lane.LEFT:
                x = center - self.lane_width / 2
            else:  # RIGHT
                x = center + self.lane_width / 2
            y = position
        else:  # Road.R2 - Horizontal road (West-East)
            if lane == Lane.LEFT:
                y = center + self.lane_width / 2
            else:  # RIGHT
                y = center - self.lane_width / 2
            x = position

        return x, y

    def _draw_roads(self):
        """Draw the road infrastructure (lanes and intersection)."""
        center = self.L_TOTAL / 2

        # Draw Road R1 (vertical) - two lanes with scaled line width
        for lane_offset in [-self.lane_width / 2, self.lane_width / 2]:
            x = center + lane_offset
            self.ax.plot(
                [x, x], [0, self.L_TOTAL], "k-", linewidth=4 * self.scale, alpha=0.5
            )

        # Draw Road R2 (horizontal) - two lanes with scaled line width
        for lane_offset in [-self.lane_width / 2, self.lane_width / 2]:
            y = center + lane_offset
            self.ax.plot(
                [0, self.L_TOTAL], [y, y], "k-", linewidth=4 * self.scale, alpha=0.5
            )

        # Highlight intersection zone (adjusted for wider lanes)
        intersection_rect = Rectangle(
            (
                self.intersection_start - self.lane_width,
                self.intersection_start - self.lane_width,
            ),
            self.intersection_end - self.intersection_start + 2 * self.lane_width,
            self.intersection_end - self.intersection_start + 2 * self.lane_width,
            linewidth=3 * self.scale,
            edgecolor="orange",
            facecolor="yellow",
            alpha=0.2,
            zorder=0,
        )
        self.ax.add_patch(intersection_rect)

        # Draw stop lines with scaled width
        stop_line_pos = self.intersection_start - 0.5
        # R1 stop line (horizontal line before intersection)
        self.ax.plot(
            [center - self.lane_width, center + self.lane_width],
            [stop_line_pos, stop_line_pos],
            "r--",
            linewidth=3 * self.scale,
            alpha=0.7,
        )
        # R2 stop line (vertical line before intersection)
        self.ax.plot(
            [stop_line_pos, stop_line_pos],
            [center - self.lane_width, center + self.lane_width],
            "r--",
            linewidth=3 * self.scale,
            alpha=0.7,
        )

    def _draw_traffic_lights(self):
        """Draw traffic light indicators."""
        center = self.L_TOTAL / 2
        offset = 5 * self.scale

        # Traffic light for R1 (vertical road) - scaled size
        r1_color = (
            "green"
            if self.model.traffic_light[Road.R1] == TrafficLightState.GREEN
            else "red"
        )
        r1_light = plt.Circle(
            (center + offset, self.intersection_start - 3 * self.scale),
            1.5 * self.scale,
            color=r1_color,
            zorder=10,
        )
        self.ax.add_patch(r1_light)
        self.ax.text(
            center + offset,
            self.intersection_start - 6 * self.scale,
            "R1",
            ha="center",
            va="center",
            fontsize=int(14 * self.scale),
            fontweight="bold",
        )

        # Traffic light for R2 (horizontal road) - scaled size
        r2_color = (
            "green"
            if self.model.traffic_light[Road.R2] == TrafficLightState.GREEN
            else "red"
        )
        r2_light = plt.Circle(
            (self.intersection_start - 3 * self.scale, center + offset),
            1.5 * self.scale,
            color=r2_color,
            zorder=10,
        )
        self.ax.add_patch(r2_light)
        self.ax.text(
            self.intersection_start - 6 * self.scale,
            center + offset,
            "R2",
            ha="center",
            va="center",
            fontsize=int(14 * self.scale),
            fontweight="bold",
        )

    def _draw_vehicles(self):
        """Draw all vehicles as larger circles with unique colors."""
        for vehicle in self.model.vehicles:
            x, y = self._get_road_coordinates(
                vehicle.road, vehicle.lane, vehicle.position
            )

            # Assign color to new vehicles
            if id(vehicle) not in self.vehicle_color_map:
                self.vehicle_color_map[id(vehicle)] = self.vehicle_colors[
                    self.color_index
                ]
                self.color_index = (self.color_index + 1) % len(self.vehicle_colors)

            # Color: red for collided vehicles, assigned color for normal
            if vehicle.collided:
                color = "red"
                edge_color = "darkred"
            else:
                color = self.vehicle_color_map[id(vehicle)]
                edge_color = "black"

            # Draw vehicle as a scaled circle with visible border
            vehicle_circle = plt.Circle(
                (x, y),
                self.cell_size / 2,
                facecolor=color,
                edgecolor=edge_color,
                linewidth=0.5 * self.scale,
                zorder=5,
            )
            self.ax.add_patch(vehicle_circle)

            # Always show velocity as text inside the circle with scaled font
            self.ax.text(
                x,
                y,
                str(vehicle.velocity),
                ha="center",
                va="center",
                fontsize=int(14 * self.scale),
                color="white",
                fontweight="bold",
                zorder=6,
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
            self.model.avg_velocities / len(self.model.vehicles)
            if len(self.model.vehicles) > 0
            else 0
        )

        info_text = (
            f"Time: {self.model.time_step}\n"
            f"Vehicles: {len(self.model.vehicles)}\n"
            f"Total Vehicles: {self.model.N_vehicles}\n"
            f"Completed: {self.model.completed_vehicles}\n"
            f"Lateral Collisions: {self.model.N_lateral}\n"
            f"Rear-end Collisions: {self.model.N_rear_end}\n"
            f"Avg Travel Time: {avg_travel_time:.2f} steps\n"
            f"Avg Speed: {avg_speed:.2f} cells/step"
        )
        self.ax.text(
            0.02,
            0.98,
            info_text,
            transform=self.ax.transAxes,
            fontsize=int(10 * self.scale),
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

    def animate(
        self,
        frames: int = 500,
        save_path: str = None,
        fps: int = 30,
        bitrate: int = 5000,
    ):
        """
        Run the animation.

        Args:
            frames: Number of frames (simulation steps) to run
            save_path: If provided, save animation to this file path (e.g., 'animation.mp4')
            fps: Frames per second for saved video (higher = smoother)
            bitrate: Video bitrate in kbps (higher = better quality)
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
            print(f"Settings: DPI={self.dpi}, FPS={fps}, Bitrate={bitrate}kbps")
            Writer = (
                animation.writers["pillow"]
                if save_path.endswith(".gif")
                else animation.FFMpegWriter
            )
            writer = Writer(
                fps=fps, metadata=dict(artist="Traffic Simulation"), bitrate=bitrate
            )
            anim.save(save_path, writer=writer, dpi=self.dpi)
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
    metrics_start_step: int = 0,
    frames: int = 500,
    interval: int = 100,
    save_path: str = None,
    dpi: int = 150,
    fps: int = 30,
    bitrate: int = 5000,
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
        metrics_start_step: Time step at which to start recording metrics
        frames: Number of animation frames
        interval: Time between frames (ms)
        save_path: Path to save animation (optional)
        dpi: Dots per inch for figure resolution (higher = better quality)
        fps: Frames per second for video (higher = smoother)
        bitrate: Video bitrate in kbps (higher = better quality)
    """
    from parameters import ModelParameters

    # Create model
    params = ModelParameters(
        p_b=p_b,
        p_chg=p_chg,
        p_red=p_red,
        p_skid=p_skid,
    )
    model = IntersectionModel(
        length=length,
        vmax=vmax,
        t_green=t_green,
        injection_rate=injection_rate,
        params=params,
    )

    # Create visualizer and run animation
    visualizer = TrafficSimulationVisualizer(model, interval=interval, dpi=dpi)
    return visualizer.animate(
        frames=frames, save_path=save_path, fps=fps, bitrate=bitrate
    )


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
