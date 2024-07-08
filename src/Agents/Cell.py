from mesa import Agent
from mesa.model import Model


class Cell(Agent):
    """
    A cell agent with sugar and spice attributes.

    Attributes:
        capacities (list[int]): Capacities of the cell.
        sugar (int): Sugar of the cell.
        spice (int): Spice of the cell.
        cell_regeneration (float): Regeneration rate of the cell.

    Methods:
        step()
            Take a step for the cell agent.
        regenerate()
            Regenerate sugar and spice.
    """
    def __init__(self, unique_id: int, model: Model, capacities: list[int], cell_regeneration: float):
        """
        Initialize cell agent.

        Args:
            unique_id (int): ID of the agent.
            model (SugarScape): Model of the agent.
            capacities (list[int]): Capacities of the cell.
            cell_regeneration (float): Regeneration rate of the cell.
        """
        super().__init__(unique_id, model)

        # Initialize sugar, spice and capacities
        self.capacities = capacities
        self.sugar = capacities[0]
        self.spice = capacities[1]

        # Initialize regeneration rate
        self.cell_regeneration = cell_regeneration

    def step(self) -> None:
        """
        Take a step for the cell agent.

        Returns:
            None

        """
        # Move agent
        self.regenerate()

    def regenerate(self) -> None:
        """
        Regenerate sugar and spice.

        Returns:
            None
        """
        # Regenerate sugar
        self.sugar = min(self.sugar + self.cell_regeneration, self.capacities[0])
        self.spice = min(self.spice + self.cell_regeneration, self.capacities[1])
