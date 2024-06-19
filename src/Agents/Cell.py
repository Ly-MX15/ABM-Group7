from mesa import Agent


class Cell(Agent):
    def __init__(self, unique_id, model, capacities):
        super().__init__(unique_id, model)

        # Initialize sugar and spice
        self.capacities = capacities
        self.sugar = capacities[0]
        self.spice = capacities[1]

    def step(self):
        # Move agent
        self.regenerate()

    def regenerate(self):
        # Regenerate sugar
        self.sugar = min(self.sugar + 1, self.capacities[0])
        self.spice = min(self.spice + 1, self.capacities[1])
