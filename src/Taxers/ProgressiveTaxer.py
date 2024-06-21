from .BaseTaxer import BaseTaxer


class ProgressiveTaxer(BaseTaxer):
    def collect_taxes(self, agents):
        # Get wealth distribution to determine tax rates
        wealths = [agent.wealth for agent in agents]

        # Sort wealth
        wealths.sort()

        # Find 33rd and 66th percentiles
        low_class = wealths[len(wealths) // 3]
        middle_class = wealths[2 * len(wealths) // 3]

        # Collect taxes
        for agent in agents:
            if agent.wealth < low_class:
                self.update_goods(agent, self.tax_rate * 0.66)
            elif agent.wealth < middle_class:
                self.update_goods(agent, self.tax_rate)
            else:
                self.update_goods(agent, self.tax_rate * 1.33)

    def update_goods(self, agent, tax_rate):
        # Compute excessive sugar and spice
        excessive_sugar = max(0, agent.sugar - agent.sugar_metabolism)
        excessive_spice = max(0, agent.spice - agent.spice_metabolism)

        # Compute tax amount
        sugar_tax = int(excessive_sugar * tax_rate)
        spice_tax = int(excessive_spice * tax_rate)

        self.taxes_collection["sugar"] += sugar_tax
        self.taxes_collection["spice"] += spice_tax
        agent.sugar -= sugar_tax
        agent.spice -= spice_tax
