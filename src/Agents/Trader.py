from mesa import Agent
from numpy import random
from .Cell import Cell


def get_distance(pos1, pos2):
    return (pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2


class Trader(Agent):
    def __init__(self, unique_id, model, sugar, sugar_metabolism,
                 spice, spice_metabolism, vision):
        super().__init__(unique_id, model)

        # Set initial parameters
        self.sugar = sugar
        self.sugar_metabolism = sugar_metabolism
        self.spice = spice
        self.spice_metabolism = spice_metabolism
        self.vision = vision

        # Weight for both sugar and spice when moving
        self.spice_weight = sugar_metabolism / (sugar_metabolism + spice_metabolism)
        self.sugar_weight = 1 - self.spice_weight

        # Set initial wealth
        self.wealth = 0
        self.update_wealth()

        # Initialize trader's price
        self.price = 0

    def step(self):
        # Move agent
        self.move()

        # Pick up sugar and spice
        self.pick_up()

        # Update wealth
        self.update_wealth()

        # Trade sugar and spice
        self.trade()

        # Metabolize sugar and spice
        self.metabolize()

    def move(self):
        # Get neighborhood
        neighbours = [i for i in self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False, radius=self.vision
        )]

        # Get cell with most sugar
        max_welfare = -1
        best_position = self.pos
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

            for agent in this_cell:
                if isinstance(agent, Cell):
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
        if self.sugar < 0:
            self.remove()

        # Die if spice is less than 0
        if self.spice < 0:
            self.remove()

    def trade(self):
        pass

    def welfare(self, sugar, spice):
        return sugar ** self.sugar_weight * spice ** self.spice_weight

    def update_wealth(self):
        self.wealth = self.welfare(self.sugar, self.spice)

    def remove(self):
        self.model.grid.remove_agent(self)
        self.model.schedule.remove(self)
        del self.model.traders[self.unique_id]
        self.model.deaths += 1
