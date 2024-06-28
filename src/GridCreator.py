from numpy.random import poisson
from numpy import maximum
from .Agents.Cell import Cell


class GridCreator:
    def __init__(self, model, map_scheme, cell_regeneration):
        self.model = model
        self.map_scheme = map_scheme
        self.cell_regeneration = cell_regeneration

    def create_grid(self):
        if self.map_scheme == "uniform":
            self.uniform_map()
        elif self.map_scheme == "top_heavy":
            self.top_heavy_map()
        elif self.map_scheme == "split":
            self.split_map()

    def uniform_map(self):
        for content, (x, y) in self.model.grid.coord_iter():
            # Generate random capacities
            capacities = poisson(6, 2)

            # Minimum has to be 1
            capacities = maximum(capacities, 1)

            # Place cell
            self.place_cell(capacities, x, y)

    def top_heavy_map(self):
        # Get size of grid
        width, height = self.model.grid.width, self.model.grid.height

        # Get the middle of the grid
        middle = width // 2

        for content, (x, y) in self.model.grid.coord_iter():
            # Generate capacities
            capacities = poisson(11, 2) if y > middle else poisson(1, 2)

            # Minimum has to be 1
            capacities = maximum(capacities, 1)

            # Place cell
            self.place_cell(capacities, x, y)

    def split_map(self):
        # Get size of grid
        width, height = self.model.grid.width, self.model.grid.height

        # Get the middle of the grid
        middle = height // 2

        for content, (x, y) in self.model.grid.coord_iter():
            # Generate capacities
            capacities = [poisson(10), poisson(2)] if y > middle else [poisson(2), poisson(10)]

            # Minimum has to be 1
            capacities = maximum(capacities, 1)

            # Place cell
            self.place_cell(capacities, x, y)

    def place_cell(self, capacities, x, y):
        # Initialize cell
        cell = Cell(self.model.last_id, self.model, capacities, self.cell_regeneration)

        # Place cell on grid
        self.model.grid.place_agent(cell, (x, y))
        self.model.schedule.add(cell)

        # Increment id
        self.model.last_id += 1
