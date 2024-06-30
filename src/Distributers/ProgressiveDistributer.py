from .BaseDistributer import BaseDistributer


class ProgressiveDistributer(BaseDistributer):
    def distribute(self, agents, taxer):
        # Get wealth of all agents
        wealth = {
            'sugar': [agent.sugar / agent.sugar_metabolism for agent in agents],
            'spice': [agent.spice / agent.spice_metabolism for agent in agents]
        }

        # Get class thresholds
        low_threshold = {}
        middle_threshold = {}
        low_n = {}
        middle_n = {}
        for key in wealth:
            # Sort wealth
            wealth[key].sort()

            # Find class thresholds
            low_threshold[key], middle_threshold[key], low_n[key], middle_n[key] = class_thresholds(wealth[key])


        # Find how much each class gets distributed
        low_class = {}
        middle_class = {}
        high_class = {}
        for key in taxer.taxes_collection:
            # Compute how much each class in total gets
            middle_class[key] = taxer.taxes_collection[key] / 3
            low_class[key] = middle_class[key] * 4 / 3
            high_class[key] = middle_class[key] * 2 / 3

            # Compute individual class distribution
            low_class[key] /= low_n[key]
            middle_class[key] /= (middle_n[key] - low_n[key])
            high_class[key] /= len(wealth[key]) - middle_n[key]

        # Distribute taxes
        for agent in agents:
            # Sugar distribution
            if agent.sugar / agent.sugar_metabolism < low_threshold["sugar"]:
                agent.sugar += low_class["sugar"]
            elif agent.sugar / agent.sugar_metabolism < middle_threshold["sugar"]:
                agent.sugar += middle_class["sugar"]
            else:
                agent.sugar += high_class["sugar"]

            # Spice distribution
            if agent.spice / agent.spice_metabolism < low_threshold["spice"]:
                agent.spice += low_class["spice"]
            elif agent.spice / agent.spice_metabolism < middle_threshold["spice"]:
                agent.spice += middle_class["spice"]
            else:
                agent.spice += high_class["spice"]

        # Reset taxes collection
        taxer.reset_tax()

def class_thresholds(resource):
    # Find the threshold for classes
    low_n = len(resource) // 3 + 1
    middle_n = 2 * low_n
    if low_n >= len(resource):
        low_n = 0
    if middle_n >= len(resource):
        middle_n = len(resource) - 1

    return resource[low_n], resource[middle_n], low_n, middle_n

