from src.Agents.Trader import Trader


class BaseTaxer:
    """
    Base class for all taxers. It defines the interface for taxers, and provides a basic implementation of the step method.
    Every other taxer should inherit from this class and implement the collect_taxes method with only one argument: traders.

    Attributes:
        tax_steps (int): Number of steps between each tax collection
        tax_rate (float): Tax rate
        taxes_collection (dict): Dictionary to store the collected taxes
        current_step (int): Current step number

    Methods:
        step(traders):
            Collects taxes from the traders every tax_steps steps
        collect_taxes(traders):
            Collects taxes from the traders
        reset_tax():
            Resets the taxes collection
    """
    def __init__(self, tax_steps: int, tax_rate: float):
        """
        Constructor for BaseTaxer.

        Args:
            tax_steps (int): Number of steps between each tax collection
            tax_rate (float): Tax rate

        """
        self.tax_steps = tax_steps
        self.tax_rate = tax_rate
        self.taxes_collection = {"sugar": 0, "spice": 0}
        self.current_step = 0

    def step(self, agents: dict) -> None:
        """
        Take step in the taxer. Collects taxes from the traders every tax_steps steps.

        Args:
            agents (dict): Dictionary of agents

        Returns:
            None
        """
        self.current_step += 1
        if self.current_step % self.tax_steps == 0:
            self.collect_taxes(agents)

    def collect_taxes(self, agents: dict) -> None:
        """
        Collects taxes from the traders. This method should be implemented by the child classes.

        Args:
            agents (dict): Dictionary of agents

        Returns:
            None
        """
        for agent in agents:
            # Compute excessive sugar and spice
            excessive_sugar = max(0, agent.sugar - agent.sugar_metabolism)
            excessive_spice = max(0, agent.spice - agent.spice_metabolism)

            # Compute tax
            sugar_tax = int(self.tax_rate * excessive_sugar)
            spice_tax = int(self.tax_rate * excessive_spice)

            # Update agent's goods and taxes collection
            agent.sugar -= sugar_tax
            agent.spice -= spice_tax
            self.taxes_collection["sugar"] += sugar_tax
            self.taxes_collection["spice"] += spice_tax

    def reset_tax(self) -> None:
        """
        Resets the taxes collection.

        Returns:
            None
        """
        self.taxes_collection = {"sugar": 0, "spice": 0}
