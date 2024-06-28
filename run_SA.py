from src.SensitivityAnalysis import *

ranges = {
    "vision_mean": [1, 6],
    "metabolism_mean": [1, 6],
    "max_age_mean": [70, 100],
    "repopulate_factor": [5, 15],
    "cell_regeneration": [1, 5],
}

problem = {
    "num_vars": len(ranges),
    "names": list(ranges.keys()),
    "bounds": list(ranges.values())
}

## Only change split if all files within this split have been run
split = 1

## Set the file_num based on your name
# amish = 1
# priyank = 2
# menghan = 3
# yuan = 4
# ilia = 5
file_num = 2

# Run model
file = f"SA/split_{split}/samples_{file_num}.csv"
run_model(file, replicates=10, max_steps=200)

## Perform sensitivity analysis
# # Get results
# results = load_data()
#
# # Get sensitivity indices
# Si_gini, Si_trader_count = analyse(problem, results)
#
# # Check for convergence
# has_converged(Si_gini, Si_trader_count)
#
# # Plot indices
# plot_indices(Si_gini, Si_trader_count, problem)
