from entities import Weather


class ModelParameters:
    """Parameters that control the behavior of the traffic simulation model."""

    def __init__(
        self,
        p_b: float,
        p_chg: float,
        p_red: float,
        p_skid: float,
        weather: Weather,
    ):
        """
        Initialize model parameters.

        Args:
            p_b: Random braking probability (NaSch)
            p_chg: Lane change probability
            p_red: Red light violation probability
            p_skid: Braking failure probability (rear-end collision)
            weather: Weather condition for these parameters
        """
        self.p_b = p_b
        self.p_chg = p_chg
        self.p_red = p_red
        self.p_skid = p_skid
        self.weather = weather


# Pre-defined parameter sets
NORMAL_PARAMS = ModelParameters(
    p_b=0.1,  # Random Braking Probability (NaSch)
    p_chg=0.8,  # Lane Change Probability
    p_red=0.001,  # Red Light Violation Probability
    p_skid=0.05,  # Braking Failure Probability (Rear-end collision)
    weather=Weather.NORMAL,
)

RAINY_PARAMS = ModelParameters(
    p_b=0.15,  # Increased: longer braking distance/more cautious braking (0.1 * 1.5)
    p_chg=0.4,  # Reduced: discourages lane changes (0.8 * 0.5)
    p_red=0.05,  # Reduced: more cautious (0.1 * 0.5)
    p_skid=0.1,  # Increased: braking failure/aquaplaning (0.05 * 2.0)
    weather=Weather.RAINY,
)
