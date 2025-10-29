import csv
import os
from pathlib import Path
from datetime import datetime
from typing import Optional


class CSVLogger:
    """
    Logger that stores simulation data to a CSV file.
    Each row represents a single simulation run with its parameters and results.
    """

    def __init__(self, filename: str = "simulation_results.csv", append: bool = True):
        """
        Initialize the CSV logger.

        Args:
            filename: Name of the CSV file to write to
            append: If True, append to existing file. If False, overwrite.
        """
        self.filename = filename
        self.append = append
        self.fieldnames = [
            # Timestamp
            "timestamp",
            # Model parameters
            "length",
            "vmax",
            "t_green",
            "injection_rate",
            "p_b",
            "p_chg",
            "p_red",
            "p_skid",
            "steps",
            # Metrics
            "n_lateral",
            "n_rear_end",
            "n_vehicles",
            "throughput",
            "lateral_to_rear_end_ratio",
            "time",
        ]

        # Create file with header if it doesn't exist
        if not self.append or not os.path.exists(self.filename):
            self._write_header()

    def _write_header(self):
        """Write the CSV header to the file."""
        with open(self.filename, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writeheader()

    def log(self, data: dict):
        """
        Log custom data dictionary to the CSV file.

        Args:
            data: Dictionary with keys matching fieldnames
        """
        # Add timestamp if not present
        if "timestamp" not in data:
            data["timestamp"] = datetime.now().isoformat()

        with open(self.filename, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writerow(data)

    def clear(self):
        """Clear the CSV file and write a new header."""
        self._write_header()
