# MESA imports
from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivationByType
from mesa.datacollection import DataCollector

# Agents
from src.Agents.Trader import Trader

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

# GridCreator
from src.GridCreator import GridCreator

# Statistics
from .statistics import *

# Numpy
import numpy as np
from numpy import random


class SugarScape(Model):
    def __init__(self, height=50, width=50, initial_population=300,
                 metabolism_mean=5, vision_mean=3, max_age_mean=85,
                 tax_scheme="progressive", tax_steps=20, tax_rate=0,
                 distributer_scheme="progressive", distributer_steps=20,
                 repopulate_factor=10, map_scheme="uniform", cell_regeneration=1,
                 seed_value=None):

        # Initialize model
        super().__init__()

        # Set seed for reproducibility
        if seed_value:
            random.seed(seed_value)

        # Set parameters
        self.height = height
        self.width = width
        self.initial_population = initial_population
        self.current_step = 0
        self.tax_rate = tax_rate

        # Agent parameters
        self.metabolism_mean = metabolism_mean
        self.vision_mean = vision_mean
        self.max_age_mean = max_age_mean
        self.map_scheme = map_scheme
        self.cell_regeneration = cell_regeneration

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
        self.last_id = 0
        grid_creator = GridCreator(self, map_scheme, cell_regeneration=self.cell_regeneration)
        grid_creator.create_grid()

        # Create traders
        self.traders = {}
        for i in range(self.initial_population):
            self.repopulation()

        self.datacollector = DataCollector(
            model_reporters={
                # "Trade Price": compute_average_trade_price,
                # "Std Price": compute_std_trade_price,
                "Gini": compute_gini,
                # "Number of Trades": compute_trade_counts,
                # "Deaths by Age": compute_deaths_by_age,
                # "Deaths by Hunger": compute_deaths_by_hunger,
                # "Average Wealth": compute_average_wealth,
                # "Average Vision": compute_average_vision,
                # "Average Sugar Metabolism": compute_average_sugar_metabolism,
                # "Average Spice Metabolism": compute_average_spice_metabolism,
                # "Reproduced": compute_repopulation,
                "Trader Count": lambda m: len(m.traders),
            },
            tables={"Trades": ["Step", "TraderHighMRS_ID", "TraderLowMRS_ID", "TradeSugar", "TradeSpice", "TradePrice"]}
        )

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        # Tracking for current step
        self.current_step += 1
        self.deaths_age_step = 0
        self.deaths_starved_step = 0
        self.reproduced_step = 0
        self.wealth_step = []
        self.reproduced_step = 0
        self.wealth_step = []

        # Update cells and traders
        self.schedule.step()

        # Add to lists
        self.deaths_age.append(self.deaths_age_step)
        self.deaths_starved.append(self.deaths_starved_step)
        self.reproduced.append(self.reproduced_step)
        self.averagewealth.append(np.mean(self.wealth_step))

        # Take step for taxer and distributer
        if self.tax_rate > 0:
            self.taxer.step(self.traders.values())
            self.distributer.step(self.traders.values(), self.taxer)

        # Collect data
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


    def tracker(self, option='server'):