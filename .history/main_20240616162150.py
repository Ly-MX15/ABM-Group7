from src.SugarScape import SugarScape
from src.Cell import Cell
from src.Trader import Trader
from mesa.visualization import CanvasGrid, ModularServer
from mesa.visualization.modules import ChartModule

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

# Add new charts for the additional data
death_chart = ChartModule(
    [{"Label": "Deaths", "Color": "Black"}],
    data_collector_name='datacollector'
)

gini_chart = ChartModule(
    [{"Label": "GiniCoefficient", "Color": "Black"}],
    data_collector_name='datacollector'
)

vision_chart = ChartModule(
    [{"Label": "AverageVision", "Color": "Black"}],
    data_collector_name='datacollector'
)

metabolism_chart = ChartModule(
    [
        {"Label": "AverageSugarMetabolism", "Color": "Blue"},
        {"Label": "AverageSpiceMetabolism", "Color": "Red"}
    ],
    data_collector_name='datacollector'
)

price_chart = ChartModule(
    [{"Label": "PriceStabilization", "Color": "Black"}],
    data_collector_name='datacollector'
)

server = ModularServer(
    SugarScape,
    [canvas_element, death_chart, gini_chart, vision_chart, metabolism_chart, price_chart],
    "Sugarscape Model",
    {"height": 50, "width": 50, "initial_population": 100},
)
server.launch()

# Run the model for 300 steps
model = SugarScape(height=50, width=50, initial_population=100)
for i in range(300):
    model.step()

# Collect data
data = model.datacollector.get_model_vars_dataframe()

# Plot data
def plot_and_save(data, y_label, title, filename):
    plt.figure()
    data.plot()
    plt.ylabel(y_label)
    plt.title(title)
    plt.savefig(filename)
    plt.close()

plot_and_save(data[['Deaths']], 'Number of Deaths', 'Deaths over Time', 'deaths_over_time.png')
plot_and_save(data[['GiniCoefficient']], 'Gini Coefficient', 'Gini Coefficient over Time', 'gini_coefficient_over_time.png')
plot_and_save(data[['AverageVision']], 'Average Vision', 'Average Vision over Time', 'average_vision_over_time.png')
plot_and_save(data[['AverageSugarMetabolism', 'AverageSpiceMetabolism']], 'Average Metabolism', 'Average Metabolism over Time', 'average_metabolism_over_time.png')
plot_and_save(data[['PriceStabilization']], 'Price Stabilization', 'Price Stabilization over Time', 'price_stabilization_over_time.png')