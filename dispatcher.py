"""
Dispatcher for running multiple traffic simulations with different parameter combinations.
Supports both multiprocessing (for cluster/parallel execution) and threading.
"""

import itertools
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import Iterator, Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, asdict
import time
from datetime import datetime

from model import IntersectionModel
from parameters import ModelParameters
from logger import CSVLogger


@dataclass
class SimulationConfig:
    """Configuration for a single simulation run."""

    # System parameters
    length: int
    vmax: int
    t_green: int
    injection_rate: float

    # Model parameters
    p_b: float
    p_chg: float
    p_red: float
    p_skid: float

    # Simulation parameters
    steps: int = 100000
    metrics_start_step: int = 0

    # Optional identifier
    config_id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return asdict(self)


def run_single_simulation(config: SimulationConfig) -> Dict[str, Any]:
    """
    Run a single simulation with the given configuration.

    Args:
        config: SimulationConfig object with all parameters

    Returns:
        Dictionary containing both parameters and metrics
    """
    start_time = time.time()

    # Create model parameters
    params = ModelParameters(
        p_b=config.p_b,
        p_chg=config.p_chg,
        p_red=config.p_red,
        p_skid=config.p_skid,
    )

    # Create and run model
    model = IntersectionModel(
        length=config.length,
        vmax=config.vmax,
        t_green=config.t_green,
        injection_rate=config.injection_rate,
        params=params,
        metrics_start_step=config.metrics_start_step,
    )

    model.run_simulation(steps=config.steps)

    # Get results
    metrics = model.get_metrics()
    params_dict = model.get_params()

    # Combine with configuration metadata
    result = {
        **params_dict,
        **metrics,
        "config_id": config.config_id,
        "total_time": time.time() - start_time,
    }

    return result


class SimulationDispatcher:
    """
    Dispatcher for running multiple simulations with different parameter combinations.
    """

    def __init__(
        self,
        output_file: str = "simulation_results.csv",
        use_multiprocessing: bool = True,
        max_workers: Optional[int] = None,
        verbose: bool = True,
    ):
        """
        Initialize the dispatcher.

        Args:
            output_file: CSV file to store results
            use_multiprocessing: If True, use ProcessPoolExecutor, else ThreadPoolExecutor
            max_workers: Maximum number of parallel workers (None = CPU count)
            verbose: Print progress information
        """
        self.output_file = output_file
        self.use_multiprocessing = use_multiprocessing
        self.max_workers = max_workers or mp.cpu_count()
        self.verbose = verbose
        self.logger = CSVLogger(filename=output_file, append=True)

    def run(
        self,
        configs: Iterator[SimulationConfig] | List[SimulationConfig],
    ) -> List[Dict[str, Any]]:
        """
        Run simulations for all configurations.

        Args:
            configs: Iterator or list of SimulationConfig objects

        Returns:
            List of result dictionaries
        """
        # Convert to list if iterator
        config_list = list(configs)
        total_sims = len(config_list)

        if self.verbose:
            print(f"Starting {total_sims} simulations...")
            print(
                f"Using {'multiprocessing' if self.use_multiprocessing else 'threading'}"
            )
            print(f"Max workers: {self.max_workers}")
            print(f"Results will be saved to: {self.output_file}")
            print("-" * 80)

        results = []
        start_time = time.time()

        ExecutorClass = (
            ProcessPoolExecutor if self.use_multiprocessing else ThreadPoolExecutor
        )

        with ExecutorClass(max_workers=self.max_workers) as executor:
            future_to_config = {
                executor.submit(run_single_simulation, config): config
                for config in config_list
            }

            # Process completed simulations
            for i, future in enumerate(as_completed(future_to_config), 1):
                config = future_to_config[future]

                try:
                    result = future.result()
                    results.append(result)

                    # Log to CSV
                    self.logger.log(result)

                    if self.verbose:
                        elapsed = time.time() - start_time
                        avg_time = elapsed / i
                        eta = avg_time * (total_sims - i)
                        print(
                            f"[{i}/{total_sims}] Completed config_id={config.config_id} "
                            f"| Elapsed: {elapsed:.1f}s | ETA: {eta:.1f}s"
                        )

                except Exception as exc:
                    print(
                        f"Simulation {config.config_id} generated an exception: {exc}"
                    )

        total_time = time.time() - start_time

        if self.verbose:
            print("-" * 80)
            print(f"All simulations completed in {total_time:.2f} seconds")
            print(f"Average time per simulation: {total_sims/total_time:.2f} seconds")
            print(f"Results saved to: {self.output_file}")

        return results


def generate_parameter_grid(
    length_values: List[int],
    vmax_values: List[int],
    t_green_values: List[int],
    injection_rate_values: List[float],
    p_b_values: List[float],
    p_chg_values: List[float],
    p_red_values: List[float],
    p_skid_values: List[float],
    steps: int = 100000,
    metrics_start_step: int = 0,
) -> List[SimulationConfig]:
    """
    Generate a grid of all parameter combinations.

    Args:
        *_values: Lists of values for each parameter
        steps: Number of simulation steps
        metrics_start_step: Time step at which to start recording metrics

    Returns:
        List of SimulationConfig objects
    """
    configs = []
    config_id = 0

    for (
        length,
        vmax,
        t_green,
        injection_rate,
        p_b,
        p_chg,
        p_red,
        p_skid,
    ) in itertools.product(
        length_values,
        vmax_values,
        t_green_values,
        injection_rate_values,
        p_b_values,
        p_chg_values,
        p_red_values,
        p_skid_values,
    ):
        config = SimulationConfig(
            length=length,
            vmax=vmax,
            t_green=t_green,
            injection_rate=injection_rate,
            p_b=p_b,
            p_chg=p_chg,
            p_red=p_red,
            p_skid=p_skid,
            steps=steps,
            metrics_start_step=metrics_start_step,
            config_id=config_id,
        )
        configs.append(config)
        config_id += 1

    return configs
