from numpy.random import poisson
from numpy import maximum
from .Agents.Cell import Cell
from mesa.model import Model


class GridCreator:
    """
    Class to create a grid for the model

    Attributes:
        model (Model): The model to create the grid for
        map_scheme (str): The scheme to use for the grid creation
        cell_regeneration (float): The amount of energy a cell regenerates each step

    Methods:
        create_grid()
            Create a grid for the model.
        uniform_map()
            Create a uniform grid.
        top_heavy_map()
            Create a top heavy grid.
        split_map()
            Create a split grid.
        place_cell(capacities: list[int], x: int, y: int)
            Place a cell on the
    """
    def __init__(self, model: Model, map_scheme: str, cell_regeneration: float):
        """
        Constructor for GridCreator

        Args:
            model (SugarScape): The model to create the grid for
            map_scheme (str): The scheme to use for the grid creation
            cell_regeneration (float): The amount of energy a cell regenerates each step
        """
        self.model = model
        self.map_scheme = map_scheme
        self.cell_regeneration = cell_regeneration

    def create_grid(self) -> None:
        """
        Create a grid for the model

        Returns:
            None
        """
        if self.map_scheme == "uniform":
            self.uniform_map()
        elif self.map_scheme == "top_heavy":
            self.top_heavy_map()
        elif self.map_scheme == "split":
            self.split_map()

    def uniform_map(self) -> None:
        """
        Create a uniform grid

        Returns:
            None
        """
        for content, (x, y) in self.model.grid.coord_iter():
            # Generate random capacities
            capacities = poisson(6, 2)

            # Minimum has to be 1
            capacities = maximum(capacities, 1)

            # Place cell
            self.place_cell(capacities, x, y)

    def top_heavy_map(self) -> None:
        """
        Create a top heavy grid

        Returns:
            None
        """
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

    def split_map(self) -> None:
        """
        Create a split grid

        Returns:
            None
        """
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

    def place_cell(self, capacities: list[int], x: int, y: int) -> None:
        """
        Place a cell on the grid
        Args:
            capacities (list[int]): The capacities of the cell for both sugar and spice
            x (int): The x coordinate of the cell
            y (int): The y coordinate of the cell

        Returns:
            None
        """
        # Initialize cell
        cell = Cell(self.model.last_id, self.model, capacities, self.cell_regeneration)

        # Place cell on grid
        self.model.grid.place_agent(cell, (x, y))
        self.model.schedule.add(cell)

        # Increment id
        self.model.last_id += 1
