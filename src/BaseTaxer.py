from src.Trader import Trader


class BaseTaxer:
    def __init__(self, model, tax_steps, tax_rate) -> None:
        self.model = model
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
            if isinstance(agent, Trader):
                sugar_tax = agent.sugar * self.tax_rate
                spice_tax = agent.spice * self.tax_rate
                agent.sugar -= sugar_tax
                agent.spice -= spice_tax
                self.taxes_collection["sugar"] += sugar_tax
                self.taxes_collection["spice"] += spice_tax
                self.model.total_sugar_tax_collected += sugar_tax
                self.model.total_spice_tax_collected += spice_tax

    def reset_tax(self):
        self.taxes_collection = {"sugar": 0, "spice": 0}