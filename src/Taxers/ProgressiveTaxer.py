from .BaseTaxer import BaseTaxer
from src.Agents.Trader import Trader


class ProgressiveTaxer(BaseTaxer):
    """
    Collects taxes from the traders using a progressive tax system. This taxer collects taxes from the traders using a
    class system. The class of the trader is determined by their wealth. The following classes are defined:
        - Low class: 0 - 33rd percentile
        - Middle class: 33rd - 66th percentile
        - High class: 66th - 100th percentile
    The tax rates for each class are:
        - Low class: tax_rate * 0.66
        - Middle class: tax_rate
        - High class: tax_rate * 1.33
    """
    def collect_taxes(self, agents: dict) -> None:
        """
        Collects taxes from the traders using a progressive tax system.

        Args:
            agents (dict): Dictionary of agents

        Returns:
            None

        """
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

    def update_goods(self, agent: Trader, tax_rate: float) -> None:
        """
        Updates the agent's goods and taxes collection.

        Args:
            agent (Trader): Agent
            tax_rate (float): Tax rate

        Returns:
            None

        """
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
