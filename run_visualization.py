"""
Simple script to run the traffic simulation visualization.
"""

from visualizer import create_and_run_visualization
import sys

if __name__ == "__main__":

    # Check for rainy condition parameter
    rainy = "--rainy" in sys.argv or "-r" in sys.argv

    # High-resolution video settings
    DPI = 170  # High resolution (200 DPI)
    FPS = 4  # Smooth 30 fps
    BITRATE = 8000  # High quality bitrate (8000 kbps)

    print("=" * 80)
    print("TRAFFIC INTERSECTION SIMULATION - VISUALIZATION")
    print("=" * 80)
    print(f"\nWeather condition: {'RAINY' if rainy else 'NORMAL'}")
    print(f"Video settings: {DPI} DPI, {FPS} FPS, {BITRATE} kbps bitrate")
    print("Starting visualization...")
    print("Close the window to end the simulation.\n")

    if rainy:
        # Rainy conditions: more cautious driving
        create_and_run_visualization(
            length=100,
            vmax=2,
            t_green=50,
            injection_rate=0.5,
            p_b=0.15,
            p_chg=0.4,
            p_red=0.01,
            p_skid=0.1,
            frames=1000,
            interval=50,
            save_path="animation_rainy.mp4",
            dpi=DPI,
            fps=FPS,
            bitrate=BITRATE,
        )
    else:
        # Normal conditions
        create_and_run_visualization(
            length=150,
            vmax=5,
            t_green=200,
            injection_rate=0.5,
            p_b=0.2,
            p_chg=1,
            p_red=0.05,
            p_skid=0.01,
            frames=500,
            interval=1,
            dpi=DPI,
            fps=FPS,
            bitrate=BITRATE,
            save_path="animation_normal.mp4",
        )

    print("\nVisualization complete!")
