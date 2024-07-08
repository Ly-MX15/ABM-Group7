from mesa import Agent
from numpy import random, sqrt
from .Cell import Cell
from mesa.model import Model
import numpy as np


def get_distance(pos1: list[int], pos2: list[int]) -> int:
    """
    Compute the squared distance between two positions

    Args:
        pos1 (list[int]): Position 1 as a list of two integers [x,y]
        pos2 (list[int]): Position 2 as a list of two integers [x,y]

    Returns:
        int: Squared distance between the two positions

    """
    return (pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2


class Trader(Agent):
    """
    A trader agent that moves around the grid, picks up sugar and spice, trades with other traders, and metabolizes sugar and spice.

    Attributes:
        sugar (int): Sugar resource of the trader
        sugar_metabolism (int): Sugar metabolism rate of the trader
        spice (int): Spice resource of the trader
        spice_metabolism (int): Spice metabolism rate of the trader
        vision (int): Vision range of the trader
        max_age (int): Maximum age of the trader
        age (int): Current age of the trader
        sugar_weight (float): Weight of sugar when moving
        spice_weight (float): Weight of spice when moving
        wealth (float): Wealth of the trader
        price (float): Price of the trader
        has_died (bool): If the trader has died

    Methods:
        step(): Execute one step of the agent
        move(): Move the agent to a cell with the highest welfare
        pick_up(): Pick up sugar and spice from the cell
        metabolize(): Metabolize sugar and spice
        trade(): Trade sugar and spice with other traders
        mrs(): Compute the Marginal Rate of Substitution (MRS)
        improve_welfare(high, low, trade_sugar, trade_spice): Check if welfare is improved after trade
        repopulate(): Repopulate the grid with new traders
        age_increase(): Increment the age of the trader
        welfare(sugar, spice): Compute the welfare of the trader
        update_wealth(): Update the wealth

    """
    def __init__(self, unique_id: int, model: Model, sugar: int, sugar_metabolism: int,
                 spice: int, spice_metabolism: int, vision: int, max_age: int):
        """
        Initialize a trader agent

        Args:
            unique_id (int): Unique identifier of the agent
            model (SugarScape): Model where the agent belongs
            sugar (int): Sugar resource of the trader at the start
            sugar_metabolism (int): Metabolism rate of sugar
            spice (int): Spice resource of the trader at the start
            spice_metabolism (int): Metabolism rate of spice
            vision (int): Vision range of the trader, also affects the movement
            max_age (int): Maximum age of the trader
        """
        super().__init__(unique_id, model)

        # Set initial parameters
        self.sugar = sugar
        self.sugar_metabolism = sugar_metabolism
        self.spice = spice
        self.spice_metabolism = spice_metabolism
        self.vision = vision
        self.max_age = max_age
        self.age = 0

        # Weight for both sugar and spice when moving
        self.sugar_weight = sugar_metabolism / (sugar_metabolism + spice_metabolism)
        self.spice_weight = 1 - self.sugar_weight

        # Set initial wealth
        self.wealth = 0
        self.update_wealth()

        # Initialize trader's price
        self.price = 0

        # If agent has died
        self.has_died = False

    def step(self) -> None:
        """
        Execute one step of the agent

        Returns:
            None
        """
        # Move agent
        self.move()

        # Pick up sugar and spice
        self.pick_up()

        # Update wealth
        self.update_wealth()

        # Trade sugar and spice
        self.trade()

        # Repopulation
        self.repopulate()

        # Metabolize sugar and spice
        self.metabolize()

        # Increment age
        self.age_increase()

        # Check if agent has died
        if self.has_died:
            self.model.remove_agent(self)

    def move(self) -> None:
        """
        Move the agent to a cell with the highest welfare

        Returns:
            None
        """
        # Get neighborhood
        neighbours = [i for i in self.model.grid.get_neighborhood(
            self.pos, moore=False, include_center=False, radius=self.vision
        )]

        # Get cell with most sugar
        max_welfare = -1
        best_position = None
        shortest_distance = float('inf')

        for neighbour in neighbours:
            # Check if another trader is in the cell
            this_cell = self.model.grid.get_cell_list_contents([neighbour])

            # Check if trader within cell
            has_agent = False
            for cells in this_cell:
                if isinstance(cells, Trader):
                    has_agent = True
                    break
            if has_agent:
                continue
            agent = this_cell[0]

            # Compute welfare based on sum of current resources and resources in the cell
            combined_sugar = self.sugar + agent.sugar
            combined_spice = self.spice + agent.spice
            welfare = self.welfare(combined_sugar, combined_spice)
            distance = get_distance(self.pos, neighbour)

            # Update best position
            if (welfare > max_welfare) or (welfare == max_welfare and distance < shortest_distance):
                max_welfare = welfare
                best_position = neighbour
                shortest_distance = distance

        if best_position:
            # Move to the position with the highest welfare
            self.model.grid.move_agent(self, best_position)

    def pick_up(self) -> None:
        """
        Pick up sugar and spice from the cell

        Returns:
            None
        """
        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        # Grab all sugar and spice from cell
        for agent in this_cell:
            if isinstance(agent, Cell):
                self.sugar += agent.sugar
                agent.sugar = 0

                self.spice += agent.spice
                agent.spice = 0

    def metabolize(self) -> None:
        """
        Metabolize sugar and spice

        Returns:
            None
        """
        # Metabolize sugar
        self.sugar -= self.sugar_metabolism

        # Metabolize spice
        self.spice -= self.spice_metabolism

        # Die if sugar is less than 0
        if self.sugar < 0 or self.spice < 0:
            self.model.deaths_starved_step += 1
            self.has_died = True

    def trade(self) -> None:
        """
        Trade sugar and spice with other traders

        Returns:
            None
        """
        # Get neighborhood
        neighbors = self.model.grid.get_neighbors(self.pos, moore=False, include_center=False, radius=1)
        random.shuffle(neighbors)

        # Loop through neighbors
        for neighbors in neighbors:
            # Skip if not a trader
            if not isinstance(neighbors, Trader):
                continue

            # Allows for continuous trading
            while True:
                # Compute MRS
                mrs = self.mrs()
                neighbors_mrs = neighbors.mrs()

                # No more trading if MRS are equal
                if mrs == neighbors_mrs:
                    break

                # Check who has the higher MRS
                if mrs > neighbors_mrs:
                    high = self
                    low = neighbors
                else:
                    high = neighbors
                    low = self

                # Compute the trade price
                trade_price = sqrt(mrs * neighbors_mrs)

                if trade_price == 0:
                    break

                # Check if trade price is greater than 1
                if trade_price > 1:
                    trade_spice = trade_price
                    trade_sugar = 1
                else:
                    trade_spice = 1
                    trade_sugar = 1 / trade_price

                # Update based on MRS
                trade_sugar = min(trade_sugar, low.sugar)
                trade_spice = min(trade_spice, high.spice)

                # No more sugar/spice to trade
                if trade_sugar <= 0 or trade_spice <= 0:
                    break

                # Check if trade improves welfare
                if self.improve_welfare(high, low, trade_sugar, trade_spice):
                    # Trade sugar and spice
                    high.sugar += trade_sugar
                    high.spice -= trade_spice
                    low.sugar -= trade_sugar
                    low.spice += trade_spice

                    # Update table
                    self.model.datacollector.add_table_row("Trades", {
                        'Step': self.model.current_step,
                        'TraderHighMRS_ID': high.unique_id,
                        'TraderLowMRS_ID': low.unique_id,
                        'TradeSugar': trade_sugar,
                        'TradeSpice': trade_spice,
                        'TradePrice': trade_price
                    })

                # No more improvements
                else:
                    break

    def mrs(self) -> float:
        """
        Compute the Marginal Rate of Substitution (MRS)

        Returns:
            float: Marginal Rate of Substitution (MRS)
        """
        return (self.sugar_metabolism * self.spice) / (self.spice_metabolism * self.sugar + 1e-9)

    def improve_welfare(self, high: "Trader", low: "Trader", trade_sugar: float, trade_spice: float) -> bool:
        """
        Check if welfare is improved after trade and if MRS is not crossed

        Args:
            high (Trader): Trader with higher MRS
            low (Trader): Trader with lower MRS
            trade_sugar (float): Amount of sugar to trade
            trade_spice (float): Amount of spice to trade

        Returns:
            bool: If welfare is improved after trade and MRS is not crossed
        """
        # Compute welfare
        high_sugar = high.sugar + trade_sugar
        high_spice = high.spice - trade_spice
        low_sugar = low.sugar - trade_sugar
        low_spice = low.spice + trade_spice

        # Compute welfare
        high_welfare = self.welfare(high_sugar, high_spice)
        low_welfare = self.welfare(low_sugar, low_spice)

        # Check if welfare is improved
        improved = high_welfare > high.wealth and low_welfare > low.wealth

        # Make sure that MRS is not crossed
        not_crossed = high_welfare > low_welfare

        # Check if welfare is improved
        return improved and not_crossed

    def repopulate(self) -> None:
        """
        Repopulate the grid with new traders.

        Returns:
            None
        """
        if (self.sugar >= self.model.repopulate_factor * self.sugar_metabolism
                and self.spice >= self.model.repopulate_factor * self.spice_metabolism):
            self.model.repopulation()
            repopulate_loss_ratio = 0.5
                # Reduce sugar and spice
            self.sugar *= 1 - repopulate_loss_ratio
            self.spice *= 1 - repopulate_loss_ratio

    def age_increase(self):
        """
        Increment the age of the trader, and check if the trader has reached the maximum age.

        Returns:
            None
        """
        # Increment age
        self.age += 1

        # Check if age is greater than max age
        if self.age >= self.max_age:
            self.has_died = True
            self.model.deaths_age_step += 1

    def welfare(self, sugar: float, spice: float) -> float:
        """
        Compute the welfare of the trader based on sugar and spice

        Args:
            sugar (float): Sugar resource of the trader
            spice (float): Spice resource of the trader

        Returns:
            float: Welfare of the trader
        """
        return sugar ** self.sugar_weight * spice ** self.spice_weight

    def update_wealth(self) -> None:
        """
        Update the wealth of the trader based on sugar and spice metabolism rates

        Returns:
            None
        """
        self.wealth = self.sugar / self.sugar_metabolism + self.spice / self.spice_metabolism
        self.model.wealth_step.append(self.wealth)
