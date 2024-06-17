class BaseTaxer:
    def __init__(self, tax_steps, distributer, distributer_steps) -> None:
        self.tax_steps = tax_steps
        self.distributer = distributer(distributer_steps)

        # Storing collected taxes
        self.taxes_collection = 0

        # Storing current step
        self.current_step = 0

    def step(self, agents):
        # Increase current step
        self.current_step += 1

        # Check if it is time to tax
        if self.current_step % self.tax_steps == 0:
            # Collect taxes
            self.collect_taxes(agents)

            # Reset taxes collection
            self.taxes_collection = 0

        # Take step for distributer
        self.distributer.step(agents)

    def collect_taxes(self, agents):
        pass
