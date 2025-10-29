# Traffic Intersection Simulation

A traffic intersection simulation using an extended **Nagel-Schreckenberg (NaSch) model** with collision detection, traffic lights, and weather effects. The project includes a parallel simulation dispatcher for running parameter grid searches efficiently.

## Overview

This simulation models a two-road intersection with traffic lights, where vehicles follow the NaSch cellular automaton rules with additional realistic features:

- **Red light violations** with configurable probability
- **Rear-end collisions** from braking failures (skidding)
- **Lateral collisions** when vehicles from perpendicular roads enter the intersection simultaneously
- **Weather conditions** affecting driving behavior (normal vs. rainy)
- **Parallel execution** support for running multiple simulations with different parameter combinations

## Features

### Core Model

- **Nagel-Schreckenberg cellular automaton** for realistic traffic flow
- **Two-road intersection** (R1: North-South, R2: East-West)
- **Dual lanes** per road (left and right)
- **Traffic light system** with configurable green light duration
- **Vehicle injection** with configurable rate

### Collision Detection

- **Lateral collisions**: Vehicles from perpendicular roads entering intersection simultaneously
- **Rear-end collisions**: Braking failures when vehicles can't stop in time
- **Collision tracking**: All collisions are recorded and affect traffic flow

### Parametrization

- **Behavioral parameters**:
  - `p_b`: Random braking probability (NaSch)
  - `p_chg`: Lane change probability
  - `p_red`: Red light violation probability
  - `p_skid`: Braking failure probability (rear-end collision)
- **System parameters**:
  - `length`: Road length in cells
  - `vmax`: Maximum vehicle velocity
  - `t_green`: Traffic light green duration
  - `injection_rate`: Vehicle injection probability

### Performance

- **Multiprocessing support** for parallel simulation execution
- **CSV logging** for automatic data collection
- **Parameter grid generation** for systematic exploration

## Project Structure

```
.
├── entities.py          # Core entity definitions (Road, Lane, Vehicle, etc.)
├── parameters.py        # ModelParameters class and preset configurations
├── model.py            # IntersectionModel - main simulation engine
├── dispatcher.py       # SimulationDispatcher for parallel execution
├── logger.py           # CSVLogger for results storage
├── main.py             # Entry point for batch simulations
├── single_sim.py       # Entry point for single simulation runs
├── main.ipynb          # Jupyter notebook for interactive analysis
├── pyproject.toml      # Project dependencies and metadata
└── README.md           # This file
```

### Module Details

#### `entities.py`

Defines core data structures:

- **Enumerations**: `Road`, `Lane`, `TrafficLightState`, `Weather`
- **Vehicle class**: Tracks position, velocity, collision status, and individual parameters

#### `parameters.py`

Configuration management:

- **ModelParameters**: Container for behavioral parameters (`p_b`, `p_chg`, `p_red`, `p_skid`)
- **Presets**: `NORMAL_PARAMS` and `RAINY_PARAMS` for different weather conditions

#### `model.py`

Main simulation engine:

- **IntersectionModel**: Manages roads, vehicles, traffic lights, and collision detection
- **NaSch rules**: Acceleration, deceleration, randomization, and movement
- **Intersection logic**: Red light handling, collision detection
- **Metrics collection**: Tracks collisions, throughput, and vehicle counts

#### `dispatcher.py`

Parallel execution framework:

- **SimulationDispatcher**: Runs multiple simulations with multiprocessing or threading
- **SimulationConfig**: Configuration dataclass for individual runs
- **generate_parameter_grid()**: Creates all combinations of parameter values
- **Progress tracking**: Real-time progress updates and ETA calculation

#### `logger.py`

Data persistence:

- **CSVLogger**: Writes simulation results to CSV with timestamps
- **Automatic header management**: Creates file structure on first use
- **Append mode**: Supports incremental result collection

## Setup

