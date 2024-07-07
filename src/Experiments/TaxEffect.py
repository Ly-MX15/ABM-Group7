from typing import Any, Hashable
import pandas as pd
from mesa import batch_run
from src.SugarScape import SugarScape
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes


def __safe_eval(x: str) -> any:
    """
    Evaluate the string and return the result. Used for converting list of strings to list of values.

    Args:
        x (str): The string to evaluate

    Returns:
        any: The evaluated result
    """
    try:
        return eval(x)
    except:
        return x


def load_scenarios(file: str) -> dict:
    """
    Load the scenarios from the file

    Args:
        file (str): The file path

    Returns:
        dict: The scenarios in a dictionary format
    """
    # Load the scenarios from the file
    scenarios = pd.read_csv(file)

    # Converting to dictionary
    scenarios_dict = {}
    for i, row in scenarios.iterrows():
        scenario = row.iloc[0]
        # Without first column
        scenarios_dict[scenario] = row.iloc[1:].to_dict()

    return scenarios_dict


def run_baseline(scenarios: dict, map_scheme: str, replicates: int = 10, max_steps: int = 200) -> pd.DataFrame:
    """
    Run all the scenarios on the model without any tax effect.

    Args:
        scenarios (dict): Scenarios in a dictionary format
        map_scheme (str): The map scheme to use
        replicates (int): Number of replicates
        max_steps (int): Maximum number of steps to run the model

    Returns:
        None
    """
    results = []
    with tqdm(total=len(scenarios), ncols=90) as pbar:
        for scenario in scenarios.values():
            # Add map scheme
            scenario["map_scheme"] = map_scheme

            # Batch run
            batch = batch_run(SugarScape, scenario, number_processes=None,
                              iterations=replicates, max_steps=max_steps, display_progress=False,
                              data_collection_period=1)

            for i in range(replicates):
                scenario["Gini"] = [val['Gini'] for val in batch[(max_steps + 1) * i:(max_steps + 1) * (i + 1)]]
                scenario["Trader Count"] = [val['Trader Count'] for val in
                                            batch[(max_steps + 1) * i:(max_steps + 1) * (i + 1)]]
                results.append(list(scenario.values()))

            # Update progress bar
            pbar.update(1)

    # Convert to DataFrame
    columns = list(scenarios.values())[0].keys()
    df = pd.DataFrame(results, columns=columns)

    return df


def run_experiments(scenarios: dict, map_scheme: str, tax_systems: list[tuple], tax_rates: list[float],
                    replicates: int = 10, max_steps: int = 200) -> pd.DataFrame:
    """
    Run all the scenarios on the model with tax effect.

    Args:
        scenarios (dict): Scenarios in a dictionary format
        map_scheme (str): The map scheme to use
        tax_systems (list[tuple]): List of tax systems
        tax_rates (list[float]): List of tax rates
        replicates (int): Number of replicates
        max_steps (int): Maximum number of steps to run the model

    Returns:
        None
    """
    results = []
    n = len(scenarios) * len(tax_systems) * len(tax_rates)
    with tqdm(total=n, ncols=70) as pbar:
        for scenario in scenarios.values():
            for tax_system in tax_systems:
                for tax_rate in tax_rates:
                    # Create copy to save all results
                    scenario_copy = scenario.copy()

                    # Adding map scheme
                    scenario_copy["map_scheme"] = map_scheme

                    # Adding taxsystem and rate into scenario
                    scenario_copy["tax_scheme"] = tax_system[0]
                    scenario_copy["distributer_scheme"] = tax_system[1]
                    scenario_copy["tax_rate"] = tax_rate

                    # Run the model
                    batch = batch_run(SugarScape, scenario_copy, number_processes=None,
                                      iterations=replicates, max_steps=max_steps, display_progress=False,
                                      data_collection_period=1)

                    # Add results
                    for i in range(replicates):
                        scenario_copy["Gini"] = [val['Gini'] for val in
                                                 batch[(max_steps + 1) * i:(max_steps + 1) * (i + 1)]]
                        scenario_copy["Trader Count"] = [val['Trader Count'] for val in
                                                         batch[(max_steps + 1) * i:(max_steps + 1) * (i + 1)]]

                        results.append(list(scenario_copy.values()))

                    # Update progress bar
                    pbar.update(1)

    # Convert to DataFrame
    columns = list(scenario_copy.keys())
    df = pd.DataFrame(results, columns=columns)

    return df


