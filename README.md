# Traffic Simulation

Traffic intersection simulation using the Nagel-Schreckenberg model with weather effects and collision detection.

## Project Structure

- `entities.py` - Core entity definitions (enumerations and Vehicle class)
  - Enumerations: Road, Lane, TrafficLightState, Weather
  - Vehicle class with position, velocity, and collision tracking
- `parameters.py` - Model parameters and configuration
  - ModelParameters class for simulation behavior control
  - Pre-defined parameter sets (NORMAL_PARAMS, RAINY_PARAMS)
- `model.py` - Main IntersectionModel class with simulation logic
- `main.py` - Entry point to run the simulation
- `pyproject.toml` - Project dependencies and configuration (uv)

## Setup with uv

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

### Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Initialize the project

```bash
uv sync
```

## Running the Simulation

```bash
uv run main.py
```

## Features

- Nagel-Schreckenberg traffic flow model
- Two-road intersection with traffic lights
- Weather conditions (Normal/Rainy) affecting driving behavior
- Collision detection (lateral and rear-end)
- Metrics tracking (throughput, accidents)
