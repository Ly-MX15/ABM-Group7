from .BaseDistributer import BaseDistributer
from src.Taxers.BaseTaxer import BaseTaxer


class NeedsBasedDistributer(BaseDistributer):
    """
    Distributes resources based on the needs of the agents. This distributer loops through all agents sorted by their
    needs from highest to lowest the trader receives resources till their metabolism is satisfied.
    """
    def distribute(self, agents: dict, taxer: BaseTaxer):
        """
        Distributes resources based on the needs of the agents.

        Args:
            agents (dict): Dictionary of agents
            taxer (BaseTaxer): Taxer object

        Returns:
            None
        """
        # Calculate needs based on the difference between current resources and metabolism
        sugar_needs = []
        spice_needs = []
        for agent in agents:
            sugar_need = max(0, agent.sugar_metabolism - agent.sugar)
            spice_need = max(0, agent.spice_metabolism - agent.spice)
            sugar_needs.append((agent, sugar_need))
            spice_needs.append((agent, spice_need))

        # Sort needs based on sugar and spice
        sugar_needs.sort(key=lambda x: x[1], reverse=True)
        spice_needs.sort(key=lambda x: x[1], reverse=True)

        # Get total sugar and spice collected
        total_sugar = taxer.taxes_collection["sugar"]
        total_spice = taxer.taxes_collection["spice"]

        # Distribute sugar
        for (agent, sugar_need) in sugar_needs:
            if total_sugar <= 0:
                break

            distributed_sugar = min(sugar_need, total_sugar)
            agent.sugar += distributed_sugar
            total_sugar -= distributed_sugar

        # Distribute spice
        for (agent, spice_need) in spice_needs:
            if total_spice <= 0:
                break

            distributed_spice = min(spice_need, total_spice)
            agent.spice += distributed_spice
            total_spice -= distributed_spice
