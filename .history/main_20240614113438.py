from src.SugarScape import SugarScape
from src.Cell import Cell
from src.Trader import Trader
from mesa.visualization import CanvasGrid, ModularServer


def agent_portrayal(agent):
    if agent is None:
        return

    portrayal = {"Filled": "true", "r": 0.5, "w": 1, "h": 1}

    if type(agent) is Trader:
        portrayal["Color"] = "red"
        portrayal["Layer"] = 1
        portrayal["Shape"] = "circle"
    elif type(agent) is Cell:
        portrayal["Shape"] = "rect"
        portrayal["Layer"] = 0

        # Selecting Color
        if agent.sugar == 0 and agent.spice == 0:
            portrayal["Color"] = "black"
        else:
            portrayal["Color"] = "orange" if agent.sugar > agent.spice else "green"

    return portrayal


canvas_element = CanvasGrid(agent_portrayal, 50, 50, 500, 500)

server = ModularServer(
    SugarScape,
    [canvas_element],
    "Sugarscape Model",
    {"height": 50, "width": 50, "initial_population": 100},
)
server.launch()
