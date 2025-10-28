from model import IntersectionModel
from parameters import NORMAL_PARAMS, RAINY_PARAMS
import time

# Fixed System Parameters
L_INIT = 200
V_MAX_INIT = 5
T_GREEN_INIT = 40
INJECTION_RATE_INIT = 1

if __name__ == "__main__":
    t1 = time.time()
    # Simulation under NORMAL conditions
    model_normal = IntersectionModel(
        L_INIT, V_MAX_INIT, T_GREEN_INIT, INJECTION_RATE_INIT, NORMAL_PARAMS
    )
    model_normal.run_simulation(steps=1000)

    t2 = time.time()
    print(f"\n--- Simulation Time (NORMAL): {t2 - t1:.2f} seconds ---")

    metrics_normal = model_normal.get_metrics()

    print("\n--- NORMAL WEATHER METRICS ---")
    for key, value in metrics_normal.items():
        print(f"{key}: {value}")
