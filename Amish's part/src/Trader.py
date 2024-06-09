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

    def step(self):
        # Move agent
        self.move()

        # Pick up sugar and spice
        self.pick_up()

        # Trade sugar and spice
        self.trade()

        # Metabolize sugar and spice
        self.metabolize()

    def move(self):
        # Get neighborhood
        neighbours = [i
                      for i in self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=False, radius=self.vision)]

        # Get cell with most sugar
        max_total = -1
        shortest_distance = 100
        max_cell = []
        for neighbour in neighbours:
            this_cell = self.model.grid.get_cell_list_contents([neighbour])
            for agent in this_cell:
                if isinstance(agent, Cell):
                    # Compute weighted average of sugar and spice
                    weighted_sugar = self.sugar_weight * agent.sugar
                    weighted_spice = self.spice_weight * agent.spice
                    total = weighted_sugar + weighted_spice

                    # Update max_sugar and max_sugar_cells
                    if total > max_total:
                        # Get distance to cell
                        distance = get_distance(self.pos, neighbour)
                        shortest_distance = distance
                        max_total = total
                        max_cell = [neighbour]

                    # Append to max_sugar_cells if equal
                    elif total == max_total:
                        # Get distance to cell
                        distance = get_distance(self.pos, neighbour)
                        if distance < shortest_distance:
                            shortest_distance = distance
                            max_cell = [neighbour]
                        elif distance == shortest_distance:
                            max_cell.append(neighbour)

        # Move to cell with most sugar
        new_position = random.choice(range(len(max_cell)))
        new_position = max_cell[new_position]
        self.model.grid.move_agent(self, new_position)

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
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)

        # Die if spice is less than 0
        if self.spice < 0:
            self.model.grid._remove_agent(self.pos, self)
            self.model.schedule.remove(self)

    def trade(self):
        pass