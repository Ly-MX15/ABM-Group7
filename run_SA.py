from src.SensitivityAnalysis import *

ranges = {
    "vision_mean": [1, 6],
    "metabolism_mean": [1, 4],
    "max_age_mean": [60, 100],
    "repopulate_factor": [5, 15],
    "cell_regeneration": [1, 3],
}

problem = {
    "num_vars": len(ranges),
    "names": list(ranges.keys()),
    "bounds": list(ranges.values())
}

## Perform simulations by setting split and file_num
split = 1
file_num = 1
file = f"SA/split_{split}/samples_{file_num}.csv"
run_model(file, replicates=10, max_steps=300)


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