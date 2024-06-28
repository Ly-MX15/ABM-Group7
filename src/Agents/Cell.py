from mesa import Agent


class Cell(Agent):
    def __init__(self, unique_id, model, capacities, cell_regeneration):
        super().__init__(unique_id, model)

        # Initialize sugar, spice and capacities
        self.capacities = capacities
        self.sugar = capacities[0]
        self.spice = capacities[1]

        # Initialize regeneration rate
        self.cell_regeneration = cell_regeneration

    def step(self):
        # Move agent
        self.regenerate()

    def regenerate(self):
        # Regenerate sugar
        self.sugar = min(self.sugar + self.cell_regeneration, self.capacities[0])
        self.spice = min(self.spice + self.cell_regeneration, self.capacities[1])
