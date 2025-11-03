"""
Simple script to run the traffic simulation visualization.
"""

from visualizer import create_and_run_visualization

if __name__ == "__main__":
    print("=" * 80)
    print("TRAFFIC INTERSECTION SIMULATION - VISUALIZATION")
    print("=" * 80)
    print("\nStarting visualization...")
    print("Close the window to end the simulation.\n")

    # Run visualization with custom parameters
    create_and_run_visualization(
        length=100,  # Road length (shorter for better visibility)
        vmax=2,  # Maximum velocity
        t_green=50,  # Green light duration
        injection_rate=0.5,  # Vehicle injection rate (higher for more traffic)
        p_b=0.1,  # Random braking probability
        p_chg=0.8,  # Lane change probability
        p_red=0.1,  # Red light violation probability
        p_skid=0.01,  # Braking failure probability
        frames=1000,  # Number of simulation steps
        interval=50,  # Milliseconds between frames (50ms = 20 fps)
        save_path=None,  # Set to 'animation.gif' to save as GIF
    )

    print("\nVisualization complete!")
