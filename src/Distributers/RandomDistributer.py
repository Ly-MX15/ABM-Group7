from .BaseDistributer import BaseDistributer
from numpy import random


class RandomDistributer(BaseDistributer):
    def distribute(self, agents, taxer):
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
