from dispatcher import (
    SimulationDispatcher,
    generate_parameter_grid,
)
from entities import Weather

# Default System Parameters
L_INIT = 200
V_MAX_INIT = 5
T_GREEN_INIT = 40
INJECTION_RATE_INIT = 0.1

if __name__ == "__main__":
    # Example usage of the dispatcher
    # You can modify this to run different parameter combinations

    # Option 1: Simple weather comparison with default parameters
    base_config = {
        "length": L_INIT,
        "vmax": V_MAX_INIT,
        "t_green": T_GREEN_INIT,
        "injection_rate": INJECTION_RATE_INIT,
    }

    # Option 2: Uncomment to run a parameter grid search
    configs = generate_parameter_grid(
        length_values=[200],
        vmax_values=[5],
        t_green_values=[30, 40, 50],
        injection_rate_values=[0.05, 0.1, 0.15],
        p_b_values=[0.1, 0.15],
        p_chg_values=[0.4, 0.8],
        p_red_values=[0.001, 0.01, 0.05],
        p_skid_values=[0.05, 0.1],
        steps=10000,
        metrics_start_step=5000,
    )

    # Create dispatcher with multiprocessing enabled
    dispatcher = SimulationDispatcher(
        output_file="simulation_results.csv",
        use_multiprocessing=True,  # Set to False to use threading instead
        max_workers=None,  # None = use all available CPU cores
        verbose=True,
    )

    # Run all simulations
    results = dispatcher.run(configs)

    # Print summary
    print("\n" + "=" * 80)
    print("SIMULATION SUMMARY")
    print("=" * 80)
    # for result in results:
    #     print(f"\nConfig {result['config_id']}")
    #     print(f"  Lateral collisions: {result['n_lateral']}")
    #     print(f"  Rear-end collisions: {result['n_rear_end']}")
    #     print(f"  Total vehicles: {result['n_vehicles']}")
    #     print(f"  Throughput: {result['throughput']}")
    #     print(f"  Simulation time: {result['time']:.2f}s")
