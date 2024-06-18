from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivationByType
from mesa.datacollection import DataCollector
import numpy as np
from .Trader import Trader
from .Cell import Cell

class SugarScape(Model):
    def __init__(self, height=50, width=50, initial_population=100, seed_value=42):
        super().__init__()
        # Set parameters
        self.height = height
        self.width = width
        self.initial_population = initial_population

        # Set seed for reproducibility
        np.random.seed(seed_value)

        self.schedule = RandomActivationByType(self)
        self.grid = MultiGrid(self.height, self.width, False)

        self.datacollector = DataCollector(
            {"Agents": lambda m: m.schedule.get_type_count(Trader)})

        # Create cells
        id = 0
        for content, (x, y) in self.grid.coord_iter():
            # Define capacities and reproduction rates based on location
            if x < self.width // 2 and y < self.height // 2:  # Left Upper
                capacities = [np.random.randint(5, 10), np.random.randint(0, 2)]
            elif x < self.width // 2 and y >= self.height // 2:  # Left Lower
                capacities = [np.random.randint(5, 10), np.random.randint(0, 2)]
            elif x >= self.width // 2 and y < self.height // 2:  # Right Upper
                capacities = [np.random.randint(0, 2), np.random.randint(5, 10)]
            else:  # Right Lower
                capacities = [np.random.randint(0, 2), np.random.randint(5, 10)]
                
            cell = Cell(id, self, capacities)

            # Place cell on grid
            self.grid.place_agent(cell, (x, y))
            self.schedule.add(cell)

            # Increment id
            id += 1

        # Create traders
        for i in range(self.initial_population):
            # Random position
            x = np.random.randint(0, self.width)
            y = np.random.randint(0, self.height)

            # Instantiate trader
            sugar, spice = np.random.randint(1, 10, 2)
            sugar_metabolism, spice_metabolism = np.random.randint(1, 4, 2)
            vision = np.random.randint(1, 4)
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
