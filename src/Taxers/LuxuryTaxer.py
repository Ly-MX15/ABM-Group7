from .BaseTaxer import BaseTaxer


class LuxuryTaxer(BaseTaxer):
    """
    Luxury taxer class. Inherits from BaseTaxer. Groups agents into luxury and non-luxury classes and applies different
    tax rates to each group. The luxury class is defined as the top luxury_size fraction of the population, and is taxed
    at a higher rate than the non-luxury class by a factor of luxury_multiplier.

    Attributes:
        luxury_size (float): Fraction of the population that is considered luxury
        luxury_multiplier (float): Factor by which the luxury class is taxed more than the non-luxury class

    Methods:
        update_goods(agent, tax_rate):
            Updates the agent's goods and taxes collection
    """
    def __init__(self, tax_steps: int, tax_rate: float, luxury_size: float = 0.9, luxury_multiplier: float = 1.5):
        """
        Constructor for LuxuryTaxer.

        Args:
            tax_steps (int): Number of steps between each tax collection
            tax_rate (float): Tax rate
            luxury_size (float): Fraction of the population that is considered luxury
            luxury_multiplier (float): Factor by which the luxury class is taxed more than the non-luxury class
        """
        super().__init__(tax_steps, tax_rate)
        self.luxury_size = luxury_size
        self.luxury_multiplier = luxury_multiplier

    def collect_taxes(self, agents: dict) -> None:
        """
        Collects taxes from the traders. Applies different tax rates to luxury and non-luxury classes.

        Args:
            agents (dict): Dictionary of agents

        Returns:
            None
        """
        # Get wealth distribution to determine tax rates
        wealths = [agent.wealth for agent in agents]

        if not wealths:
            return  # No wealth to tax

        # Sort wealth
        wealths.sort()

        # Determine a threshold for luxury tax (e.g., top 10% wealth)
        threshold_index = int(len(wealths) * self.luxury_size)
        luxury_threshold = wealths[threshold_index] if threshold_index < len(wealths) else wealths[-1]

        # Collect taxes
        for agent in agents:
            total_wealth = agent.wealth
            if total_wealth > luxury_threshold:
                luxury_tax_rate = self.tax_rate * self.luxury_multiplier  # Higher tax rate for luxury
            else:
                luxury_tax_rate = self.tax_rate

            # Apply tax
            self.update_goods(agent, luxury_tax_rate)

    def update_goods(self, agent: dict, tax_rate: float) -> None:
        """
        Updates the agent's goods and taxes collection. Computes the amount of sugar and spice exceeding metabolism and
        applies tax based on the excess amount.

        Args:
            agent (dict): Agent to update goods and taxes collection
            tax_rate (float): Tax rate

        Returns:
            None
        """
        # Compute the amount of sugar and spice exceeding metabolism
        excess_sugar = max(0, agent.sugar - agent.sugar_metabolism)
        excess_spice = max(0, agent.spice - agent.spice_metabolism)

        # Compute tax based on the excess amount
        sugar_tax = excess_sugar * tax_rate
        spice_tax = excess_spice * tax_rate

        # Update agent's goods and taxes collection
        agent.sugar -= sugar_tax
        agent.spice -= spice_tax
        self.taxes_collection["sugar"] += sugar_tax
        self.taxes_collection["spice"] += spice_tax