def load_results(result: str, scenarios: dict) -> dict[str, pd.DataFrame]:
    """
    Load the results from the folder

    Args:
        result (str): The path to the results file as csv
        scenarios (dict): All scenarios in a dictionary format

    Returns:
        dict[str, pd.DataFrame]: The results in a dictionary format with scenario name as key and DataFrame as value
    """
    # Load results
    result = pd.read_csv(result)

    # Apply safe eval on each column to convert list of strings to list of values
    result = result.map(__safe_eval)

    # Create empty dict to store each scenario
    results = {}

    # Group by parameters
    parameters = list(scenarios.values())[0].keys()
    groups = result.groupby(list(parameters))

    # Adding each group to the results
    for name, group in groups:
        for scenario_name, scenario in scenarios.items():
            if all(scenario[key] == name[j] for j, key in enumerate(parameters)):
                results[scenario_name] = group.reset_index()
                break

    return results


def compute_mean(results: pd.DataFrame) -> dict[Hashable, dict[Any, Any]]:
    """
    Compute the mean and confidence interval of the results

    Args:
        results (pd.DataFrame): The results of one given scenario as DataFrame

    Returns: dict[Hashable, dict[Any, Any]]: The mean and confidence interval of the results. The dictionary is
    structured as follows: { "Tax Rate": { "Tax System": { "Variable": { "Mean": List[float], "CI": List[float] } } }
    """
    # Create empty dict to store the results
    tax_rate_dict = {}

    # Variables to compute the mean
    variables = ["Gini", "Trader Count"]

    # Group by tax rate
    rate_groups = results.groupby("tax_rate")
    for rate, values in rate_groups:
        # Create empty dict to store the results
        tax_rate_dict[rate] = {}

        # Group by tax system
        values = values.groupby(['tax_scheme', 'distributer_scheme'])
        for tax_system, system_values in values:
            # Convert tax_system to a proper label
            tax_scheme = tax_system[0].capitalize()
            distributer_scheme = tax_system[1].capitalize()
            tax_system = f"{tax_scheme}-{distributer_scheme}"

            # Create empty dict to store the results
            tax_rate_dict[rate][tax_system] = {}

            # Loop through each variable
            for variable in variables:
                # Converting into a numpy array
                var_values = np.vstack(system_values[variable])

                # Compute the mean and confidence interval
                mean = np.mean(var_values, axis=0)
                ci = 1.96 * np.std(var_values, ddof=1, axis=0) / np.sqrt(var_values.shape[0])

                # Adding to dict
                tax_rate_dict[rate][tax_system][variable] = {"mean": mean, "ci": ci}

    return tax_rate_dict


def time_series(results: pd.DataFrame) -> tuple:
    """
    Create time series plot for each variable and tax rate

    Args:
        results (pd.DataFrame): The results of one given scenario as DataFrame

    Returns:
        tuple: The figure and axes of the plot

    """

    # Create figure
    fig, axs = plt.subplots(3, 2, figsize=(10, 10))

    # Measured variables
    variables = ["Gini", "Trader Count"]

    # Get means of each tax rate + tax system
    tax_rate_dict = compute_mean(results)

    # Loop through each tax rate
    for i, tax_rate in enumerate(tax_rate_dict):
        # Looping through tax systems
        for tax_system in tax_rate_dict[tax_rate]:
            # Loop through each variable
            for j, variable in enumerate(variables):
                # Get the mean and confidence interval
                mean = tax_rate_dict[tax_rate][tax_system][variable]["mean"]
                ci = tax_rate_dict[tax_rate][tax_system][variable]["ci"]

                # Plotting
                axs[i, j].plot(mean, label=tax_system)
                axs[i, j].fill_between(range(len(mean)), mean - ci, mean + ci, alpha=0.5)

        # Adding grid
        axs[i, 0].grid()
        axs[i, 1].grid()

        # Add legend
        if i == 0:
            axs[i, 0].legend()
            axs[i, 1].legend()

        # Setting x-axis label and legend
        if i < 2:
            axs[i, 0].set_xticklabels([])
            axs[i, 1].set_xticklabels([])
        else:
            axs[i, 0].set_xlabel("Time")
            axs[i, 1].set_xlabel("Time")

        # Set y-axis label
        axs[i, 0].set_ylabel("Gini")
        axs[i, 1].set_ylabel("Trader Count")

        # Set titles
        axs[i, 0].set_title(f"Gini - {tax_rate * 100:.0f}%")
        axs[i, 1].set_title(f"Trader Count - {tax_rate * 100:.0f}%")

    return fig, axs


def base_period_mean(results: pd.DataFrame, period: int = 20) -> dict[str, dict[str, float]]:
    """
    Compute the mean of the last period for the base results.

    Args:
        results (pd.DataFrame): The results of one given scenario as DataFrame
        period (int): Period of time before last period to compute the mean

    Returns:
        dict: The mean and confidence interval of the results for the base scenario. The dictionary is structured as
        follows: { "Variable": { "Mean": float, "CI": float } }

    """

    # Dictionary to store the results
    base_results = {}

    # Variables
    variables = ["Gini", "Trader Count"]

    # Looping through variables
    for variable in variables:
        # Create array
        arr = np.vstack(results[variable])

        # Compute mean over last period
        mean = np.mean(arr[:, -period:], axis=1)

        # Compute ci and mean
        ci = 1.96 * np.std(mean, ddof=1) / np.sqrt(arr.shape[0])
        mean = np.mean(mean)

        # Adding to dict
        base_results[variable] = {"mean": mean, "ci": ci}

    return base_results


