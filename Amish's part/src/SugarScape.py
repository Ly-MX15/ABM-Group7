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

        self.datacollector = DataCollector(
            {"Agents": lambda m: m.schedule.get_type_count(Trader)})

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