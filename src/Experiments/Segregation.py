import matplotlib.pyplot as plt
import pandas as pd
from src.SugarScape import SugarScape
from mesa import batch_run
import numpy as np
from tqdm import tqdm
from src.Experiments.TaxEffect import __plot_boxplot


def extract_results(scenario: dict, batches: list, replicates: int, max_steps: int) -> tuple[list, list]:
    """
    Extract the results of the experiments.
    Args:
        scenario (dict): Dictionary containing the scenario.
        batches (list): List containing the batches of the experiments.
        replicates (int): Number of replicates.
        max_steps (int): Number of time steps to run the model for.

    Returns:
        tuple[list, list]: Tuple containing the results and the keys of the results.
    """

    # Initialize the results list
    results = []

    # Extracting the results
    for i in range(replicates):
        # Get sugar metabolisms
        scenario['lower_sugar'] = [float(batch["Lower Sugar Metabolism"]) for batch in
                                   batches[(max_steps + 1) * i:(max_steps + 1) * (i + 1)]]
        scenario["middle_sugar"] = [float(batch["Middle Sugar Metabolism"]) for batch in
                                    batches[(max_steps + 1) * i:(max_steps + 1) * (i + 1)]]
        scenario["upper_sugar"] = [float(batch["Upper Sugar Metabolism"]) for batch in
                                   batches[(max_steps + 1) * i:(max_steps + 1) * (i + 1)]]

        # Get spice metabolisms
        scenario["lower_spice"] = [float(batch["Lower Spice Metabolism"]) for batch in
                                   batches[(max_steps + 1) * i:(max_steps + 1) * (i + 1)]]
        scenario["middle_spice"] = [float(batch["Middle Spice Metabolism"]) for batch in
                                    batches[(max_steps + 1) * i:(max_steps + 1) * (i + 1)]]
        scenario["upper_spice"] = [float(batch["Upper Spice Metabolism"]) for batch in
                                   batches[(max_steps + 1) * i:(max_steps + 1) * (i + 1)]]

        # Get visions
        scenario["lower_vision"] = [float(batch["Lower Vision"]) for batch in
                                    batches[(max_steps + 1) * i:(max_steps + 1) * (i + 1)]]
        scenario["middle_vision"] = [float(batch["Middle Vision"]) for batch in
                                     batches[(max_steps + 1) * i:(max_steps + 1) * (i + 1)]]
        scenario["upper_vision"] = [float(batch["Upper Vision"]) for batch in
                                    batches[(max_steps + 1) * i:(max_steps + 1) * (i + 1)]]

        # Add to results
        results.append(list(scenario.values()))

    return results, list(scenario.keys())


def run_baseline(scenarios: dict, replicates: int = 10, max_steps: int = 200) -> pd.DataFrame:
    """
    Run the baseline scenarios for measuring segregation in the SugarScape model.
    Args:
        scenarios (dict): Dictionary containing the scenarios to be run.
        replicates (int): Number of replicates to be run for each scenario.
        max_steps (int): Number of time steps to run the model for.

    Returns:
        pd.DataFrame: DataFrame containing the results of the experiments.
    """

    # Initialize the results list
    results = []

    # Looping through scenarios
    with tqdm(total=len(scenarios)) as pbar:
        for scenario in scenarios.values():
            # Set map and tracking scheme
            scenario["map_scheme"] = "split"
            scenario["track_scheme"] = "segregation"

            # Run simulation
            batches = batch_run(SugarScape, scenario, number_processes=None, iterations=replicates, max_steps=max_steps,
                                display_progress=False, data_collection_period=1)

            # Extract results
            batch_results, keys = extract_results(scenario, batches, replicates, max_steps)
            results += batch_results

            # Update progress bar
            pbar.update(1)

    # Converting to DataFrame
    results = pd.DataFrame(results, columns=keys)

    return results


