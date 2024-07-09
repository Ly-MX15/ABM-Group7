from src.SugarScape import SugarScape
from src.Agents.Cell import Cell
from src.Agents.Trader import Trader
from mesa.visualization import CanvasGrid, ModularServer, TextElement
from mesa.visualization.modules import ChartModule
from mesa.agent import Agent

import math


def agent_portrayal(agent) -> dict:
    """
    This function is used to define how agents are displayed in the visualization.

    Args:
        agent (Agent): The agent to be displayed.

    Returns:
        dict: A dictionary containing the agent's portrayal.

    """
    if agent is None:
        return {}

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

# Charts
labels = ["Trader Count", "Number of Trades", "Trade Price", "Gini", "Deaths by Age", "Deaths by Hunger",
          "Average Vision", "Average Wealth", "Average Sugar Metabolism", "Average Spice Metabolism",
          "Reproduced", "Std Price"]
colors = ["Yellow", "Blue", "Red", "Black", "Green", "Orange", "Purple", "Purple", "Pink", "Brown", "Black", "Red"]
chart_modules = []
for label, color in zip(labels, colors):
    chart_modules.append(ChartModule([{"Label": label, "Color": color}], data_collector_name='datacollector'))

# Add canvas element and legend element to the chart modules
chart_modules.insert(0, canvas_element)
chart_modules.insert(1, legend_element)

server = ModularServer(
    SugarScape,
    chart_modules,
    "Sugarscape Model",
    {
        "initial_population": 100,
        "metabolism_mean": 5.724278133362532,
        "vision_mean": 2.4390112552791834,
        "max_age_mean": 93.55770520865917,
        "repopulate_factor": 10.740787368267775,
        "cell_regeneration": 4.586485207080841,
        "track_scheme": "server"
    }
)

server.port = 8488
server.launch()
