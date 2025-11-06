from dispatcher import (
    SimulationDispatcher,
    generate_parameter_grid,
)
from entities import Weather
import numpy as np

if __name__ == "__main__":
    # Fixed parameters
    LENGTH = 100
    P_B = 0.1
    P_CHG = 0.1
    P_RED = 0.1
    P_SKID = 0.0
    T_GREEN = 40
    STEPS = 100000
    REPLICATIONS = 5

    # Variable parameters
    injection_rates = np.linspace(0.05, 1.0, 20)
    vmax_values = [2, 3, 4, 5, 6, 7]

    print(f"Number of injection rate values: {len(injection_rates)}")
    print(f"Injection rates: {injection_rates}")
    print(f"vmax values: {vmax_values}")
    print(f"Number of replications per configuration: {REPLICATIONS}")
    print(
        f"Total simulations: {len(injection_rates) * len(vmax_values) * REPLICATIONS}"
    )

    configs = generate_parameter_grid(
        length_values=[LENGTH],
        vmax_values=vmax_values,
        t_green_values=[T_GREEN],
        injection_rate_values=injection_rates.tolist(),
        p_b_values=[P_B],
        p_chg_values=[P_CHG],
        p_red_values=[P_RED],
        p_skid_values=[P_SKID],
        steps=STEPS,
        metrics_start_step=0,
        replications=REPLICATIONS,
    )

    print(f"Generated {len(configs)} simulation configurations")
    print(f"\nFirst configuration:")
    print(configs[0])

    output_file = "vmax_test.csv"

    dispatcher = SimulationDispatcher(
        output_file=output_file,
        use_multiprocessing=True,
        max_workers=None,  # Use all available CPU cores
        verbose=True,
    )

    # Run all simulations
    results = dispatcher.run(configs)

    print(f"\nSimulations complete! Results saved to {output_file}")
