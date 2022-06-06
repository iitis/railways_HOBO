#!/usr/bin/env python3

import pickle as pk
import numpy as np
import os
from railway_solvers import earliest_dep_time, indexing4qubo, make_Q, energy



def visualise_Qubo_solution(solution, trains_timing, trains_paths, d_max):
    inds, q_bits = indexing4qubo(trains_paths, d_max)
    print("n.o. x vars", q_bits)
    print("n.o. all var", np.size(solution))

    for i in range(q_bits):
        if solution[i] == 1:
            j = inds[i]["j"]
            s = inds[i]["s"]
            d = inds[i]["d"]
            t = d + earliest_dep_time(trains_paths["Paths"], trains_timing, j, s)
            print("train", j, "station", s, "delay", d, "dep. time", t)
    print("--------------------------------------------------")


def load_train_solution(f, i):
    """ load particular DWave solution from file """
    file = open(
        f, 'rb')
    print("css", i)

    output = pk.load(file)
    solution = output[0][0]
    print("lowest energy")
    print("from file =", output[0][1])
    return solution



def print_trains_timings():
    print("  >>>>>>>>>>>>>>>>>  original problem  <<<<<<<<<<<<<<<<<<<")

    print(" ##########   DW  results  ###################")
    Q = np.load("files/Qfile.npz")["Q"]
    for i in [3, 3.5, 4, 4.5]:
        f = f"files/dwave_data/Qfile_samples_sol_real-anneal_numread3996_antime250_chainst{i}"
        solution = load_train_solution(f, i)
        print("from v Q vT = ", energy(solution, Q))
        visualise_Qubo_solution(solution, trains_timing, trains_paths, d_max)

    print(" #########  Hybrid  solver results ############ ")
    f = "files/hybrid_data/Qfile_samples_sol_hybrid-anneal"
    solution = load_train_solution(f, "")
    print("from v Q vT = ", energy(solution, Q))
    visualise_Qubo_solution(solution, trains_timing, trains_paths, d_max)

    print("  >>>>>>>>>>>>>>>>>  rerouted problem  <<<<<<<<<<<<<<<<<<<")
    Q_r = np.load("files/Qfile_r.npz")["Q"]
    print(" ##########  DW  results retouted   ###################")
    for i in [3, 3.5, 4, 4.5]:
        f = f"files/dwave_data/Qfile_samples_sol_real-anneal_numread3996_antime250_chainst{i}_r"
        solution_r = load_train_solution(f, i)
        print("from v Q vT = ", energy(solution_r, Q_r))
        visualise_Qubo_solution(solution_r, trains_timing,
                                    trains_paths_rerouted, d_max)

    print(" ######### Hybrid  solver results rerouted ############ ")
    f = "files/hybrid_data/Qfile_samples_sol_hybrid-anneal_r"
    solution_r = load_train_solution(f, "")
    print("from v Q vT = ", energy(solution_r, Q_r))
    visualise_Qubo_solution(solution_r, trains_timing, trains_paths_rerouted, d_max)



####################  original problem ##########################



def save_Qmat(d_max, trains_paths, trains_timing, f):

    if not os.path.isfile(f):
        print(f"save Q file to {f}")
        p_sum = 2.5
        p_pair = 1.25
        p_qubic = 2.1

        Q = make_Q(d_max, p_sum, p_pair, p_qubic, trains_timing, trains_paths)

        np.savez(f, Q=Q)



if __name__ == "__main__":

    #####   Q matrix generation #########

    from inputs.DW_example import d_max, p_sum, p_pair, p_qubic, trains_timing, trains_paths, trains_paths_rerouted

    save_Qmat(d_max, trains_paths, trains_timing, 'files/Qfile.npz')
    save_Qmat(d_max, trains_paths_rerouted, trains_timing, 'files/Qfile_r.npz')

    print_trains_timings()
