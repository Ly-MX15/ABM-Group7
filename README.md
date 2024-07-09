# SugarScape-Spice with Tax
This repository contains the code for the SugarScape with Spice model, which is an extension of the original SugarScape
model where agents only collect Sugar. In the SugarScape with Spice model, agents can collect both Sugar and Spice and
trade one resource for the other. The main goal of this model is to investigate wealth distribution among the agents. 
As an extension to this model, we have added a tax system where the agents have to pay a certain amount of their wealth
every set number of ticks. This tax system consists of two types of schemes: a taxing scheme and a distribution scheme.
The model has been implemented as an ABM using the MESA framework.

## Taxing Scheme
The taxing scheme determines how much tax an agent has to pay. The taxing scheme can be one of the following:
1. **Flat Tax**: Every agent has to pay a fixed amount of tax.
2. **Progressive Tax**: Agents are grouped into three tax brackets: low, middle, and high. Each tax bracket has a
different tax rate, with the low tax bracket having the lowest tax rate and the high tax bracket having the highest tax
3. **Regressive Tax**: Same as the progressive tax, but the tax rate is reversed, with the low tax bracket having the
highest tax rate and the high tax bracket having the lowest tax rate.
4. **Luxury Tax**: Agents are grouped into a luxury class and an average class. The luxury class has to pay a 
higher tax rate than the average class.

## Distribution Scheme
The distribution scheme determines how the tax collected is distributed. The distribution scheme can be one of 
the following:
1. **Flat Distribution**: The tax collected is distributed equally among all agents.
2. **Progressive Distribution**: The tax collected is distributed based on the wealth of the agents. Agents are grouped
into three wealth brackets: low, middle, and high. Each wealth bracket has a different distribution rate, with the low
wealth bracket receiving the highest distribution rate and the high wealth bracket receiving the lowest distribution rate.
3. **Needs-Based Distribution**: The tax collected is distributed based on the needs of the agents. Agents which are further
from their metabolic needs receive a higher distribution rate than agents which are closer to their metabolic needs.
4. **Random Distribution**: The tax collected is distributed randomly among all agents. A random agent is selected and
is given one sugar and one spice. This process is repeated until all the tax collected is distributed.

# Getting Started
Before we can start running the model, we need to install the required dependencies. Make sure that Python3 is installed
on your system, and has been added to the PATH. In the next section, we will setup a Virtual Environment and install the
required dependencies. This is not necessary, but it is recommended to avoid conflicts with other Python projects.

## Setting up the Virtual Environment
Virtual Environments are used to create isolated environments for Python projects. This ensures that the dependencies
installed for one project do not conflict with the dependencies of another project. Setup the Virtual Environment by
running the following commands in the terminal:
```bash
python3 -m venv .venv
```
This will create a new directory called `.venv` which will contain the Virtual Environment. Before we can install the 
packages, we need to activate the Virtual Environment. Depending on your system, the command to activate the Virtual
Environment will be different. Run the appropriate command from the list below:
### Windows
```bash
.venv\Scripts\activate
```

### MacOS/Linux
```bash
source .venv/bin/activate
```
Now that we have activated the Virtual Environment, we can install the required dependencies. Run the following command
to install the required dependencies:
```bash
pip install -r requirements.txt
```
This will install all the required dependencies for the project. Now that we have installed the dependencies, we can
start running the model. Again, it is not necessary to setup a Virtual Environment. Given that you don't want to setup
a Virtual Environment, you can skip the above steps and directly install the dependencies globally by using the above
command without setting up the Virtual Environment.

