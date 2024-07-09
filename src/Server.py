from typing import List
from mesa_viz_tornado.modules import ChartModule
from src.SugarScape import SugarScape
from src.Agents.Cell import Cell
from src.Agents.Trader import Trader
from mesa.visualization import CanvasGrid, ModularServer, TextElement
from mesa.visualization.modules import ChartModule
from mesa.agent import Agent
import math


def create_legend() -> TextElement:
    """
    This function creates a legend for the visualization.

    Returns:
        TextElement: The legend element.

    """
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

    return LegendElement()


def agent_portrayal(agent: Trader) -> dict:
    """
    This function is used to define how agents are displayed in the visualization.

    Args:
        agent (Trader): The agent to be displayed.

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


def create_canvas(width, height) -> CanvasGrid:
    """
    This function creates the canvas grid for the visualization.

    Returns:
        CanvasGrid: The canvas grid element.

    """
    return CanvasGrid(agent_portrayal, width, height, 500, 500)


def create_chart_module() -> list:
    """
    This function creates a chart module for the visualization.

    Returns:
        list: A list containing the chart modules for the visualization.

    """

    # Labels that are being used in the visualization
    labels = ["Trader Count", "Number of Trades", "Trade Price", "Gini", "Deaths by Age", "Deaths by Hunger",
              "Average Vision", "Average Wealth", "Average Sugar Metabolism", "Average Spice Metabolism",
              "Reproduced", "Std Price"]

    # Color for each label
    colors = ["Yellow", "Blue", "Red", "Black", "Green", "Orange", "Purple", "Purple", "Pink", "Brown", "Black", "Red"]

    # Add the chart module to the list of chart modules
    chart_modules = []
    for label, color in zip(labels, colors):
        chart_modules.append(ChartModule([{"Label": label, "Color": color}], data_collector_name='datacollector'))

    return chart_modules


class Server:
    def __init__(self, width: int = 50, height: int = 50, initial_population: int = 300, metabolism_mean: float = 5,
                 vision_mean: float = 3, max_age_mean: float = 85, tax_scheme: str = "progressive", tax_steps: int = 20,
                 tax_rate: float = 0, distributer_scheme: str = "progressive", distributer_steps: int = 20,
                 repopulate_factor: float = 10, map_scheme: str = "uniform", cell_regeneration: float = 1):
        """
        This function initializes the server for the visualization.

        Args:
            width (int): The width of the grid.
            height (int): The height of the grid.
            initial_population (int): The number of traders to start with.
            metabolism_mean (float): The mean metabolism for traders.
            vision_mean (float): The mean vision for traders.
            max_age_mean (float): The mean maximum age for traders.
            tax_scheme (str): The tax scheme to use. Options are "flat", "progressive", "regressive", and "luxury".
            tax_steps (int): The number of tax steps to use.
            tax_rate (float): The tax rate to apply to all trades.
            distributer_scheme (str): The distributer scheme to use. Options are "flat", "progressive", "needs", and "random".
            distributer_steps (int): The number of distributer steps to use.
            repopulate_factor (float): The factor used to determine when to repopulate traders.
            map_scheme (str): The scheme to use for generating the map. Options are "uniform" and "random".
            cell_regeneration (float): The amount of sugar to regenerate in each cell.
        """
        # Create legend
        legend = create_legend()

        # Create canvas
        canvas = create_canvas(width, height)

        # Create chart module
        chart = create_chart_module()

        # Add canvas element and legend element to the chart modules
        chart.insert(0, canvas)
        chart.insert(1, legend)

        # Create server
        self.server = ModularServer(
            SugarScape,
            chart,
            "Sugarscape Model",
            {
                "width": width,
                "height": height,
                "initial_population": initial_population,
                "metabolism_mean": metabolism_mean,
                "vision_mean": vision_mean,
                "max_age_mean": max_age_mean,
                "tax_scheme": tax_scheme,
                "tax_steps": tax_steps,
                "tax_rate": tax_rate,
                "distributer_scheme": distributer_scheme,
                "distributer_steps": distributer_steps,
                "repopulate_factor": repopulate_factor,
                "map_scheme": map_scheme,
                "cell_regeneration": cell_regeneration,
                "track_scheme": "server"
            }
        )

    def launch(self, port: int = 8488) -> None:
        """
        This function launches the server for the visualization.

        Args:
            port (int): The port to launch the server on.

        Returns:
            None
        """
        self.server.port = port
        self.server.launch()
