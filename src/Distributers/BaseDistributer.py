from src.Agents.Trader import Trader
from src.Taxers.BaseTaxer import BaseTaxer


class BaseDistributer:
    """
    Base class for distributers. All other distributers should inherit from this class. Every class that inherits from
    this class should implement the distribute method with two arguments: agents and taxer.

    Attributes:
        distributer_steps (int): Number of steps between each distribution
        current_step (int): Current step number

    Methods:
        step(agents, taxer):
            Distributes the taxes to the agents every distributer_steps steps
        distribute(agents, taxer):
            Distributes the taxes to the agents
    """
    def __init__(self, distributer_steps: int):
        """
        Constructor for BaseDistributer

        Args:
            distributer_steps (int): Number of steps between each distribution
        """
        self.distributer_steps = distributer_steps
        self.current_step = 0

    def step(self, agents: dict, taxer: BaseTaxer) -> None:
        """
        Take step in the distributer. Distributes the taxes to the agents every distributer_steps steps.

        Args:
            agents (dict): Dictionary of agents
            taxer (BaseTaxer): Taxer object

        Returns:
            None

        """
        self.current_step += 1
        if self.current_step % self.distributer_steps == 0:
            self.distribute(agents, taxer)

    def distribute(self, agents: dict, taxer: BaseTaxer) -> None:
        """
        Distributes the taxes to the agents

        Args:
            agents (dict): Dictionary of agents
            taxer (BaseTaxer): Taxer object

        Returns:
            None
        """
        total_agents = len([agent for agent in agents if isinstance(agent, Trader)])
        if total_agents > 0:
            sugar_per_agent = taxer.taxes_collection["sugar"] / total_agents
            spice_per_agent = taxer.taxes_collection["spice"] / total_agents
            for agent in agents:
                agent.sugar += sugar_per_agent
                agent.spice += spice_per_agent

            # Reset taxes collection
            taxer.reset_tax()