def period_mean(results: pd.DataFrame, period: int = 20) -> dict[str, dict[str, np.ndarray]]:
    """
    Compute the mean of the last period for each tax system and rate.

    Args:
        results (pd.DataFrame): The results of one given scenario as DataFrame
        period (int): Period of time before last period to compute the mean

    Returns:
        dict: The mean and confidence interval of the results for each tax system and rate. The dictionary is structured
        as follows: { "Variable": { "Tax System-Tax Rate": List[float] } }
    """
    # Variables
    variables = ["Gini", "Trader Count"]

    # Create dict to store the results
    period_results = {var: {} for var in variables}

    # Grouping by tax system
    groups = results.groupby(['tax_scheme', 'distributer_scheme'])
    for tax_system, group in groups:
        # Convert tax and distributer schemes
        tax_scheme = tax_system[0].capitalize()
        distributer_scheme = tax_system[1].capitalize()

        # Group by tax rate
        tax_groups = group.groupby('tax_rate')
        for tax_rate, tax_group in tax_groups:
            # Create label
            label = f"{tax_scheme}-{distributer_scheme}-{tax_rate * 100:.0f}%"

            # Looping through variables
            for variable in variables:
                # Create array
                arr = np.vstack(tax_group[variable])

                # Compute mean over last period
                mean = np.mean(arr[:, -period:], axis=1)

                # Adding to dict
                period_results[variable][label] = mean

    return period_results


def __plot_boxplot(ax: Axes, boxes: dict, mean: float, ci: float) -> Axes:
    """
    Plot the boxplot. Should only be used within the boxplots function.

    Args:
        ax (Axes): The axes to plot the boxplot
        boxes (dict): The boxes to plot
        mean (float): The mean of the boxes
        ci (float): The confidence interval of the boxes

    Returns:
        Axes: The axes with the boxplot
    """
    # Plotting
    box = ax.boxplot(boxes.values(), tick_labels=boxes.keys(), patch_artist=True)

    # Add base line
    ax.axhline(mean, color='r', linestyle='--', label='Base')
    ax.axhspan(mean + ci, mean - ci, color='r', alpha=0.5)

    # Set boxplot colors in groups of three
    colors = ['blue', 'green', 'purple', 'cyan', 'orange']
    for j, patch in enumerate(box['boxes']):
        color = colors[j // 3]
        patch.set_facecolor(color)

    # Set median bar color
    for median in box['medians']:
        median.set_color('black')

    return ax


def boxplot(results: dict, base_results: dict, map_scheme: str) -> dict[str, tuple[Any, Any]]:
    """
    Create box plots for each variable and tax rate
    Args:
        results (dict): The results of the experiments for each scenario
        base_results (dict): The results of the base scenario
        map_scheme (str): The map scheme used

    Returns:
        tuple: The figure and axes of the plot for both variables
    """
    # Variables
    variables = ["Gini", "Trader Count"]

    # Create empty dict to store the figures
    figs = {}
    for variable in variables:
        # Create figure
        fig, axs = plt.subplots(3, 2, figsize=(9, 10))
        axs = axs.flatten()

        # Adding to dict
        figs[variable] = (fig, axs)

    # Loop through scenarios
    for i, scenario_name in enumerate(results):
        # Get results and corresponding mean
        result = results[scenario_name]
        means = period_mean(result, 20)

        # Get base results and corresponding mean with ci
        base_result = base_results[scenario_name]
        mean_ci = base_period_mean(base_result, 20)

        # Loop through variables
        for variable in variables:
            # Get mean and ci of base
            base_mean = mean_ci[variable]["mean"]
            base_ci = mean_ci[variable]["ci"]

            # Get the axes
            ax = figs[variable][1][i]

            # Plot boxplot
            ax = __plot_boxplot(ax, means[variable], base_mean, base_ci)

            # Set title
            ax.set_title(scenario_name)

            # Remove x-ticklabels for all but last row
            if i < 4:
                ax.set_xticklabels([])
            else:
                # Rotate by 90 degrees
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=90)

    # Set tight layout and add suptitle
    for variable in variables:
        fig = figs[variable][0]
        fig.suptitle(f"{map_scheme.capitalize()} - {variable.capitalize()}")
        fig.tight_layout()

    return figs
