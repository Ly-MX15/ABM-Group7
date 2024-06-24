import logging
import pandas as pd
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
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

def run_model(args):
    map_scheme, replicate, seed_value, max_steps, step_size = args
    """Run the SugarScape model with given parameters and log the process."""
    logger = setup_logger()
    logger.info(f"Running experiment: map_scheme={map_scheme},  replicate={replicate}")
    print(f"Running experiment: map_scheme={map_scheme}, replicate={replicate}")
    
    model = SugarScape(map_scheme=map_scheme,
                       #tax_scheme=tax_scheme,
                       #distributer_scheme=distributer_scheme,
                       #tax_rate=tax_rate,
                       height=50, width=50, initial_population=300,
                       metabolism_mean=4 if map_scheme == "top_heavy" else 5 if map_scheme == "uniform" else 3,
                       vision_mean=5 if map_scheme == "top_heavy" else 2 if map_scheme == "uniform" else 4,
                       max_age_mean=70,
                       tax_steps=20, distributer_steps=20, repopulate_factor=10, tax_bool=False,
                       seed_value=seed_value)
    
    gini_over_time = []
    agents_over_time = []
    
    for step in range(max_steps):
        model.step()
        if step % step_size == 0:  # Output every step
            logger.info(f"Model step {step}: map_scheme={map_scheme}, replicate={replicate}")
            gini_coefficient = model.datacollector.get_model_vars_dataframe()['Gini'].values[-1]
            gini_over_time.append(float(gini_coefficient))
            agents_over_time.append(len(model.traders))
    
    gini_coefficient = model.datacollector.get_model_vars_dataframe()['Gini'].values[-1]
    logger.info(f"Finished: map_scheme={map_scheme}, replicate={replicate}, gini_coefficient={gini_coefficient}")
    
    return map_scheme, list(range(0, max_steps, step_size)), gini_over_time, agents_over_time

# Define experiment parameters
max_steps = 500
replicates = 10
tax_rates = [0.1, 0.25, 0.4]
step_size = 1

# Define the different map schemes
map_schemes = ['uniform','top_heavy', 'split']

# Define the combinations of tax and redistribution schemes
combinations = [
    ("progressive", "needs"),
    ("flat", "flat"),
    ("regressive", "random"),
    ("luxury", "progressive"),
    ("progressive", "progressive")
]

def run_experiments():
    # Generate the list of arguments for each experiment
    args_list = []
    for map_scheme in map_schemes:
        #for tax_scheme, distributer_scheme in combinations:
            #for tax_rate in tax_rates:
                for replicate in range(replicates):
                    #args = (map_scheme, tax_scheme, distributer_scheme, tax_rate, replicate, None, max_steps, step_size)
                    args =(map_scheme, replicate, None, max_steps, step_size)
                    args_list.append(args)
    
    # Run the experiments in parallel
    with Pool(cpu_count() - 1) as pool:  # Use all available CPUs except one
        results = list(tqdm(pool.imap(run_model, args_list), total=len(args_list)))

    # Organize results and save to CSV
    for map_scheme in map_schemes:
        results_data = [result for result in results if result[0] == map_scheme]
        columns = ['Map Scheme', 'Time Steps', 'Gini Over Time', 'Agents Over Time']
        results_df = pd.DataFrame(results_data, columns=columns)
        results_df.to_csv(f'experiments_results_basic_{map_scheme}.csv', index=False)

if __name__ == "__main__":
    print("Starting experiments...")
    run_experiments()
    print("All experiments done!")