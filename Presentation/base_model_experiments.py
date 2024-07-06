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
    map_scheme, metabolism_mean, replicate, seed_value, max_steps, step_size = args
    """Run the SugarScape model with given parameters and log the process."""
    logger = setup_logger()
    logger.info(f"Running experiment: map_scheme={map_scheme}, metabolism_mean={metabolism_mean}, replicate={replicate}")
    print(f"Running experiment: map_scheme={map_scheme}, metabolism_mean={metabolism_mean}, replicate={replicate}")
    
    model = SugarScape(map_scheme=map_scheme,
                       height=50, width=50, initial_population=300,
                       metabolism_mean=metabolism_mean,
                       vision_mean=2,
                       max_age_mean=70,
                       tax_steps=20, distributer_steps=20, repopulate_factor=10, tax_bool=False,
                       seed_value= seed_value)
    
    gini_over_time = []
    agents_over_time = []
    
    for step in range(max_steps):
        model.step()
        if step % step_size == 0:  # Output every step
            logger.info(f"Model step {step}: map_scheme={map_scheme}, metabolism_mean={metabolism_mean}, replicate={replicate}")
            gini_coefficient = model.datacollector.get_model_vars_dataframe()['Gini'].values[-1]
            gini_over_time.append(float(gini_coefficient))
            agents_over_time.append(len(model.traders))
    
    gini_coefficient = model.datacollector.get_model_vars_dataframe()['Gini'].values[-1]
    logger.info(f"Finished: map_scheme={map_scheme}, metabolism_mean={metabolism_mean}, replicate={replicate}, gini_coefficient={gini_coefficient}")
    
    return map_scheme, metabolism_mean, list(range(0, max_steps, step_size)), gini_over_time, agents_over_time

# Define experiment parameters
max_steps = 300
replicates = 10
step_size = 1

# Define the different map schemes
map_schemes = ['uniform','top_heavy', 'split']

# Define the metabolism mean range
metabolism_means = range(1, 6)

def run_experiments():
    # Generate the list of arguments for each experiment
    args_list = []
    for map_scheme in map_schemes:
        for metabolism_mean in metabolism_means:
            for replicate in range(replicates):
                args = (map_scheme, metabolism_mean, replicate, None, max_steps, step_size)
                args_list.append(args)
    
    # Run the experiments in parallel
    with Pool(cpu_count() - 1) as pool:  # Use all available CPUs except one
        results = list(tqdm(pool.imap(run_model, args_list), total=len(args_list)))

    # Organize results and save to CSV
    for map_scheme in map_schemes:
        for metabolism_mean in metabolism_means:
            results_data = [result for result in results if result[0] == map_scheme and result[1] == metabolism_mean]
            columns = ['Map Scheme', 'Metabolism Mean', 'Time Steps', 'Gini Over Time', 'Agents Over Time']
            results_df = pd.DataFrame(results_data, columns=columns)
            results_df.to_csv(f'experiments_results_{map_scheme}_metabolism_{metabolism_mean}.csv', index=False)

if __name__ == "__main__":
    print("Starting experiments...")
    run_experiments()
    print("All experiments done!")