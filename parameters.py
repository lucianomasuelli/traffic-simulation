from entities import Weather


class ModelParameters:
    """Parameters that control the behavior of the traffic simulation model."""

    def __init__(
        self,
        p_b: float,
        p_chg: float,
        p_red: float,
        p_skid: float,
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


# Pre-defined parameter sets
NORMAL_PARAMS = ModelParameters(
    p_b=0.1,  # Random Braking Probability (NaSch)
    p_chg=0.8,  # Lane Change Probability
    p_red=0.1,  # Red Light Violation Probability
    p_skid=0.05,  # Braking Failure Probability (Rear-end collision)
)

RAINY_PARAMS = ModelParameters(
    p_b=0.5,  # Increased: more probability of random braking 
    p_chg=0.2,  # Reduced: discourages lane changes
    p_red=0.05,  # Reduced: more cautious
    p_skid=0.9,  # Increased: braking failure/aquaplaning
)
