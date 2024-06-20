# MESA imports
from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivationByType
from mesa.datacollection import DataCollector

# Agents
from src.Agents.Trader import Trader
from src.Agents.Cell import Cell

# Taxers
from src.Taxers.BaseTaxer import BaseTaxer
from src.Taxers.ProgressiveTaxer import ProgressiveTaxer
from src.Taxers.RegressiveTaxer import RegressiveTaxer
from src.Taxers.LuxuryTaxer import LuxuryTaxer

# Distributers
from src.Distributers.BaseDistributer import BaseDistributer
from src.Distributers.ProgressiveDistributer import ProgressiveDistributer
from src.Distributers.NeedsBasedDistributer import NeedsBasedDistributer
from src.Distributers.RandomDistributer import RandomDistributer

# Distributers


# Statistics
from .statistics import *

# Numpy
import numpy as np
from numpy import random


class SugarScape(Model):
    def __init__(self, height=50, width=50, initial_population=100,
                 metabolism_mean=3, vision_mean=3, max_age_mean=70,
                 tax_scheme="flat", tax_steps=10, tax_rate=0.2,
                 distributer_scheme="flat", distributer_steps=20,
                 repopulate_factor=10, seed_value=42):

        # Initialize model
        super().__init__()

        # Set seed for reproducibility
        random.seed(seed_value)

        # Set parameters
        self.height = height
        self.width = width
        self.initial_population = initial_population
        self.current_step = 0

        # Agent parameters
        self.metabolism_mean = metabolism_mean
        self.vision_mean = vision_mean
        self.max_age_mean = max_age_mean

        # Creating taxer object
        if tax_scheme == "flat":
            self.taxer = BaseTaxer(tax_steps, tax_rate)
        elif tax_scheme == "progressive":
            self.taxer = ProgressiveTaxer(tax_steps, tax_rate)
        elif tax_scheme == "regressive":
            self.taxer = RegressiveTaxer(tax_steps, tax_rate)
        elif tax_scheme == "luxury":
            self.taxer = LuxuryTaxer(tax_steps, tax_rate)
        else:
            raise ValueError("Invalid tax scheme")

        # Creating distributer object
        if distributer_scheme == "flat":
            self.distributer = BaseDistributer(distributer_steps)
        elif distributer_scheme == "progressive":
            self.distributer = ProgressiveDistributer(distributer_steps)
        elif distributer_scheme == "needs":
            self.distributer = NeedsBasedDistributer(distributer_steps)
        elif distributer_scheme == "random":
            self.distributer = RandomDistributer(distributer_steps)
        else:
            raise ValueError("Invalid distributer scheme")

        # Set repopulation factor
        self.repopulate_factor = repopulate_factor

        # Create grid and schedule
        self.schedule = RandomActivationByType(self)
        self.grid = MultiGrid(self.height, self.width, False)

        # Initialize counters and lists used for data collection
        self.deaths_age = []
        self.deaths_starved = []
        self.deaths_age_step = 0
        self.deaths_starved_step = 0
        self.reproduced = []
        self.reproduced_step = 0
        self.averagewealth = []
        self.wealth_step = []

        # Create grid cells
        id = 0
        for content, (x, y) in self.grid.coord_iter():
            # mean = 4
            low_low = 2
            low_high = 4
            high_low = 4
            high_high = 8
            # Define capacities and reproduction rates based on location
            if x < self.width // 2 and y < self.height // 2:  # Left Upper
                capacities = [random.randint(high_low, high_high), random.randint(low_low, low_high)]
            elif x < self.width // 2 and y >= self.height // 2:  # Left Lower
                capacities = [random.randint(high_low, high_high), random.randint(low_low, low_high)]
            elif x >= self.width // 2 and y < self.height // 2:  # Right Upper
                capacities = [random.randint(low_low, low_high), random.randint(high_low, high_high)]
            else:  # Right Lower
                capacities = [random.randint(low_low, low_high), random.randint(high_low, high_high)]

            #capacities = [random.randint(1, 7), random.randint(1, 7)]
            cell = Cell(id, self, capacities)

            # Place cell on grid
            self.grid.place_agent(cell, (x, y))
            self.schedule.add(cell)

            # Increment id
            id += 1

        # Create traders
        self.traders = {}
        self.last_id = id
        for i in range(self.initial_population):
            self.repopulation()


        self.datacollector = DataCollector(
            model_reporters={
                "Trade Price": compute_average_trade_price,
                "Std Price":compute_std_trade_price,
                "Gini": compute_gini,
                "Number of Trades": compute_trade_counts,
                "Deaths by Age": compute_deaths_by_age,
                "Deaths by Hunger": compute_deaths_by_hunger,
                "Average Wealth": compute_average_wealth,
                "Average Vision": compute_average_vision,
                "Average Sugar Metabolism": compute_average_sugar_metabolism,
                "Average Spice Metabolism": compute_average_spice_metabolism,
                "Reproduced": compute_repopulation,
                "Trader Count": lambda m: len(m.traders),
            },
            tables={"Trades": ["Step", "TraderHighMRS_ID", "TraderLowMRS_ID", "TradeSugar", "TradeSpice", "TradePrice"]}
        )

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        self.current_step += 1
        self.deaths_age_step = 0
        self.deaths_starved_step = 0
        self.reproduced_step = 0
        self.wealth_step = []
        self.schedule.step()

        self.deaths_age.append(self.deaths_age_step)
        self.deaths_starved.append(self.deaths_starved_step)
        self.reproduced.append(self.reproduced_step)
        self.averagewealth.append(np.mean(self.wealth_step))

        # Take step for taxer and distributer
        self.taxer.step(self.traders.values())
        self.distributer.step(self.traders.values(), self.taxer)

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
        # Random position
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)

        # Instantiate trader parameters
        sugar, spice = np.random.randint(10, 20, 2)
        sugar_metabolism, spice_metabolism = np.maximum(1, np.random.poisson(self.metabolism_mean, 2))
        vision = max(1, np.random.poisson(self.vision_mean))
        max_age = max(1, np.random.poisson(self.max_age_mean))

        # Update last id
        self.last_id += 1

        # Instantiate trader
        trader = Trader(self.last_id, self, sugar, sugar_metabolism, spice, spice_metabolism, vision, max_age)

        # Place trader on grid
        self.grid.place_agent(trader, (x, y))
        self.schedule.add(trader)

        # Add trader to dictionary
        self.traders[self.last_id] = trader

        # Increment reproduction counter
        self.reproduced_step += 1






