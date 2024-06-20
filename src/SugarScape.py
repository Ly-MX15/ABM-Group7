from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivationByType
from mesa.datacollection import DataCollector
import numpy as np
from numpy import random
from src.Agents.Trader import Trader
from src.Agents.Cell import Cell
from src.Taxers.BaseTaxer import BaseTaxer
from src.Distributers.BaseDistributer import BaseDistributer
from src.Taxers.ProgressiveTaxer import ProgressiveTaxer
from src.Taxers.RegressiveTaxer import RegressiveTaxer
from src.Distributers.ProgressiveDistributer import ProgressiveDistributer
from .statistics import *


class SugarScape(Model):
    def __init__(self, height=50, width=50, initial_population=300, sugar_metabolism_mean=3, spice_metabolism_mean=3,
                 vision_mean=5,max_age_mean=10000,tax_scheme="flat", tax_steps=10, tax_rate=0.2, distributer_scheme="flat", 
                 distributer_steps=50,repopulate_factor=10000, seed_value=42):

        super().__init__()
        # Set parameters
        self.height = height
        self.width = width
        self.initial_population = initial_population
        self.current_step = 0
        self.repopulate_factor = repopulate_factor
        self.sugar_metabolism_mean = sugar_metabolism_mean
        self.spice_metabolism_mean = spice_metabolism_mean
        self.vision_mean = vision_mean
        self.max_age_mean = max_age_mean

        # Set seed for reproducibility
        random.seed(seed_value)

        self.schedule = RandomActivationByType(self)
        self.grid = MultiGrid(self.height, self.width, False)

        # Initialize counters
        self.deaths_age = []
        self.deaths_starved = []
        self.deaths_age_step = 0
        self.deaths_starved_step = 0
        self.reproduced = 0

        # Create taxers and distributers
        if tax_scheme == "flat":
            self.taxer = BaseTaxer(tax_steps, tax_rate)
        elif tax_scheme == "progressive":
            self.taxer = ProgressiveTaxer(tax_steps, tax_rate)
        elif tax_scheme == "regressive":
            self.taxer = RegressiveTaxer(tax_steps, tax_rate)
        else:
            raise ValueError("Invalid tax scheme")

        if distributer_scheme == "flat":
            self.distributer = BaseDistributer(distributer_steps)
        elif distributer_scheme == "progressive":
            self.distributer = ProgressiveDistributer(distributer_steps)
        else:
            raise ValueError("Invalid distributer scheme")

        # Create cells
        id = 0
        high_right = 19
        high_left = 5
        low_right = 3
        low_left = 0
        for content, (x, y) in self.grid.coord_iter():
            # Define capacities and reproduction rates based on location
            if x < self.width // 2 and y < self.height // 2:  # Left Upper
                capacities = [np.random.randint(high_left,high_right), np.random.randint(low_left, low_right)]
            elif x < self.width // 2 and y >= self.height // 2:  # Left Lower
                capacities = [np.random.randint(high_left,high_right), np.random.randint(low_left, low_right)]
            elif x >= self.width // 2 and y < self.height // 2:  # Right Upper
                capacities = [np.random.randint(low_left, low_right), np.random.randint(high_left,high_right)]
            else:  # Right Lower
                capacities = [np.random.randint(low_left, low_right), np.random.randint(high_left,high_right)]

            cell = Cell(id, self, capacities)

            # Place cell on grid
            self.grid.place_agent(cell, (x, y))
            self.schedule.add(cell)

            # Increment id
            id += 1

        # Create traders
        self.traders = {}
        for i in range(self.initial_population):
            # Random position
            x = np.random.randint(0, self.width)
            y = np.random.randint(0, self.height)

            # Instantiate trader using Poisson distribution
            sugar_metabolism = max(1, np.random.poisson(self.sugar_metabolism_mean))
            spice_metabolism = max(1, np.random.poisson(self.spice_metabolism_mean))
            sugar, spice = sugar_metabolism * 10, spice_metabolism * 10
            vision = max(1, np.random.poisson(self.vision_mean))
            max_age = max(70, np.random.poisson(self.max_age_mean))
            trader = Trader(id, self, sugar, sugar_metabolism, spice, spice_metabolism, vision, max_age)

            # Place trader on grid
            self.grid.place_agent(trader, (x, y))
            self.schedule.add(trader)

            # Add trader to dictionary
            self.traders[id] = trader

            # Increment id
            id += 1

        self.datacollector = DataCollector(
            model_reporters={
                "Average Trading Price": compute_average_trade_price,
                "Standard Deviation of Trading Price": compute_std_trade_price,
                "Gini": compute_gini,
                "Living Agents Count": lambda m: len(m.traders),
                "Number of Trades": compute_trade_counts,
                "Deaths by Age": compute_deaths_by_age,
                "Deaths by Hunger": compute_deaths_by_hunger,
                "Average Vision": compute_average_vision,
                "Average Sugar Metabolism": compute_average_sugar_metabolism,
                "Average Spice Metabolism": compute_average_spice_metabolism,
                "Reproduced": lambda m: m.reproduced
            },
            tables={"Trades": ["Step", "TraderHighMRS_ID", "TraderLowMRS_ID", "TradeSugar", "TradeSpice", "TradePrice"]}
        )

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        self.current_step += 1
        self.deaths_age_step = 0
        self.deaths_starved_step = 0
        self.schedule.step()

        self.deaths_age.append(self.deaths_age_step)
        self.deaths_starved.append(self.deaths_starved_step)

        # Get all trader
        traders = [agent for agent in self.schedule.agents if isinstance(agent, Trader)]

        # Take step for taxer and distributer
        self.taxer.step(traders)
        self.distributer.step(traders, self.taxer)

        self.datacollector.collect(self)
        self.running = True if self.schedule.get_agent_count() > 0 else False

    def run_model(self, step_count=200):
        for i in range(step_count):
            self.step()

    def get_trade_log(self):
        return self.datacollector.get_table_dataframe("Trades")

    def remove_agent(self, agent):
        self.grid.remove_agent(agent)
        self.schedule.remove(agent)
        del self.traders[agent.unique_id]

    def repopulation(self):
        # Use Poisson distribution to create set of parameters
        sugar_metabolism = max(1, np.random.poisson(self.sugar_metabolism_mean))
        spice_metabolism = max(1, np.random.poisson(self.spice_metabolism_mean))
        sugar, spice = sugar_metabolism * 5, spice_metabolism * 5
        vision = max(1, np.random.poisson(self.vision_mean))
        max_age = max(70, np.random.poisson(self.max_age_mean))

        # Create new trader
        id = max(self.traders.keys()) + 1
        trader = Trader(id, self, sugar, sugar_metabolism, spice, spice_metabolism, vision, max_age)

        # Random position
        x = np.random.randint(0, self.width)
        y = np.random.randint(0, self.height)

        # Place trader on grid
        self.grid.place_agent(trader, (x, y))
        self.schedule.add(trader)

        # Add trader to dictionary
        self.traders[id] = trader

        # Increment reproduction counter
        self.reproduced += 1