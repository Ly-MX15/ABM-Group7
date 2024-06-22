from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivationByType
from mesa.datacollection import DataCollector
from numpy import random
from src.Agents.Trader import Trader
from src.Agents.Cell import Cell
from src.Taxers.BaseTaxer import BaseTaxer
from src.Distributers.BaseDistributer import BaseDistributer
from src.Taxers.ProgressiveTaxer import ProgressiveTaxer
from src.Distributers.ProgressiveDistributer import ProgressiveDistributer
from .statistics import *
import numpy as np


class SugarScape(Model):
    def __init__(self, height=50, width=50, initial_population=100,
                 tax_scheme="flat", tax_steps=10, tax_rate=0.1, distributer_scheme="flat", distributer_steps=20,
                 repopulate_factor=10, seed_value=42):
        super().__init__()
        # Set parameters
        self.height = height
        self.width = width
        self.initial_population = initial_population
        self.current_step = 0
        self.repopulate_factor = repopulate_factor

        # Set seed for reproducibility
        random.seed(seed_value)

        self.schedule = RandomActivationByType(self)
        self.grid = MultiGrid(self.height, self.width, False)

        # Initialize counters
        self.deaths_age = []
        self.deaths_starved = []
        self.deaths_age_step = 0
        self.deaths_starved_step = 0
        self.reproduced = []
        self.reproduced_step = 0

        # Create taxers and distributers
        if tax_scheme == "flat":
            self.taxer = BaseTaxer(tax_steps, tax_rate)
        elif tax_scheme == "progressive":
            self.taxer = ProgressiveTaxer(tax_steps, tax_rate)
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
        for content, (x, y) in self.grid.coord_iter():
            # Define capacities and reproduction rates based on location
            if x < self.width // 2 and y < self.height // 2:  # Left Upper
                capacities = [random.randint(5, 10), random.randint(1, 2)]
            elif x < self.width // 2 and y >= self.height // 2:  # Left Lower
                capacities = [random.randint(5, 10), random.randint(1, 2)]
            elif x >= self.width // 2 and y < self.height // 2:  # Right Upper
                capacities = [random.randint(1, 2), random.randint(5, 10)]
            else:  # Right Lower
                capacities = [random.randint(1, 2), random.randint(5, 10)]

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
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)

            # Instantiate trader
            sugar, spice = random.randint(10, 20, 2)
            sugar_metabolism, spice_metabolism = random.randint(1, 6, 2)
            vision = random.randint(1, 4)
            max_age = random.randint(70, 100)
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
                "Trade Price": compute_average_trade_price,
                "Gini": compute_gini,
                "Number of Trades": compute_trade_counts,
                "Deaths by Age": compute_deaths_by_age,
                "Deaths by Hunger": compute_deaths_by_hunger,
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
        self.schedule.step()

        self.deaths_age.append(self.deaths_age_step)
        self.deaths_starved.append(self.deaths_starved_step)
        self.reproduced.append(self.reproduced_step)
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
        # Random position
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)

        # Instantiate trader
        sugar, spice = np.random.randint(10, 20, 2)
        sugar_metabolism, spice_metabolism = np.random.randint(1, 6, 2)
        vision = random.randint(1, 4)
        max_age = random.randint(70, 100)
        id = max(self.traders.keys()) + 1
        trader = Trader(id, self, sugar, sugar_metabolism, spice, spice_metabolism, vision, max_age)

        # Place trader on grid
        self.grid.place_agent(trader, (x, y))
        self.schedule.add(trader)

        # Add trader to dictionary
        self.traders[id] = trader
        """
        # Get distribution of metabolism, vision and max age
        sugar_metabolism = {i: 0 for i in range(1, 4)}
        spice_metabolism = {i: 0 for i in range(1, 4)}
        vision = {i: 0 for i in range(1, 4)}
        max_age = {i: 0 for i in range(70, 100)}

        # Incrementing each level within distribution
        for trader in self.traders.values():
            sugar_metabolism[trader.sugar_metabolism] += 1
            spice_metabolism[trader.spice_metabolism] += 1
            vision[trader.vision] += 1
            max_age[trader.max_age] += 1

        # Normalize distribution
        n = len(self.traders)
        sugar_metabolism = {k: v/n for k, v in sugar_metabolism.items()}
        spice_metabolism = {k: v/n for k, v in spice_metabolism.items()}
        vision = {k: v/n for k, v in vision.items()}
        max_age = {k: v/n for k, v in max_age.items()}

        # Use distributions to create set of parameters
        sugar_metabolism = random.choice(list(sugar_metabolism.keys()), p=list(sugar_metabolism.values()))
        spice_metabolism = random.choice(list(spice_metabolism.keys()), p=list(spice_metabolism.values()))
        vision = random.choice(list(vision.keys()), p=list(vision.values()))
        max_age = random.choice(list(max_age.keys()), p=list(max_age.values()))

        # Create new trader
        id = max(self.traders.keys()) + 1
        sugar, spice = np.random.randint(1, 10, 2)
        trader = Trader(id, self, sugar, sugar_metabolism, spice, spice_metabolism, vision, max_age)

        # Random position
        x = random.randint(0, self.width)
        y = random.randint(0, self.height)

        # Place trader on grid
        self.grid.place_agent(trader, (x, y))
        self.schedule.add(trader)

        # Add trader to dictionary
        self.traders[id] = trader
        """
        # Increment reproduction counter
        self.reproduced_step += 1






