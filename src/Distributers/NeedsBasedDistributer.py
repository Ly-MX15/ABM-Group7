from .BaseDistributer import BaseDistributer


class NeedsBasedDistributer(BaseDistributer):
    def distribute(self, agents, taxer):
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

        # Reset taxes collection
        taxer.reset_tax()