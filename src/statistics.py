def calculate_gini(model):
    # Calculate Gini coefficient based on traders' wealth
    wealths = [agent.sugar + agent.spice for agent in model.traders.values()]
    wealths.sort()
    n = len(wealths)
    if n == 0:
        return 0
    cumulative_wealth = sum(wealths)
    cumulative_weighted_wealth = sum((i + 1) * wealths[i] for i in range(n))
    gini_coefficient = (2 * cumulative_weighted_wealth) / (n * cumulative_wealth) - (n + 1) / n
    return gini_coefficient


def average_vision(model):
    # Calculate average vision of traders
    visions = [agent.vision for agent in model.traders.values()]
    return sum(visions) / len(visions) if visions else 0


def average_sugar_metabolism(model):
    # Calculate average sugar metabolism of traders
    sugar_metabolisms = [agent.sugar_metabolism for agent in model.traders.values()]
    return sum(sugar_metabolisms) / len(sugar_metabolisms) if sugar_metabolisms else 0


def average_spice_metabolism(model):
    # Calculate average spice metabolism of traders
    spice_metabolisms = [agent.spice_metabolism for agent in model.traders.values()]
    return sum(spice_metabolisms) / len(spice_metabolisms) if spice_metabolisms else 0


def price_stabilization(model):
    # Calculate price stabilization (example: average price over all traders)
    prices = [agent.price for agent in model.traders.values()]
    return sum(prices) / len(prices) if prices else 0