## Running the Model
After installing all the dependencies, we can start running the model. The model can be run by executing the following
command:
```bash
python3 server.py
```
This will launch a server, and open your web browser to the model's interface. If the browser does not open automatically,
then the model can be accessed by opening a web browser and navigating to `http://127.0.0.1:8488/`. The model can be
can be run with different parameters by adding arguments to the command. The available arguments are:
```
usage: server.py [-h] [--width WIDTH] [--height HEIGHT] [--initial_population INITIAL_POPULATION] 
[--metabolism_mean METABOLISM_MEAN] [--vision_mean VISION_MEAN] [--max_age_mean MAX_AGE_MEAN] [--tax_scheme TAX_SCHEME]
 [--tax_steps TAX_STEPS] [--tax_rate TAX_RATE] [--distributer_scheme DISTRIBUTER_SCHEME]
  [--distributer_steps DISTRIBUTER_STEPS] [--repopulate_factor REPPOPULATE_FACTOR] [--map_scheme MAP_SCHEME] 
  [--cell_regeneration CELL_REGENERATION]

options:
  -h, --help              show this help message and exit
  --width WIDTH           The width of the grid (default: 50)
  --height HEIGHT         The height of the grid (default: 50)
  --initial_population INITIAL_POPULATION
                          The number of traders to start with (default: 300)
  --metabolism_mean METABOLISM_MEAN
                          The mean metabolism for traders (default: 5)
  --vision_mean VISION_MEAN
                          The mean vision for traders (default: 3)
  --max_age_mean MAX_AGE_MEAN
                          The mean maximum age for traders (default: 85)
  --tax_scheme TAX_SCHEME The tax scheme to use (default: progressive)
  --tax_steps TAX_STEPS   The number of tax steps to use (default: 20)
  --tax_rate TAX_RATE     The tax rate to apply to all trades (default: 0.1)
  --distributer_scheme DISTRIBUTER_SCHEME
                          The distributer scheme to use (default: progressive)
  --distributer_steps DISTRIBUTER_STEPS
                          The number of distributer steps to use (default: 20)
  --repopulate_factor REPOPULATE_FACTOR
                          The factor used to determine when to repopulate traders (default: 10)
  --map_scheme MAP_SCHEME The scheme to use for generating the map (default: uniform)
  --cell_regeneration CELL_REGENERATION
                          The amount of sugar to regenerate in each cell (default: 1)


```
Some of the parameters take a string as an argument. The available options for these parameters are:
1. **tax_scheme**: flat, progressive, regressive, luxury
2. **distributer_scheme**: flat, progressive, needs, random
3. **map_scheme**: uniform, split, top_heavy

The tax system can also be disabled by setting the tax rate to 0. An example is given below with 100 initial traders, a flat tax scheme, and a flat (uniform) distribution scheme:
```bash
python3 server.py --initial_population 100 --tax_scheme flat --distributer_scheme flat
```

## Sensitivity Analysis
Before experimenting with the model, we need to perform a sensitivity analysis to determine the effect of the different
parameters on the model. We have taken the base model (no tax system) and determined the effect of the different
parameters on the model. The parameters that we have varied and their respective values are:
1. **vision_mean**: [1, 6]
2. **metabolism_mean**: [1, 6]
3. **max_age_mean**: [70, 100]
4. **repopulate_factor**: [5, 15]
5. **cell_regeneration**: [1, 5]

The Sobol Sensitivity Analysis was performed using the SALib library. The notebook **SensitivityAnalysis.ipynb** 
contains the code for the sensitivity analysis. The results of the sensitivity analysis are stored in the 
**SensitivityAnalysis** directory. The results are stored in the form of a CSV file, where each parameter value,
the Gini coefficient and the number of traders at the 200th tick are stored. The results are then visualized, with the
code also present in the notebook. The visualization is stored in the **SensitivityAnalysis** directory as
**indices.png**, visualizing the first and total order indices for each parameter.

## Experimentation with effects of Taxes on Wealth Distribution
After performing the sensitivity analysis, we have performed experiments to determine the effect of the different tax
systems with varying tax rates. We have created six different scenarios to determine the effect of the tax system under
different conditions. The scenarios are:
1. **Worst Case**: In this scenario, the ratio of Living agents and Gini is minimized.
2. **Best Case**: In this scenario, the ratio of Living agents and Gini is maximized.
3. **Typical Case**: In this scenario, the ratio of Living agents and Gini is close to the mean of the ratio of Living
agents and Gini ratio.
4. **Balanced Case**: In this scenario, the midpoint for each parameter is taken with the ranges used in the sensitivity
analysis.
5. **Slow Evolving**: In this scenario, the same parameters as the typical case are used, except for the max_age_mean and
repopulate_factor, which are maximized and minimized, respectively according to the sensitivity analysis.
6. **Fast Evolving**: In this scenario, the same parameters as the typical case are used, except for the max_age_mean and
repopulate_factor, which are minimized and maximized, respectively according to the sensitivity analysis.

The parameters for each scenario are stored within the **scenarios.csv** file. The code for the experiments is present in the **TaxEffect.ipynb** notebook. This notebook shows the code for running
the experiments and visualizing the results. The results of the experiments are stored in the **TaxEffect** directory. 
Another notebook has been created to perform analysis on the results, to determine if there is a significant difference
between the base model and the models with the tax system. The code for the analysis is present in the 
**TaxEffectAnalysis.ipynb** notebook. 

## Experimentation of segregation
The split map is a map scheme where the map is divided into two halves, with each half having a massive amount of one
resource and a small amount of the other resource. This map scheme can lead to segregation in terms of metabolic needs. 
We have studied the effect of tax systems on the segregation of agents on this map. The code for the experiments is 
present in the **Segregation.ipynb** notebook. 

# Extra Folders
There are two extra folders in the repository: **Presentation** and **Base Model Results - Report**. The **Presentation**
folder contains results for our presentation. The results and notebooks in this folder were created with an older version
of the model, possibly leading to different results. The **Base Model Results - Report** folder contains the results
of the base model presented in the report.
