from src.SugarScape import SugarScape
from mesa import batch_run
import numpy as np
from tqdm import tqdm
import SALib
from SALib.analyze import sobol
from SALib.sample.sobol import sample
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt


def __save_samples(ranges, distinct_samples, splits=8):
    # Create problem
    problem = {
        'num_vars': len(ranges),
        'names': list(ranges.keys()),
        'bounds': list(ranges.values())
    }

    # Get samples
    samples = sample(problem, distinct_samples)

    # Create dataframe
    df = pd.DataFrame(samples, columns=problem['names'])

    # Split into splits
    split_dfs = np.array_split(df, splits)

    # Get current directory
    current_directory = Path(__file__).parent

    # Go to parent directory
    parent_directory = current_directory.parent

    # Split dataframe
    for i in range(splits):
        # Create folder
        Path(f"{parent_directory}/SA/split_{i + 1}").mkdir(parents=True, exist_ok=True)

        # Splitting into 5 files
        split_df = np.array_split(split_dfs[i], 5)

        # Save samples
        for j in range(5):
            split_df[j].to_csv(f"{parent_directory}/SA/split_{i + 1}/samples_{j + 1}.csv", index=False)


def run_model(file, replicates=10, max_steps=300):
    # Load samples
    samples = pd.read_csv(file)

    # Run batch
    results = []
    with tqdm(total=len(samples), ncols=100) as pbar:
        for row in samples.iterrows():
            params = row[1].to_dict()
            batches = batch_run(SugarScape, params, number_processes=None,
                                iterations=replicates, max_steps=max_steps, display_progress=False)

            for i in range(replicates):
                params["Gini"] = batches[i]["Gini"]
                params["Trader Count"] = batches[i]["Trader Count"]
                results += [params]
            pbar.update(1)

    # Get directory of file
    directory = Path(file).parent

    # Get file number
    file_number = file.split("_")[-1].split(".")[0]

    # Save results
    pd.DataFrame(results).to_csv(f"{directory}/results_{file_number}.csv", index=False)


def load_data(path="SA"):
    # Get all directories
    directories = list(Path(path).iterdir())

    # Load all results
    results = pd.DataFrame()
    for directory in directories:
        files = list(directory.iterdir())
        for file in files:
            if "results" in file.name:
                result = pd.read_csv(file)
                results = pd.concat([results, result])

    # Reset index
    results = results.reset_index(drop=True)

    return results


def analyse(problem, results):
    # Get Gini index and Trader count
    gini = results["Gini"]
    trader_count = results["Trader Count"]

    # Perform analysis
    Si_gini = sobol.analyze(problem, gini.values)
    Si_trader_count = sobol.analyze(problem, trader_count.values)

    return Si_gini, Si_trader_count


def has_converged(Si_gini, Si_trader_count):
    # Get names
    indices = ["S1", "ST"]

    for index in indices:
        # Get values
        gini = Si_gini[index]
        trader_count = Si_trader_count[index]

        # Get confidence intervals
        gini_CI = Si_gini[f"{index}_conf"]
        trader_count_CI = Si_trader_count[f"{index}_conf"]

        # Checking left bounds
        if np.any(gini - gini_CI < 0) or np.any(trader_count - trader_count_CI < 0):
            print(f"Sensitivity indices have not converged")
            return

        # Checking right bounds
        # if np.any(gini + gini_CI > 1) or np.any(trader_count + trader_count_CI > 1):
        #     return False

    print("Sensitivity indices have converged")


def plot_indices(Si_gini, Si_trader_count, problem):
    # Create subplots
    fig, axs = plt.subplots(2, 2, figsize=(10, 10))

    # Get indices
    indices = ["S1", "ST"]

    # X-labels
    x_labels = problem["names"]
    ticks = range(len(x_labels))

    for i in range(2):
        # Plotting for gini
        axs[i, 0].plot(Si_gini[indices[i]], ticks, 'o')
        axs[i, 0].errorbar(Si_gini[indices[i]], ticks, xerr=Si_gini[f"{indices[i]}_conf"], fmt='o')
        axs[i, 0].set_title(f"Gini {indices[i]}")
        axs[i, 0].set_yticks(range(len(x_labels)))
        axs[i, 0].set_yticklabels(x_labels, rotation=45)

        # Plotting for trader count
        axs[i, 1].plot(Si_trader_count[indices[i]], ticks, 'o')
        axs[i, 1].errorbar(Si_trader_count[indices[i]], ticks, xerr=Si_trader_count[f"{indices[i]}_conf"], fmt='o')
        axs[i, 1].set_title(f"Trader Count {indices[i]}")
        axs[i, 1].set_yticks(range(len(x_labels)))
        axs[i, 1].set_yticklabels(x_labels, rotation=45)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    ranges = {
        "vision_mean": [1, 6],
        "metabolism_mean": [1, 6],
        "max_age_mean": [70, 100],
        "repopulate_factor": [5, 15],
        "cell_regeneration": [1, 5],
    }

    __save_samples(ranges, 1024, splits=8)
