from src.SugarScape import SugarScape
from src.Agents.Cell import Cell
from src.Agents.Trader import Trader
from mesa.visualization import CanvasGrid, ModularServer, TextElement
from mesa.visualization.modules import ChartModule

import math

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

        # Calculate total resources
        total_resources = agent.sugar + agent.spice

        # Calculate intensity using a logarithmic scale
        if total_resources > 0:
            intensity = min(int(math.log(total_resources + 1) / math.log(10) * 51), 255)
        else:
            intensity = 0

        if agent.sugar > agent.spice:
            # Brighter green gradient for sugar-dominant cells
            portrayal["Color"] = f"rgba(0, 255, 0, {intensity / 255})"
        elif agent.spice > agent.sugar:
            # Brighter blue gradient for spice-dominant cells
            portrayal["Color"] = f"rgba(0, 0, 255, {intensity / 255})"
        elif agent.sugar > 0 and agent.spice > 0:
            # Brighter yellow gradient for balanced cells
            portrayal["Color"] = f"rgba(255, 255, 0, {intensity / 255})"
        else:
            portrayal["Color"] = "black"  # No resources

        portrayal["Layer"] = 0


        # # Set color based on sugar and spice
        # if agent.sugar > agent.spice:
        #     portrayal["Color"] = "green"
        # elif agent.sugar < agent.spice:
        #     portrayal["Color"] = "orange"
        # elif agent.sugar > 0 and agent.spice > 0:
        #     portrayal["Color"] = "rgba(128,210,0, 255)"
        # else:
        #     portrayal["Color"] = "black"

        # portrayal["Layer"] = 0

    return portrayal


legend_html = """
<div style='position: absolute; top: 60px; left: 10px; background: white; padding: 10px; border: 1px solid black;'>
    <h4>Legend</h4>
    <div><span style='display: inline-block; width: 20px; height: 20px; background-color: rgba(255, 0, 0, 1);'></span> Trader</div>
    <div>
        <div style='display: flex; align-items: center;'><span style='display: inline-block; width: 20px; height: 20px; background-color: rgba(0, 255, 0, 0.2);'></span> High Sugar (Green)</div>
        <div style='display: flex; align-items: center;'><span style='display: inline-block; width: 20px; height: 20px; background-color: rgba(0, 255, 0, 0.4);'></span></div>
        <div style='display: flex; align-items: center;'><span style='display: inline-block; width: 20px; height: 20px; background-color: rgba(0, 255, 0, 0.6);'></span></div>
        <div style='display: flex; align-items: center;'><span style='display: inline-block; width: 20px; height: 20px; background-color: rgba(0, 255, 0, 0.8);'></span></div>
        <div style='display: flex; align-items: center;'><span style='display: inline-block; width: 20px; height: 20px; background-color: rgba(0, 255, 0, 1);'></span></div>
    </div>
    <div>
        <div style='display: flex; align-items: center;'><span style='display: inline-block; width: 20px; height: 20px; background-color: rgba(0, 0, 255, 0.2);'></span> High Spice (Blue)</div>
        <div style='display: flex; align-items: center;'><span style='display: inline-block; width: 20px; height: 20px; background-color: rgba(0, 0, 255, 0.4);'></span></div>
        <div style='display: flex; align-items: center;'><span style='display: inline-block; width: 20px; height: 20px; background-color: rgba(0, 0, 255, 0.6);'></span></div>
        <div style='display: flex; align-items: center;'><span style='display: inline-block; width: 20px; height: 20px; background-color: rgba(0, 0, 255, 0.8);'></span></div>
        <div style='display: flex; align-items: center;'><span style='display: inline-block; width: 20px; height: 20px; background-color: rgba(0, 0, 255, 1);'></span></div>
    </div>
    <div>
        <div style='display: flex; align-items: center;'><span style='display: inline-block; width: 20px; height: 20px; background-color: rgba(255, 255, 0, 0.2);'></span> Balanced (Yellow)</div>
        <div style='display: flex; align-items: center;'><span style='display: inline-block; width: 20px; height: 20px; background-color: rgba(255, 255, 0, 0.4);'></span></div>
        <div style='display: flex; align-items: center;'><span style='display: inline-block; width: 20px; height: 20px; background-color: rgba(255, 255, 0, 0.6);'></span></div>
        <div style='display: flex; align-items: center;'><span style='display: inline-block; width: 20px; height: 20px; background-color: rgba(255, 255, 0, 0.8);'></span></div>
        <div style='display: flex; align-items: center;'><span style='display: inline-block; width: 20px; height: 20px; background-color: rgba(255, 255, 0, 1);'></span></div>
    </div>
    <div><span style='display: inline-block; width: 20px; height: 20px; background-color: black;'></span> No Resources</div>
</div>
"""


class LegendElement(TextElement):
    def render(self, model):
        return legend_html


canvas_element = CanvasGrid(agent_portrayal, 50, 50, 500, 500)

legend_element = LegendElement()

trader_count_chart = ChartModule(
    [{"Label": "Trader Count", "Color": "Yellow"}],
    data_collector_name='datacollector'
)

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

Std_trade_price_chart = ChartModule(
    [{"Label": "Std Price", "Color": "Red"}],
    data_collector_name='datacollector'
)

server = ModularServer(
    SugarScape,
    [canvas_element, trader_count_chart, legend_element, Std_trade_price_chart, average_wealth_chart, trader_count_chart, trade_count_chart, average_trade_price_chart, gini_pop,
     deaths_by_age_chart, deaths_by_hunger_chart, average_vision_chart,
     average_sugar_metabolism_chart, average_spice_metabolism_chart, reproduced_chart],
    "Sugarscape Model",
    {
        "height": 50,
        "width": 50,
        "initial_population": 150,
        "metabolism_mean": 5,
        "vision_mean": 2,
        "max_age_mean": 70,
        "tax_scheme": "progressive",
        "tax_steps": 20,
        "tax_rate": 0,
        "distributer_scheme": "progressive",
        "distributer_steps": 20,
        "repopulate_factor": 10,
        "map_scheme": "split",
    }
)

server.port = 8488
server.launch()

