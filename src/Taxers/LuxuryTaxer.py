from .BaseTaxer import BaseTaxer


class LuxuryTaxer(BaseTaxer):
    def __init__(self, tax_steps, tax_rate, luxury_size=0.9, luxury_multiplier=1.5):
        super().__init__(tax_steps, tax_rate)
        self.luxury_size = luxury_size
        self.luxury_multiplier = luxury_multiplier

    def collect_taxes(self, agents):
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

    def update_goods(self, agent, tax_rate):
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
