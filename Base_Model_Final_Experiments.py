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
    map_scheme, replicate, seed_value, max_steps, step_size, cell_regeneration, repopulate_factor, metabolism_mean = args
    """Run the SugarScape model with given parameters and log the process."""
    logger = setup_logger()
    logger.info(f"Running experiment: map_scheme={map_scheme}, replicate={replicate}, cell_regeneration={cell_regeneration}, repopulate_factor={repopulate_factor}, metabolism_mean={metabolism_mean}")
    print(f"Running experiment: map_scheme={map_scheme}, replicate={replicate}, cell_regeneration={cell_regeneration}, repopulate_factor={repopulate_factor}, metabolism_mean={metabolism_mean}")
    
    model = SugarScape(map_scheme=map_scheme,
                       height=50, width=50, initial_population=300,
                       metabolism_mean=metabolism_mean, vision_mean=3, max_age_mean=85,
                       repopulate_factor=repopulate_factor,
                       cell_regeneration=cell_regeneration,
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
    
    return map_scheme, list(range(0, max_steps, step_size)), gini_over_time, agents_over_time, cell_regeneration, repopulate_factor, metabolism_mean

# Define experiment parameters
max_steps = 250
replicates = 20
step_size = 1

# Define the different map schemes
map_schemes = ['uniform', 'top_heavy', 'split']

# Define the best, worst, and average scenarios
scenarios = [
    {"cell_regeneration": 5, "repopulate_factor": 15, "metabolism_mean": 3},  # Best case
    {"cell_regeneration": 1, "repopulate_factor": 5, "metabolism_mean": 9},   # Worst case
    {"cell_regeneration": 3, "repopulate_factor": 10, "metabolism_mean": 6}   # Average case
]

def run_experiments():
    # Generate the list of arguments for each experiment
    args_list = []
    for map_scheme in map_schemes:
        for scenario in scenarios:
            for replicate in range(replicates):
                args = (map_scheme, replicate, None, max_steps, step_size, scenario["cell_regeneration"], scenario["repopulate_factor"], scenario["metabolism_mean"])
                args_list.append(args)
    
    # Run the experiments in parallel
    with Pool(cpu_count() - 1) as pool:  # Use all available CPUs except one
        results = list(tqdm(pool.imap(run_model, args_list), total=len(args_list)))

    # Organize results and save to CSV
    for map_scheme in map_schemes:
        results_data = [result for result in results if result[0] == map_scheme]
        columns = ['Map Scheme', 'Time Steps', 'Gini Over Time', 'Agents Over Time', 'Cell Regeneration', 'Repopulate Factor', 'Metabolism Mean']
        results_df = pd.DataFrame(results_data, columns=columns)
        results_df.to_csv(f'experiments_results_base_{map_scheme}.csv', index=False)

if __name__ == "__main__":
    print("Starting experiments...")
    run_experiments()
    print("All experiments done!")


# import logging
# import pandas as pd
# from tqdm import tqdm
# from multiprocessing import Pool, cpu_count
# from src.SugarScape import SugarScape

# def setup_logger():
#     """Set up a logger for simulation."""
#     logger = logging.getLogger("simulation")
#     handler = logging.FileHandler("simulation.log")
#     formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
#     handler.setFormatter(formatter)
#     logger.addHandler(handler)
#     logger.setLevel(logging.INFO)
#     return logger

# def run_model(args):
#     map_scheme, replicate, seed_value, max_steps, step_size, cell_regeneration, repopulate_factor, metabolism_mean = args
#     """Run the SugarScape model with given parameters and log the process."""
#     logger = setup_logger()
#     logger.info(f"Running experiment: map_scheme={map_scheme}, replicate={replicate}, cell_regeneration={cell_regeneration}, repopulate_factor={repopulate_factor}, metabolism_mean={metabolism_mean}")
#     print(f"Running experiment: map_scheme={map_scheme}, replicate={replicate}, cell_regeneration={cell_regeneration}, repopulate_factor={repopulate_factor}, metabolism_mean={metabolism_mean}")
    
#     model = SugarScape(map_scheme=map_scheme,
#                        height=50, width=50, initial_population=300,
#                        metabolism_mean=metabolism_mean, vision_mean=3, max_age_mean=85,
#                        repopulate_factor=repopulate_factor,
#                        cell_regeneration=cell_regeneration,
#                        seed_value=seed_value)
    
#     gini_over_time = []
#     agents_over_time = []
    
#     for step in range(max_steps):
#         model.step()
#         if step % step_size == 0:  # Output every step
#             logger.info(f"Model step {step}: map_scheme={map_scheme}, replicate={replicate}")
#             gini_coefficient = model.datacollector.get_model_vars_dataframe()['Gini'].values[-1]
#             gini_over_time.append(float(gini_coefficient))
#             agents_over_time.append(len(model.traders))
    
#     gini_coefficient = model.datacollector.get_model_vars_dataframe()['Gini'].values[-1]
#     logger.info(f"Finished: map_scheme={map_scheme}, replicate={replicate}, gini_coefficient={gini_coefficient}")
    
#     return map_scheme, cell_regeneration, repopulate_factor, metabolism_mean, list(range(0, max_steps, step_size)), gini_over_time, agents_over_time

# # Define experiment parameters
# max_steps = 200
# replicates = 20
# step_size = 1

# # Define the specific map scheme to run experiments for
# specific_map_scheme = 'uniform'

# # Define varying parameters
# cell_regeneration_values = [1, 3, 5]
# repopulate_factor_values = [5, 10, 15]
# metabolism_mean_values = [3, 6, 9]

# def run_experiments():
#     # Generate the list of arguments for each experiment
#     args_list = []
#     for cell_regeneration in cell_regeneration_values:
#         for repopulate_factor in repopulate_factor_values:
#             for metabolism_mean in metabolism_mean_values:
#                 for replicate in range(replicates):
#                     args = (specific_map_scheme, replicate, None, max_steps, step_size, cell_regeneration, repopulate_factor, metabolism_mean)
#                     args_list.append(args)
    
#     # Run the experiments in parallel
#     with Pool(cpu_count() - 1) as pool:  # Use all available CPUs except one
#         results = list(tqdm(pool.imap(run_model, args_list), total=len(args_list)))

#     # Organize results and save to CSV
#     results_data = [result for result in results if result[0] == specific_map_scheme]
#     columns = ['Map Scheme', 'Cell Regeneration', 'Repopulate Factor', 'Metabolism Mean', 'Time Steps', 'Gini Over Time', 'Agents Over Time']
#     results_df = pd.DataFrame(results_data, columns=columns)
#     results_df.to_csv(f'experiments_results_base_{specific_map_scheme}.csv', index=False)

# if __name__ == "__main__":
#     print("Starting experiments...")
#     run_experiments()
#     print("All experiments done!")
