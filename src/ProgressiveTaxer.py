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
        self.taxes_collection["sugar"] += int(agent.sugar * tax_rate)
        self.taxes_collection["spice"] += int(agent.spice * tax_rate)
        agent.sugar -= int(agent.sugar * tax_rate)
        agent.spice -= int(agent.spice * tax_rate)
