from src.SugarScape import SugarScape
from mesa import batch_run
import numpy as np
from tqdm import tqdm
from SALib.analyze import sobol
from SALib.sample.sobol import sample
import pandas as pd
import os
import matplotlib.pyplot as plt


def __save_samples(ranges: dict, distinct_samples: int, splits: int = 8) -> None:
    """
    Create samples using Sobol sequence and save them in different splits for parallel processing. Results are saved to
    csv files. This function should only be run once, when splitting among different team members.

    Args:
        ranges (dict): Dictionary of parameter ranges
        distinct_samples (int): Number of distinct samples to generate
        splits (int):  Number of splits to divide the samples into

    Returns:
        None
    """

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
    current_directory = os.path.dirname(os.path.realpath(__file__))

    # Go to parent directory
    parent_directory = current_directory.parent

    # Split dataframe
    for i in range(splits):
        # Check if folder does not exist
        if not os.path.exists(f"{parent_directory}/SensitivityAnalysis/split_{i + 1}"):
            os.mkdir(f"{parent_directory}/SensitivityAnalysis/split_{i + 1}")

        # Splitting into 5 files
        split_df = np.array_split(split_dfs[i], 5)

        # Save samples
        for j in range(5):
            split_df[j].to_csv(f"{parent_directory}/SensitivityAnalysis/split_{i + 1}/samples_{j + 1}.csv", index=False)


def run_model(file: str, replicates: int = 10, max_steps: int = 200) -> None:
    """
    Run the model for each sample in the file and save the results to a csv file.

    Args:
        file (str): File containing the samples
        replicates (int): Number of replicates to run
        max_steps (int): Maximum number of steps to run the model

    Returns:
        None
    """
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

                results.append(list(params.values()))
            pbar.update(1)

    # Get directory of file
    directory = "/".join(file.split("/")[:-1])

    # Get file number
    file_number = file.split("_")[-1].split(".")[0]

    # Create df
    df = pd.DataFrame(results, columns=list(params.keys()))

    # Save results
    df.to_csv(f"{directory}/results_{file_number}.csv", index=False)


def load_data(splits: int, path: str = "SensitivityAnalysis") -> pd.DataFrame:
    """
    Load all results from the different splits.

    Args:
        splits (int): Number of splits that have been simulated
        path (str): Path to the directory containing the splits

    Returns:
        pd.DataFrame: Dataframe containing all the results
    """
    # Get all directories
    directories = ["split_" + str(i) for i in range(1, splits + 1)]

    # Load all results
    results = pd.DataFrame()
    for directory in directories:
        files = os.listdir(f"{path}/{directory}")
        for file in files:
            if "results" in file:
                result = pd.read_csv(f"{path}/{directory}/{file}")
                results = pd.concat([results, result])

    # Reset index
    results = results.reset_index(drop=True)

    return results


def analyse(problem: dict, results: pd.DataFrame) -> tuple:
    """
    Perform sensitivity analysis using the Sobol method.

    Args:
        problem (dict): Problem definition as given in the SA-Lib documentation
        results (pd.DataFrame): Dataframe containing the results of the model runs

    Returns:
        tuple: Sensitivity indices for Gini and Trader Count

    """
    # Get Gini index and Trader count
    gini = results["Gini"]
    trader_count = results["Trader Count"]

    # Perform analysis
    Si_gini = sobol.analyze(problem, gini.values)
    Si_trader_count = sobol.analyze(problem, trader_count.values)

    return Si_gini, Si_trader_count


def plot_indices(Si_gini: pd.DataFrame, Si_trader_count: pd.DataFrame, problem: dict) -> tuple:
    """
    Plot the sensitivity indices for Gini and Trader Count.

    Args:
        Si_gini (pd.DataFrame): Sensitivity indices for Gini
        Si_trader_count (pd.DataFrame): Sensitivity indices for Trader Count
        problem (dict): Problem definition as given in the SA-Lib documentation

    Returns:
        tuple: Figure and Axes of the plots

    """
    # Create subplots
    fig, axs = plt.subplots(2, 2, figsize=(10, 10))

    # Get indices
    indices = ["S1", "ST"]

    # X-labels
    x_labels = problem["names"]
    ticks = range(len(x_labels))

    for i in range(2):
        # Plotting for gini
        axs[i, 0].plot(Si_gini[indices[i]], ticks, 'o', color='blue')
        axs[i, 0].errorbar(Si_gini[indices[i]], ticks, xerr=Si_gini[f"{indices[i]}_conf"],
                           capsize=1, fmt='o', color='black')
        axs[i, 0].set_title(f"Gini {indices[i]}")
        axs[i, 0].set_yticks(range(len(x_labels)))
        axs[i, 0].set_yticklabels(x_labels, rotation=45)

        # Plotting for trader count
        axs[i, 1].plot(Si_trader_count[indices[i]], ticks, 'o', color='blue')
        axs[i, 1].errorbar(Si_trader_count[indices[i]], ticks, xerr=Si_trader_count[f"{indices[i]}_conf"],
                           capsize=1, fmt='o', color='black')
        axs[i, 1].set_title(f"Trader Count {indices[i]}")
        axs[i, 1].set_yticks(range(len(x_labels)))
        axs[i, 1].set_yticklabels(x_labels, rotation=45)

        # Remove y-ticks for the right plot
        axs[i, 1].set_yticklabels([])

    fig.tight_layout()

    return fig, axs


if __name__ == "__main__":
    ranges = {
        "vision_mean": [1, 6],
        "metabolism_mean": [3, 9],
        "max_age_mean": [70, 100],
        "repopulate_factor": [5, 15],
        "cell_regeneration": [1, 5],
    }

    __save_samples(ranges, 1024, splits=8)
