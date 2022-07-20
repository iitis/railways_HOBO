# QUBO and HOBO of Railway Rescheduling for Quantum Computing

Source code utilized for Quadratic and Higher-Order Unconstrained Binary Optimization of Railway Rescheduling for Quantum Computing.

## Dependency installation

Anaconda distribution can be downloaded from [https://www.anaconda.com/products/individual](https://www.anaconda.com/products/individual). To install

```
conda env create -f rail-hobo.yml
```

To activate this environment, use
```
conda activate rail-hobo
```
To deactivate an active environment, use
```
conda deactivate
```

## Results reproduction

To reproduce the `Figure.[6]` and `Figure.[7]` in the article one need to run

```
python plot_DWave_results.py
```
the figures are saved in the `plots` folder.

## Generating new data

Generating data contains the following steps

### Generating Q-matrix:
To generate the `Q-matrix` one needs to run

```
python proceed_DWave_results.py
```

the matrix is saved on files for


(1) `files/Qfile.npz` for **default setting** and,
(2) `files/Qfile_r.npz` for **rerouted setting**,
(3) `files/Qfile_enlarged.npz` for **4 trains, 2 stations** model and,
(4) `files/Qfile_5_trains.npz` for **5 trains, 5 stations** model.

### Getting a solution:

To solve the Quadratic Unconstrained Binary Optimization problem on D-Wave's Advantage `QPU` and `hybrid solver` or `simulated annealer` one needs to do the following

```
python Qfile_solve.npy 'annealer_type' 'num_reads' 'annealing_time' 'method'
```

For more details on the solvers see: [https://www.dwavesys.com/media/m2xbmlhs/14-1048a-a_d-wave_hybrid_solver_service_plus_advantage_technology_update.pdf](https://www.dwavesys.com/media/m2xbmlhs/14-1048a-a_d-wave_hybrid_solver_service_plus_advantage_technology_update.pdf).
The `'method'` denotes the `model` we want to consider for solving. The available `models` are as follows

```
'default'  --> For default setting,
'rerouted' --> For rerouted setting,
'enlarged' --> For 4 trains, 2 stations setting,
'5trains'  --> For 5 trains, 5 stations setting.
```

The data produced in the paper using the following specifications


```
python Qfile_solve.npy 'simulated' 0 0 'default'
```
for **simulated annealer** with **default** model and

```
python Qfile_solve.npy 'quantum' 3996 250 'enlarged'
```
for **quantum annealer** with **4 trains, 2 stations** model and finally

```
python Qfile_solve.npy 'hybrid' 0 0 'rerouted'
```
for **hybrid solver** with **rerouted** model.

**NOTE:** For `'hybrid'` and `'simulated'` annealer the `annealing_time` and `num_reads` can be set arbitrarily.

## Saved Data

The newly generated data containing solution to the problem using the `hybrid solver` is saved in

```
files/hybrid_data
```
whereas the folder

```
files/dwave_data
```
contains the outcome for `quantum annealer`.

**NOTE:** For a particular `model` and for each annealing `run` two data files are saved in the following form

```
Qfile_complete.. --> Contains the whole D-Wave outcome, in the form of a dictionary,
Qfile_samples..  --> Contains just the solutions and corresponding energies, in the form of a list.
```

## Plotting

One can simply run the following code the generate and save the plot (similar to `Figure.[6]` and `Figure.[7]` in the article)

```
python plot_DWave_results.py
```

which are saved in `files/plots` folder.


## Timetable and output analysis

To get analysis of D-Wave output, and particular trains timetables run:

```
analyse_DWave_results.py
```

## Citing this work

K Domino, A Kundu, Ö Salehi, K Krawiec, Quadratic and Higher-Order Unconstrained Binary Optimization of Railway Rescheduling for Quantum Computing
https://arxiv.org/abs/2107.03234

The research was supported by:
- the Foundation for Polish Science (FNP) under grant number TEAM NET POIR.04.04.00-00-17C1/18-00
- the National Science Centre (NCN), Poland, under project number 2019/33/B/ST6/02011
