from src.Agents.Trader import Trader


class BaseDistributer:
    def __init__(self, distributer_steps) -> None:
        self.distributer_steps = distributer_steps
        self.current_step = 0

    def step(self, agents, taxer):
        self.current_step += 1
        if self.current_step % self.distributer_steps == 0:
            self.distribute(agents, taxer)

    def distribute(self, agents, taxer):
        total_agents = len([agent for agent in agents if isinstance(agent, Trader)])
        if total_agents > 0:
            sugar_per_agent = taxer.taxes_collection["sugar"] / total_agents
            spice_per_agent = taxer.taxes_collection["spice"] / total_agents
            for agent in agents:
                agent.sugar += sugar_per_agent
                agent.spice += spice_per_agent

            # Reset taxes collection
            taxer.reset_tax()
