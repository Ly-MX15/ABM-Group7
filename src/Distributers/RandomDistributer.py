from .BaseDistributer import BaseDistributer
from numpy import random
from src.Taxers.BaseTaxer import BaseTaxer


class RandomDistributer(BaseDistributer):
    """
    Distributes resources randomly to agents. The resources are distributed based on a random selection of agents.
    The selected agent will receive one unit, and this is repeated until all resources are distributed.
    """
    def distribute(self, agents: dict, taxer: BaseTaxer) -> None:
        """
        Distribute according to random scheme.

        Args:
            agents (dict): Dictionary of agents
            taxer (BaseTaxer): Taxer object

        Returns:
            None

        """
        # Convert agents to a list
        agents_list = list(agents)

        total_sugar = taxer.taxes_collection["sugar"]
        total_spice = taxer.taxes_collection["spice"]

        while total_sugar > 0:
            agent = random.choice(agents_list)
            agent.sugar += 1
            total_sugar -= 1

        while total_spice > 0:
            agent = random.choice(agents_list)
            agent.spice += 1
            total_spice -= 1

        # Reset taxes collection
        taxer.reset_tax()