This project uses [uv](https://github.com/astral-sh/uv) for fast, reliable Python package management.

### Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Initialize the project

```bash
uv sync
```

## Usage

### Single Simulation

Run a single simulation with default parameters:

```bash
uv run single_sim.py
```

This will execute one simulation under normal weather conditions and print metrics:

- Lateral collisions (red light violations leading to crashes)
- Rear-end collisions (braking failures)
- Total vehicles processed
- Throughput (vehicles passing through intersection)
- Simulation execution time

### Batch Simulations (Parameter Grid)

Run multiple simulations with different parameter combinations:

```bash
uv run main.py
```

The `main.py` script:

- Generates a grid of parameter combinations
- Runs simulations in parallel using all available CPU cores
- Saves results to `simulation_results.csv`
- Displays progress with ETA

**Example configuration** (from `main.py`):

```python
configs = generate_parameter_grid(
    length_values=[200],
    vmax_values=[5],
    t_green_values=[30, 40, 50],           # Test different light durations
    injection_rate_values=[0.05, 0.1, 0.15],  # Test different traffic densities
    p_b_values=[0.1, 0.15],                # Test different braking behaviors
    p_chg_values=[0.4, 0.8],               # Test lane change rates
    p_red_values=[0.001, 0.01, 0.05],      # Test red light violation rates
    p_skid_values=[0.05, 0.1],             # Test skidding probabilities
    steps=100000,                          # Simulation length
)
```

This example generates **2 × 3 × 3 × 2 × 2 × 3 × 2 = 432 simulations**.

### Customization

#### Modify simulation parameters

Edit `main.py` to change the parameter grid:

```python
# Focus on green light duration effects
configs = generate_parameter_grid(
    length_values=[200],
    vmax_values=[5],
    t_green_values=[20, 30, 40, 50, 60],  # More granular
    injection_rate_values=[0.1],
    p_b_values=[0.1],
    p_chg_values=[0.8],
    p_red_values=[0.01],
    p_skid_values=[0.05],
    steps=100000,
)
```

#### Configure parallel execution

```python
dispatcher = SimulationDispatcher(
    output_file="my_results.csv",
    use_multiprocessing=True,  # False for threading
    max_workers=8,             # None = use all cores
    verbose=True,              # Show progress
)
```

#### Use preset weather conditions

```python
from parameters import NORMAL_PARAMS, RAINY_PARAMS
from model import IntersectionModel

# Normal weather
model = IntersectionModel(
    length=200,
    vmax=5,
    t_green=40,
    injection_rate=0.1,
    params=NORMAL_PARAMS
)
model.run_simulation(steps=100000)

# Rainy weather (higher p_b and p_skid, lower p_chg and p_red)
model_rainy = IntersectionModel(
    length=200,
    vmax=5,
    t_green=40,
    injection_rate=0.1,
    params=RAINY_PARAMS
)
model_rainy.run_simulation(steps=100000)
```

### Interactive Analysis

Use the Jupyter notebook for interactive exploration:

```bash
uv run jupyter lab main.ipynb
```

The notebook allows you to:

- Run simulations with custom parameters
- Visualize results in real-time
- Analyze collision patterns
- Compare different configurations

## Output

### Metrics

Each simulation generates the following metrics:

- **`n_lateral`**: Number of lateral collisions (intersection crashes)
- **`n_rear_end`**: Number of rear-end collisions (braking failures)
- **`n_vehicles`**: Total vehicles injected into the system
- **`throughput`**: Number of vehicles that successfully passed through the intersection
- **`lateral_to_rear_end_ratio`**: Ratio of lateral to rear-end collisions
- **`time`**: Simulation execution time (seconds)

### CSV Output

Results are automatically saved to CSV with the following columns:

```csv
timestamp,config_id,length,vmax,t_green,injection_rate,p_b,p_chg,p_red,p_skid,steps,n_lateral,n_rear_end,n_vehicles,throughput,lateral_to_rear_end_ratio,time,total_time
```

Example row:

```csv
2025-10-29T14:23:45.123456,0,200,5,40,0.1,0.1,0.8,0.001,0.05,100000,15,342,8234,8177,0.044,12.34,12.45
```

## Model Details

### NaSch Update Rules

For each vehicle at each time step:

1. **Acceleration**: `v → min(v + 1, v_max)`
2. **Deceleration (safety)**: `v → min(v, gap_ahead)`
3. **Red light check**:
   - If red light ahead: `v → min(v, gap_to_intersection)` (unless violating with probability `p_red`)
4. **Randomization**: With probability `p_b`: `v → max(v - 1, 0)`
5. **Braking failure check**: If `v > gap_ahead` and random < `p_skid`, rear-end collision occurs
6. **Movement**: `position → position + v`

### Collision Detection

#### Rear-End Collisions

Occur when a vehicle fails to brake in time (probability `p_skid`):

- Both vehicles involved are marked as collided
- Vehicles stop at collision point
- Traffic flow is blocked

#### Lateral Collisions

Occur when vehicles from both roads enter the intersection simultaneously:

- Happens when both roads have vehicles violating red lights
- All entering vehicles are marked as collided
- Vehicles stop at intersection entrance

### Weather Effects

Rainy conditions modify parameters:

- **`p_b`**: 0.1 → 0.15 (more cautious braking)
- **`p_chg`**: 0.8 → 0.4 (fewer lane changes)
- **`p_red`**: 0.001 → 0.05 (more cautious, fewer violations)
- **`p_skid`**: 0.05 → 0.1 (more braking failures/aquaplaning)

## Performance

The parallel dispatcher provides significant speedup:

- **Single-threaded**: ~12 seconds per 100k-step simulation
- **Multiprocessing (8 cores)**: ~7.5x speedup for 432 simulations
- **Memory efficient**: Each process handles its own simulation independently

## Analysis Ideas

Use the CSV output to explore questions like:

- How does traffic light timing affect throughput?
- What injection rate maximizes throughput while minimizing collisions?
- How do weather conditions affect collision rates?
- What's the relationship between red light violations and lateral collisions?
- How does `p_skid` affect rear-end collision frequency?
