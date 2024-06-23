import logging
import pandas as pd
from tqdm import tqdm
from src.SugarScape import SugarScape

def setup_logger():
    """Set up a logger for simulation."""
    logger = logging.getLogger("simulation")
    handler = logging.FileHandler("simulation.log")
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

def run_model(map_scheme, tax_scheme, distributer_scheme, tax_rate, replicate, seed_value):
    """Run the SugarScape model with given parameters and log the process."""
    logger = setup_logger()
    logger.info(f"Running experiment: map_scheme={map_scheme}, tax_scheme={tax_scheme}, distributer_scheme={distributer_scheme}, tax_rate={tax_rate}, replicate={replicate}")
    print(f"Running experiment: map_scheme={map_scheme}, tax_scheme={tax_scheme}, distributer_scheme={distributer_scheme}, tax_rate={tax_rate}, replicate={replicate}")
    
    model = SugarScape(map_scheme=map_scheme,
                       tax_scheme=tax_scheme,
                       distributer_scheme=distributer_scheme,
                       tax_rate=tax_rate,
                       seed_value=seed_value)
    
    gini_over_time = []
    
    for step in range(max_steps):
        model.step()
        if step % 10 == 0:  # Output every 10 steps
            logger.info(f"Model step {step}: map_scheme={map_scheme}, tax_scheme={tax_scheme}, distributer_scheme={distributer_scheme}, tax_rate={tax_rate}, replicate={replicate}")
            gini_coefficient = model.datacollector.get_model_vars_dataframe()['Gini'].values[-1]
            gini_over_time.append(float(gini_coefficient))
    
    gini_coefficient = model.datacollector.get_model_vars_dataframe()['Gini'].values[-1]
    logger.info(f"Finished: map_scheme={map_scheme}, tax_scheme={tax_scheme}, distributer_scheme={distributer_scheme}, tax_rate={tax_rate}, replicate={replicate}, gini_coefficient={gini_coefficient}")
    
    return map_scheme, tax_scheme, distributer_scheme, tax_rate, list(range(0, max_steps, 10)), gini_over_time

# Define experiment parameters
max_steps = 500
replicates = 5
tax_rates = [0.1, 0.25, 0.4]

# Define the different map schemes
map_schemes = ['uniform', 'top_heavy', 'split']

# Define the combinations of tax and redistribution schemes
combinations = [
    ("progressive", "needs"),
    ("flat", "flat"),
    ("regressive", "random"),
    ("luxury", "progressive"),
    ("progressive", "progressive")
]

# Run experiments
for map_scheme in map_schemes:
    results_data = []
    for tax_scheme, distributer_scheme in combinations:
        for tax_rate in tax_rates:
            for replicate in range(replicates):
                result = run_model(map_scheme, tax_scheme, distributer_scheme, tax_rate, replicate, seed_value=None)
                results_data.append(result)
    
    # Save results to a DataFrame and CSV file
    columns = ['Map Scheme', 'Tax Scheme', 'Distributer Scheme', 'Tax Rate', 'Time Steps', 'Gini Over Time']
    results_df = pd.DataFrame(results_data, columns=columns)
    results_df.to_csv(f'experiments_results_{map_scheme}.csv', index=False)

print("All experiments done!")


