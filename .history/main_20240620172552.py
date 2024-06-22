from src.SugarScape import SugarScape
from src.Agents.Cell import Cell
from src.Agents.Trader import Trader
from mesa.visualization import CanvasGrid, ModularServer
from mesa.visualization.modules import ChartModule


def agent_portrayal(agent):
    if agent is None:
        return

    portrayal = {"Filled": "true",
                 "r": 0.5,
                 "w": 1,
                 "h": 1}

    if type(agent) is Trader:
        portrayal["Color"] = "red"
        portrayal["Layer"] = 1
        portrayal["Shape"] = "circle"
    elif type(agent) is Cell:
        portrayal["Shape"] = "rect"
        portrayal["Color"] = "green" if agent.sugar > 0 and agent.spice > 0 else "black"
        portrayal["Layer"] = 0

    return portrayal


canvas_element = CanvasGrid(agent_portrayal, 50, 50, 500, 500)

trader_count_chart = ChartModule(
    [{"Label": "Trader Count", "Color": "Yellow"}],
    data_collector_name='datacollector'
)

trade_count_chart = ChartModule(
    [{"Label": "Number of Trades", "Color": "Blue"}],
    data_collector_name='datacollector'
)

average_trade_price_chart = ChartModule(
    [{"Label": "Trade Price", "Color": "Red"}],
    data_collector_name='datacollector'
)

gini_pop = ChartModule(
    [{"Label": "Gini", "Color": "Black"}],
    data_collector_name='datacollector'
)

deaths_by_age_chart = ChartModule(
    [{"Label": "Deaths by Age", "Color": "Green"}],
    data_collector_name='datacollector'
)

deaths_by_hunger_chart = ChartModule(
    [{"Label": "Deaths by Hunger", "Color": "Orange"}],
    data_collector_name='datacollector'
)

average_vision_chart = ChartModule(
    [{"Label": "Average Vision", "Color": "Purple"}],
    data_collector_name='datacollector'
)

average_wealth_chart = ChartModule(
    [{"Label": "Average Wealth", "Color": "Purple"}],
    data_collector_name='datacollector'
)


average_sugar_metabolism_chart = ChartModule(
    [{"Label": "Average Sugar Metabolism", "Color": "Pink"}],
    data_collector_name='datacollector'
)

average_spice_metabolism_chart = ChartModule(
    [{"Label": "Average Spice Metabolism", "Color": "Brown"}],
    data_collector_name='datacollector'
)

reproduced_chart = ChartModule(
    [{"Label": "Reproduced", "Color": "Black"}],
    data_collector_name='datacollector'
)

Std_trade_price_chart = ChartModule(
    [{"Label": "Std Price", "Color": "Red"}],
    data_collector_name='datacollector'
)

server = ModularServer(
    SugarScape,
    [canvas_element, Std_trade_price_chart, average_wealth_chart, trader_count_chart, trade_count_chart, average_trade_price_chart, gini_pop,
     deaths_by_age_chart, deaths_by_hunger_chart, average_vision_chart,
     average_sugar_metabolism_chart, average_spice_metabolism_chart, reproduced_chart],
    "Sugarscape Model",
    {"height": 50, "width": 50, 
     "initial_population": 300,
     'tax_scheme':"flat", 
     'distributer_scheme':"flat",
     'tax_steps':5,
     'tax_rate':0.2}
)

server.port = 8469
server.launch()

