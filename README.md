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

To reproduce the `Figure.[6]` in the article one need to run

```
python plot_DWave_results.py
```
the figures are saved in the `plots` folder.

## Generating new data

Generating data basically constains the following steps

### Generating Q-matrix:
To generate the `Q-matrix` one need to run

```
python proceed_DWave_results.py
```

the matrix is saved on files for 


(1) `files/Qfile.npz` for **default setting** and,
(2) `files/Qfile_r.npz` for **rerouted setting**.

### Getting a solution:

To solve the Quadratic Unconstrained Binary Optimization problem on D-Wave's Advantage `QPU` and `hybrid solver` or `simulated annealer` one need to do the following

```
python Qfile_solve.npy 'annealer_type' 'num_reads' 'annealing_time'
```

For more details on the solvers see: [https://www.dwavesys.com/media/m2xbmlhs/14-1048a-a_d-wave_hybrid_solver_service_plus_advantage_technology_update.pdf](https://www.dwavesys.com/media/m2xbmlhs/14-1048a-a_d-wave_hybrid_solver_service_plus_advantage_technology_update.pdf). The data produced in the paper using the following specifications


```
python Qfile_solve.npy 'simulated' 3996 250
```
for **simulated annealer** and 

```
python Qfile_solve.npy 'quantum' 3996 250
```
for **quantum annealer** and finally

```
python Qfile_solve.npy 'hybrid' 3996 250
```
for **hybrid solver**.

## Saved Data

The newly generated data containing solution to the problem using the `hybrid solver` is saved in

```
files/hybrid_data
```
whereas the folder

```
files/dwave_data
```
constains the outcome for `simulated` and `quantum annealer`.

## Plotting

One can simply run the follwing code the generate and save the plot (similar to `Figure.[6]` in the article)

```
python plot_DWave_results.py
```

which are saved in `files/plots` folder.