def run_experiments(scenarios: dict, tax_systems: list[tuple], tax_rates: list[float],
                    replicates: int = 10, max_steps: int = 200) -> pd.DataFrame:
    """
    Run the experiments for measuring segregation in the SugarScape model.

    Args:
        scenarios (dict): Dictionary containing the scenarios to be run.
        tax_systems (list[tuple]): List containing the tax systems to be run.
        tax_rates (list[float]): List containing the tax rates to be run.
        replicates (int): Number of replicates to be run for each scenario.
        max_steps (int): Number of time steps to run the model for.

    Returns:

    """
    # Initialize the results list
    results = []

    # Looping through scenarios
    n = len(scenarios) * len(tax_systems) * len(tax_rates)
    with tqdm(total=n) as pbar:
        for scenario in scenarios.values():
            for tax_system in tax_systems:
                for tax_rate in tax_rates:
                    # Create copy of scenario
                    scenario_copy = scenario.copy()

                    # Set tax system and rate
                    scenario_copy['tax_scheme'] = tax_system[0]
                    scenario_copy['distributer_scheme'] = tax_system[1]
                    scenario_copy['tax_rate'] = tax_rate

                    # Set map and tracking scheme
                    scenario_copy["map_scheme"] = "split"
                    scenario_copy["track_scheme"] = "segregation"

                    # Run simulation
                    batches = batch_run(SugarScape, scenario_copy, number_processes=None, iterations=replicates,
                                        max_steps=max_steps,
                                        display_progress=False, data_collection_period=1)

                    # Extract results
                    batch_results, keys = extract_results(scenario_copy, batches, replicates, max_steps)
                    results += batch_results

                    # Update progress bar
                    pbar.update(1)

    # Converting to DataFrame
    results = pd.DataFrame(results, columns=keys)

    return results


def mean_ci(base_results: pd.DataFrame, period: int = 20) -> dict:
    """
    Compute average over last period, and determine mean and ci of these values.
    Args:
        base_results (pd.DataFrame): DataFrame containing the results of the experiments.
        period (int): Number of time steps to compute the average over.

    Returns:
        dict: Dictionary containing the mean and confidence intervals of each variable.
    """
    # Get all positions and variables
    positions = ['lower', 'middle', 'upper']
    variables = ['sugar', 'spice', 'vision']

    # Dict to save results
    results = {}

    # Looping through each position
    for position in positions:
        # Looping through each variable
        for variable in variables:
            # Get values
            values = base_results[f'{position}_{variable}']

            # Converting to array
            values = np.vstack(values)

            # Get mean over last 20 steps
            mean = np.mean(values[:, -period:], axis=1)

            # Compute mean and confidence interval
            ci = 1.96 * np.std(mean, ddof=1) / np.sqrt(len(mean))
            mean = np.mean(mean)

            # Save results
            results[f'{position}_{variable}'] = (mean, ci)

    return results


def boxplots(results: pd.DataFrame, base_results: pd.DataFrame, period: int = 20) -> tuple[plt.Figure, plt.Axes]:
    """
    Create boxplots of the results.
    Args:
        results (pd.DataFrame): DataFrame containing the results of the experiments.
        base_results (pd.DataFrame): DataFrame containing the results of the baseline experiments.
        period (int): Number of time steps to compute the average over.
    """
    # Get all positions and variables
    positions = ['lower', 'middle', 'upper']
    variables = ['sugar', 'spice', 'vision']

    # Group by tax system
    grouped = results.groupby(['tax_scheme', 'distributer_scheme'])
    boxes = {}
    for tax_system, tax_groups in grouped:
        # Grouping based on tax_rate
        grouped_tax = tax_groups.groupby("tax_rate")
        for rate, rate_groups in grouped_tax:
            # Creating label for dict
            label = f"{tax_system[0]}-{tax_system[1]}-{rate * 100:.0f}%"

            # Looping through each position
            for position in positions:
                # Looping through each variable
                for variable in variables:
                    # Get values
                    values = rate_groups[f'{position}_{variable}']

                    # Converting to array
                    values = np.vstack(values)

                    # Get mean over last 20 steps
                    mean = np.mean(values[:, -period:], axis=1)

                    # Add to dict
                    var = f'{position}_{variable}'
                    if var not in boxes:
                        boxes[var] = {}
                    boxes[var][label] = mean

    # Get mean and ci of baseline
    base_results = mean_ci(base_results, period)

    # Create figure
    fig, axs = plt.subplots(3, 3, figsize=(15, 15))

    # Looping through each position
    for i, position in enumerate(positions):
        # Looping through each variable
        for j, variable in enumerate(variables):
            # Get variable
            var = f'{position}_{variable}'

            # Get mean and ci of current variable
            mean, ci = base_results[var]

            # Create boxplot
            ax = axs[i, j]
            __plot_boxplot(ax, boxes[var], mean, ci)

            # Set title
            suffix = 'Metabolism' if variable in ['sugar', 'spice'] else ''
            ax.set_title(f'{position.capitalize()} {variable.capitalize()} {suffix}')

            # Remove x-ticks if not the last row
            if i != 2:
                ax.set_xticklabels([])
            # Rotate x-ticks by 90 degrees
            else:
                ax.tick_params(axis='x', rotation=90)

    return fig, axs
