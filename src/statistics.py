import numpy as np
from mesa.model import Model


def compute_std_trade_price(model: Model) -> float:
    """
    Compute the standard deviation of the log of trade prices for the current step.

    Args:
        model (Model): Model model instance.

    Returns:
        float: Standard deviation of the log of trade prices for the current step

    """
    trade_data = model.get_trade_log()
    if len(trade_data) == 0:
        return 0
    current_step_trades = trade_data[trade_data["Step"] == model.current_step]
    if len(current_step_trades) == 0:
        return 0
    log_trade_prices = np.log(current_step_trades["TradePrice"])
    std_log_price = np.std(log_trade_prices)
    return std_log_price


def compute_average_trade_price(model: Model) -> float:
    """
    Compute the average of the log of trade prices for the current step.

    Args:
        model (Model): Model model instance.

    Returns:
        float: Average of the log of trade prices for the current step

    """
    trade_data = model.get_trade_log()
    if len(trade_data) == 0:
        return 0
    current_step_trades = trade_data[trade_data["Step"] == model.current_step]
    if len(current_step_trades) == 0:
        return 0
    log_trade_prices = np.log(current_step_trades["TradePrice"])
    average_price = np.mean(log_trade_prices)
    return average_price


def compute_trade_counts(model: Model) -> int:
    """
    Compute the number of trades that occurred in the current step.

    Args:
        model (Model): Model model instance.

    Returns:
        int: Number of trades that occurred in the current step

    """
    trade_data = model.get_trade_log()
    current_step_trades = trade_data[trade_data["Step"] == model.current_step]
    return len(current_step_trades)


def compute_gini(model: Model) -> float:
    """
    Compute the Gini coefficient for the current step.

    Args:
        model (Model): Model model instance.

    Returns:
        float: Gini coefficient for the current step

    """
    agent_wealths = [agent.sugar / agent.sugar_metabolism + agent.spice / agent.spice_metabolism for agent in
                     model.traders.values()]
    sorted_wealths = sorted(agent_wealths)
    n = len(sorted_wealths)
    if n == 0:
        return 0
    cumulative_sum = sum((i + 1) * wealth for i, wealth in enumerate(sorted_wealths))
    total_wealth = sum(sorted_wealths)
    gini = (2 * cumulative_sum) / (n * total_wealth) - (n + 1) / n

    return gini


def compute_deaths_by_age(model: Model) -> int:
    """
    Return the number of deaths by age for the current step.

    Args:
        model (Model): Model instance.

    Returns:
        int: Number of deaths by age for the current step

    """
    return model.deaths_age[-1] if model.deaths_age else 0


def compute_average_wealth(model: Model) -> float:
    """
    Compute the average wealth of all living Trader agents.

    Args:
        model (Model): Model instance.

    Returns:
        float: Average wealth of all living Trader agents

    """
    return model.averagewealth[-1] if model.averagewealth else 0


def compute_deaths_by_hunger(model: Model) -> int:
    """
    Return the number of deaths by hunger for the current step.

    Args:
        model (Model): Model instance.

    Returns:
        int: Number of deaths by hunger for the current step

    """
    return model.deaths_starved[-1] if model.deaths_starved else 0


def compute_repopulation(model: Model) -> int:
    """
    Return the number of agents that were born in the current step.
    Args:
        model (Model): Model instance.

    Returns:
        int: Number of agents that were born in the current step

    """
    return model.reproduced[-1] if model.reproduced else 0


def compute_average_vision(model: Model) -> float:
    """
    Compute the average vision of all living Trader agents.

    Args:
        model (Model):

    Returns:
        float: Average vision of all living Trader agents

    """
    traders = [agent for agent in model.traders.values()]
    if len(traders) == 0:
        return 0
    average_vision = sum(trader.vision for trader in traders) / len(traders)
    return average_vision


def compute_average_sugar_metabolism(model: Model) -> float:
    """
    Compute the average sugar metabolism of all living Trader agents.

    Args:
        model (Model): Model instance.

    Returns:
        float: Average sugar metabolism of all living Trader

    """
    traders = [agent for agent in model.traders.values()]
    if len(traders) == 0:
        return 0
    average_sugar_metabolism = sum(trader.sugar_metabolism for trader in traders) / len(traders)
    return average_sugar_metabolism


def compute_average_spice_metabolism(model: Model) -> float:
    """
    Compute the average spice metabolism of all living Trader agents.

    Args:
        model (Model): Model instance.

    Returns:
        float: Average spice metabolism of all living Trader agents

    """
    traders = [agent for agent in model.traders.values()]
    if len(traders) == 0:
        return 0
    average_spice_metabolism = sum(trader.spice_metabolism for trader in traders) / len(traders)
    return average_spice_metabolism


