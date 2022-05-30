import matplotlib.pyplot as plt
import numpy as np


def plotD_Wave(f, title, non_feasible_css, non_feasible_ens, feasible_css, feasible_ens, ground):

    plt.plot(non_feasible_css, non_feasible_ens, 'ro',
             label="not feasible DWave solution")
    plt.plot(feasible_css, feasible_ens, 'go',
             label="feasible and optimal DWave solution")
    plt.axhline(ground, color="green", label="ground state and hybrid solver")
    plt.ylabel('minimal energy')
    plt.xlabel('coupling strength')
    plt.title(title)
    plt.legend()
    plt.savefig(f)
    plt.clf()


# annealing time = 250 μs
# number of runs = 3996

# default setting

non_feasible_css = [3., 3.5, 4., 4.5]
non_feasible_ens = [-5.75, -5.15, -6.55, -4.95]
feasible_css = []
feasible_ens = []
ground = -7.4
title = "annealing t = 250 μs, 3996 runs, default"

plotD_Wave("plots/DW_default.pdf", title, non_feasible_css,
           non_feasible_ens, feasible_css, feasible_ens, ground)


# rerouting

non_feasible_css = [3., 3.5, 4.]
non_feasible_ens = [-8.05, -7.7, -8.35]
feasible_css = [4.5]
feasible_ens = [-9.6]
ground = -10.1

title = "annealing t = 250 μs, 3996 runs, rerouting"

plotD_Wave("plots/DW_rerouting.pdf", title, non_feasible_css,
           non_feasible_ens, feasible_css, feasible_ens, ground)
