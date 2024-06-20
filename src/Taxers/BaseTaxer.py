from src.Agents.Trader import Trader


class BaseTaxer:
    def __init__(self, tax_steps, tax_rate) -> None:
        self.tax_steps = tax_steps
        self.tax_rate = tax_rate
        self.taxes_collection = {"sugar": 0, "spice": 0}
        self.current_step = 0

    def step(self, agents):
        self.current_step += 1
        if self.current_step % self.tax_steps == 0:
            self.collect_taxes(agents)

    def collect_taxes(self, agents):
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

    def reset_tax(self):
        self.taxes_collection = {"sugar": 0, "spice": 0}