def compute_lower_spice_metabolism(model: Model) -> float:
    """
    Compute the average spice metabolism of all living Trader agents in the lower region of the grid.

    Args:
        model (Model): Model instance.

    Returns:
        float: Average spice metabolism of all living Trader agents in the lower region of the grid

    """
    spice_metabolisms = [agent.spice_metabolism for agent in model.traders.values() if
                         agent.pos[1] < 23]
    if len(spice_metabolisms) == 0:
        return 0
    return np.mean(spice_metabolisms)


def compute_lower_sugar_metabolism(model: Model) -> float:
    """
    Compute the average sugar metabolism of all living Trader agents in the lower region of the grid.

    Args:
        model (Model): Model instance.

    Returns:
        float: Average sugar metabolism of all living Trader agents in the lower region of the grid

    """
    sugar_metabolisms = [agent.sugar_metabolism for agent in model.traders.values() if
                         agent.pos[1] < 23]
    if len(sugar_metabolisms) == 0:
        return 0
    return np.mean(sugar_metabolisms)


def compute_middle_spice_metabolism(model: Model) -> float:
    """
    Compute the average spice metabolism of all living Trader agents in the middle region of the grid.

    Args:
        model (Model): Model instance.

    Returns:
        float: Average spice metabolism of all living Trader agents in the middle region of the grid

    """
    spice_metabolisms = [agent.spice_metabolism for agent in model.traders.values() if
                         23 <= agent.pos[1] <= 27]
    if len(spice_metabolisms) == 0:
        return 0
    return np.mean(spice_metabolisms)


def compute_middle_sugar_metabolism(model: Model) -> float:
    """
    Compute the average sugar metabolism of all living Trader agents in the middle region of the grid.

    Args:
        model (Model): Model instance.

    Returns:
        float: Average sugar metabolism of all living Trader agents in the middle region of the grid

    """
    sugar_metabolisms = [agent.sugar_metabolism for agent in model.traders.values() if
                         23 <= agent.pos[1] <= 27]
    if len(sugar_metabolisms) == 0:
        return 0
    return np.mean(sugar_metabolisms)


def compute_upper_spice_metabolism(model: Model) -> float:
    """
    Compute the average spice metabolism of all living Trader agents in the upper region of the grid.

    Args:
        model (Model): Model instance.

    Returns:
        float: Average spice metabolism of all living Trader agents in the upper region of the grid

    """
    spice_metabolisms = [agent.spice_metabolism for agent in model.traders.values() if
                         agent.pos[1] > 27]
    if len(spice_metabolisms) == 0:
        return 0
    return np.mean(spice_metabolisms)


def compute_upper_sugar_metabolism(model: Model) -> float:
    """
    Compute the average sugar metabolism of all living Trader agents in the upper region of the grid.

    Args:
        model (Model): Model instance.

    Returns:
        float: Average sugar metabolism of all living Trader agents in the upper region of the grid

    """
    sugar_metabolisms = [agent.sugar_metabolism for agent in model.traders.values() if
                         agent.pos[1] > 27]
    if len(sugar_metabolisms) == 0:
        return 0
    return np.mean(sugar_metabolisms)


def compute_lower_vision(model: Model) -> float:
    """
    Compute the average vision of all living Trader agents in the lower region of the grid.

    Args:
        model (Model): Model instance.

    Returns:
        float: Average vision of all living Trader agents in the lower region of the grid

    """
    visions = [agent.vision for agent in model.traders.values() if
               agent.pos[1] < 23]
    if len(visions) == 0:
        return 0
    return np.mean(visions)


def compute_middle_vision(model: Model) -> float:
    """
    Compute the average vision of all living Trader agents in the middle region of the grid.

    Args:
        model (Model): Model instance.

    Returns:
        float: Average vision of all living Trader agents in the middle region of the grid

    """
    visions = [agent.vision for agent in model.traders.values() if
               23 <= agent.pos[1] <= 27]
    if len(visions) == 0:
        return 0
    return np.mean(visions)


def compute_upper_vision(model: Model) -> float:
    """
    Compute the average vision of all living Trader agents in the upper region of the grid.

    Args:
        model (Model): Model instance.

    Returns:
        float: Average vision of all living Trader agents in the upper region of the grid

    """
    visions = [agent.vision for agent in model.traders.values() if
               agent.pos[1] > 27]
    if len(visions) == 0:
        return 0
    return np.mean(visions)
