class BaseDistributer:
    def __init__(self, distributer_steps) -> None:
        self.distributer_steps = distributer_steps
        # Storing current step
        self.current_step = 0

    def step(self, agents, collect_taxes):
        # Increase current step
        self.current_step += 1
        # Check if it is time to distribute
        if self.current_step % self.distributer_steps == 0:
            # Distribute
            self.distribute(agents, collect_taxes)

            # Reset current step
            self.current_step = 0

    def distribute(self, agents, collect_taxes):
        pass
