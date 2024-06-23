from .BaseDistributer import BaseDistributer


class ProgressiveDistributer(BaseDistributer):
    def distribute(self, agents, taxer):
        # Get wealth of all agents
        wealths = [agent.wealth for agent in agents]
        wealths.sort()

        # Find the threshold for classes
        low_n = len(wealths) // 3 + 1
        middle_n = 2 * low_n
        if low_n >= len(wealths):
            low_n = 0
        if middle_n >= len(wealths):
            middle_n = len(wealths) - 1
        low_class_threshold = wealths[low_n]
        middle_class_threshold = wealths[middle_n]

        # Find how much each class gets distributed
        low_class = {}
        middle_class = {}
        high_class = {}
        for key in taxer.taxes_collection:
            # Compute how much middle class gets
            middle_class[key] = taxer.taxes_collection[key] / (7 / 3 * low_n + 2 / 3 * (len(wealths) - middle_n))

            # Compute how much low and high class gets
            low_class[key] = middle_class[key] * 4 / 3
            high_class[key] = middle_class[key] * 2 / 3

        # Distribute
        for agent in agents:
            if agent.wealth < low_class_threshold:
                agent.sugar += low_class["sugar"]
                agent.spice += low_class["spice"]

            elif agent.wealth < middle_class_threshold:
                agent.sugar += middle_class["sugar"]
                agent.spice += middle_class["spice"]

            else:
                agent.sugar += high_class["sugar"]
                agent.spice += high_class["spice"]

        # Reset taxes collection
        taxer.reset_tax()