import numpy as np
def compute_std_trade_price(model):
    trade_data = model.get_trade_log()
    if len(trade_data) == 0:
        return 0
    current_step_trades = trade_data[trade_data["Step"] == model.current_step]
    if len(current_step_trades) == 0:
        return 0
    print(current_step_trades)
    log_trade_prices = np.log(current_step_trades["TradePrice"])
    
    std_log_price = log_trade_prices.std()
    print(std_log_price)
    return std_log_price

def compute_average_trade_price(model):
    trade_data = model.get_trade_log()
    if len(trade_data) == 0:
        return 0
    current_step_trades = trade_data[trade_data["Step"] == model.current_step]
    if len(current_step_trades) == 0:
        return 0
    average_price = np.log(current_step_trades["TradePrice"])
    average_price = np.mean()
    return average_price

def compute_trade_counts(model):
    trade_data = model.get_trade_log()
    current_step_trades = trade_data[trade_data["Step"] == model.current_step]
    return len(current_step_trades)





def compute_gini(model):
    agent_wealths = [agent.sugar / agent.sugar_metabolism + agent.spice / agent.spice_metabolism for agent in
                     model.traders.values()]
    sorted_wealths = sorted(agent_wealths)
    # plt.hist(sorted_wealths, bins=10)
    # plt.show()
    n = len(sorted_wealths)
    # print(n)
    if n == 0:
        return 0
    cumulative_sum = sum((i + 1) * wealth for i, wealth in enumerate(sorted_wealths))
    total_wealth = sum(sorted_wealths)
    gini = (2 * cumulative_sum) / (n * total_wealth) - (n + 1) / n

    return gini


def compute_deaths_by_age(model):
    """Return the number of deaths by age for the current step."""
    return model.deaths_age[-1] if model.deaths_age else 0
def compute_average_wealth(model):
    """Return the number of deaths by age for the current step."""
    return model.averagewealth[-1] if model.averagewealth else 0

def compute_deaths_by_hunger(model):
    """Return the number of deaths by hunger for the current step."""
    return model.deaths_starved[-1] if model.deaths_starved else 0

def compute_repopulation(model):
    """Return the number of deaths by hunger for the current step."""
    return model.reproduced[-1] if model.reproduced else 0

def compute_average_vision(model):
    """Compute the average vision of all living Trader agents."""
    traders = [agent for agent in model.traders.values()]
    if len(traders) == 0:
        return 0
    average_vision = sum(trader.vision for trader in traders) / len(traders)
    return average_vision


def compute_average_sugar_metabolism(model):
    """Compute the average sugar metabolism of all living Trader agents."""
    traders = [agent for agent in model.traders.values()]
    if len(traders) == 0:
        return 0
    average_sugar_metabolism = sum(trader.sugar_metabolism for trader in traders) / len(traders)
    return average_sugar_metabolism


def compute_average_spice_metabolism(model):
    """Compute the average spice metabolism of all living Trader agents."""
    traders = [agent for agent in model.traders.values()]
    if len(traders) == 0:
        return 0
    average_spice_metabolism = sum(trader.spice_metabolism for trader in traders) / len(traders)
    return average_spice_metabolism