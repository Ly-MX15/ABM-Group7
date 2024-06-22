from mesa import Agent
from numpy import random, sqrt
from .Cell import Cell
import numpy as np

def get_distance(pos1, pos2):
    return (pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2


class Trader(Agent):
    def __init__(self, unique_id, model, sugar, sugar_metabolism,
                 spice, spice_metabolism, vision, max_age):
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
        self.spice_weight = sugar_metabolism / (sugar_metabolism + spice_metabolism)
        self.sugar_weight = 1 - self.spice_weight

        # Set initial wealth
        self.wealth = 0
        self.update_wealth()

        # Initialize trader's price
        self.price = 0

        # If agent has died
        self.has_died = False

    def step(self):
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

    def move(self):
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

    def pick_up(self):
        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        # Grab all sugar and spice from cell
        for agent in this_cell:
            if isinstance(agent, Cell):
                self.sugar += agent.sugar
                agent.sugar = 0

                self.spice += agent.spice
                agent.spice = 0

    def metabolize(self):
        # Metabolize sugar
        self.sugar -= self.sugar_metabolism

        # Metabolize spice
        self.spice -= self.spice_metabolism

        # Die if sugar is less than 0
        if self.sugar < 0 or self.spice < 0:
            self.model.deaths_starved_step += 1
            self.has_died = True

    def trade(self):
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

    def mrs(self):
        return (self.sugar_metabolism * self.spice) / (self.spice_metabolism * self.sugar + 1e-9)

    def improve_welfare(self, high, low, trade_sugar, trade_spice):
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

    def repopulate(self):
        # Check if trader has enough sugar and spice
        mean_sugar_metabolism = 3.5
        self.spice_metabolism = 3.5
        if (self.sugar >= self.model.repopulate_factor * self.sugar_metabolism
                and self.spice >= self.model.repopulate_factor * self.spice_metabolism):
            probability_of_repopulate =  np.log(min((self.sugar/self.sugar_metabolism),(self.spice/self.spice_metabolism))
                                                /self.model.repopulate_factor)
            print(probability_of_repopulate)
            if random.random() < probability_of_repopulate:
                # Create new trader
                self.model.repopulation()

                repopulate_loss_ratio = 0.3 + (0.5 - 0.3) * np.random.random()
                # Reduce sugar and spice
                self.sugar *= 1 - repopulate_loss_ratio
                self.spice *= 1 - repopulate_loss_ratio

    def age_increase(self):
        # Increment age
        self.age += 1

        # Check if age is greater than max age
        if self.age >= self.max_age:
            self.has_died = True
            self.model.deaths_age_step += 1

    def welfare(self, sugar, spice):
        return sugar ** self.sugar_weight * spice ** self.spice_weight

    def update_wealth(self):
        self.wealth = self.welfare(self.sugar, self.spice)

