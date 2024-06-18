from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivationByType
from mesa.datacollection import DataCollector
from numpy import random
from .Trader import Trader
from .Cell import Cell

class SugarScape(Model):
    def __init__(self, height=50, width=50, initial_population=100):
        super().__init__()
        # Set parameters
        self.height = height
        self.width = width
        self.initial_population = initial_population

        self.schedule = RandomActivationByType(self)
        self.grid = MultiGrid(self.height, self.width, False)

        # Initialize counters
        self.deaths = 0

        self.datacollector = DataCollector(
            {
                "Agents": lambda m: m.schedule.get_type_count(Trader),
                "Deaths": lambda m: m.deaths,
                "GiniCoefficient": lambda m: calculate_gini(m),
                "AverageVision": lambda m: average_vision(m),
                "AverageSugarMetabolism": lambda m: average_sugar_metabolism(m),
                "AverageSpiceMetabolism": lambda m: average_spice_metabolism(m),
                "PriceStabilization": lambda m: price_stabilization(m)
            }
        )

        # Create cells
        id = 0
        for content, (x, y) in self.grid.coord_iter():
            # Instantiate cell
            capacities = random.randint(1, 10, 2)
            cell = Cell(id, self, capacities)

            # Place cell on grid
            self.grid.place_agent(cell, (x, y))
            self.schedule.add(cell)

            # Increment id
            id += 1

        # Create traders
        for i in range(self.initial_population):
            # Random position
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)

            # Instantiate trader
            sugar, spice = random.randint(1, 10, 2)
            sugar_metabolism, spice_metabolism = random.randint(1, 4, 2)
            vision = random.randint(1, 4)
            trader = Trader(id, self, sugar, sugar_metabolism, spice, spice_metabolism, vision)

            # Place trader on grid
            self.grid.place_agent(trader, (x, y))
            self.schedule.add(trader)

            # Increment id
            id += 1

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)
        self.running = True if self.schedule.get_agent_count() > 0 else False

    def run_model(self, step_count=200):
        for i in range(step_count):
            self.step()

def calculate_gini(model):
    # Calculate Gini coefficient based on traders' wealth
    wealths = [agent.sugar + agent.spice for agent in model.schedule.agents if isinstance(agent, Trader)]
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
    visions = [agent.vision for agent in model.schedule.agents if isinstance(agent, Trader)]
    return sum(visions) / len(visions) if visions else 0

def average_sugar_metabolism(model):
    # Calculate average sugar metabolism of traders
    sugar_metabolisms = [agent.sugar_metabolism for agent in model.schedule.agents if isinstance(agent, Trader)]
    return sum(sugar_metabolisms) / len(sugar_metabolisms) if sugar_metabolisms else 0

def average_spice_metabolism(model):
    # Calculate average spice metabolism of traders
    spice_metabolisms = [agent.spice_metabolism for agent in model.schedule.agents if isinstance(agent, Trader)]
    return sum(spice_metabolisms) / len(spice_metabolisms) if spice_metabolisms else 0

def price_stabilization(model):
    # Calculate price stabilization (example: average price over all traders)
    prices = [agent.price for agent in model.schedule.agents if isinstance(agent, Trader)]
    return sum(prices) / len(prices) if prices else 0
