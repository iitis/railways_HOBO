#!/usr/bin/env python3

import pickle as pk
import numpy as np
from railway_solvers import earliest_dep_time, indexing4qubo, make_Q, energy
import os


def visualise_Qubo_solution(solution, timetable, train_sets, d_max):
    inds, q_bits = indexing4qubo(train_sets, d_max)
    l = q_bits
    print("n.o. x vars", l)
    print("n.o. all var", np.size(solution))

    S = train_sets["Paths"]
    for i in range(l):
        if solution[i] == 1:
            j = inds[i]["j"]
            s = inds[i]["s"]
            d = inds[i]["d"]
            t = d + earliest_dep_time(S, timetable, j, s)
            print("train", j, "station", s, "delay", d, "dep. time", t)
    print("--------------------------------------------------")


def load_train_solution(f, i):
    """ load particular DWave solution from file """
    file = open(
        f, 'rb')
    print("css", i)

    x = pk.load(file)
    solution = x[0][0]
    print("lowest energy")
    print("from file =", x[0][1])
    return solution



def print_timetables():
    print("  >>>>>>>>>>>>>>>>>  original problem  <<<<<<<<<<<<<<<<<<<")

    print(" ##########   DW  results  ###################")
    Q = np.load("files/Qfile.npz")["Q"]
    for i in [3, 3.5, 4, 4.5]:
        solution = load_train_solution(f"files/dwave_data/Qfile_samples_sol_real-anneal_numread3996_antime250_chainst{i}", i)
        print("from v Q vT = ", energy(solution, Q))
        visualise_Qubo_solution(solution, timetable, train_sets, d_max)

    print(" #########  Hybrid  solver results ############ ")
    solution = load_train_solution("files/hybrid_data/Qfile_samples_sol_hybrid-anneal", "")
    print("from v Q vT = ", energy(solution, Q))
    visualise_Qubo_solution(solution, timetable, train_sets, d_max)

    print("  >>>>>>>>>>>>>>>>>  rerouted problem  <<<<<<<<<<<<<<<<<<<")
    Q_r = np.load("files/Qfile_r.npz")["Q"]
    print(" ##########  DW  results retouted   ###################")
    for i in [3, 3.5, 4, 4.5]:
        solution_r = load_train_solution(f"files/dwave_data/Qfile_samples_sol_real-anneal_numread3996_antime250_chainst{i}_r", i)
        print("from v Q vT = ", energy(solution_r, Q_r))
        visualise_Qubo_solution(solution_r, timetable,
                                    train_sets_rerouted, d_max)

    print(" ######### Hybrid  solver results rerouted ############ ")
    solution_r = load_train_solution("files/hybrid_data/Qfile_samples_sol_hybrid-anneal_r", "")
    print("from v Q vT = ", energy(solution_r, Q_r))
    visualise_Qubo_solution(solution_r, timetable, train_sets_rerouted, d_max)



####################  original problem ##########################

"""
                                            <- j3
    ..........c........................c....c......
     [ S1 ] .  .                        .  .   [ S2 ]
    .......c....c........................c.........
    j1 ->
    j2 ->


    S1, S2 - stations
    j1, j2, j3 - trains
    .....  - track
    c - switch
"""

taus = {"pass": {"j1_S1_S2": 4, "j2_S1_S2": 8, "j3_S2_S1": 8},
        "headway": {"j1_j2_S1_S2": 2, "j2_j1_S1_S2": 6},
        "stop": {"j1_S2": 1, "j2_S2": 1},
        "res": 1
        }

timetable = {"tau": taus,
             "initial_conditions": {"j1_S1": 4, "j2_S1": 1, "j3_S2": 8},
             "penalty_weights": {"j1_S1": 2, "j2_S1": 1, "j3_S2": 1}}

d_max = 10

train_sets = {
    "skip_station": {
        "j3": "S1",  # we do not count train j3 leaving S1
    },
    "Paths": {"j1": ["S1", "S2"], "j2": ["S1", "S2"], "j3": ["S2", "S1"]},
    "J": ["j1", "j2", "j3"],
    "Jd": {"S1": {"S2": [["j1", "j2"]]}, "S2": {"S1": [["j3"]]}},
    "Josingle": dict(),
    "Jround": dict(),
    "Jtrack": {"S2": [["j1", "j2"]]},
    "Jswitch": dict(),
    "add_swithes_at_s": ["S2"]  # additional τ(res.)(j, "B") in Eq. 18
}

##########################   rerouted problem  #########################

"""
    j2 ->                                      <- j3
    ...........c.......................c...c.......
     [ S1 ]  .  .                       . .    [ S2 ]
    .........c...c.......................c.........
    j1 ->


"""


train_sets_rerouted = {
    "skip_station": {
        "j3": "S1",  # we do not count train j3 leaving S1
    },
    "Paths": {"j1": ["S1", "S2"], "j2": ["S1", "S2"], "j3": ["S2", "S1"]},
    "J": ["j1", "j2", "j3"],
    "Jd": dict(),
    "Josingle": {("S1", "S2"): [["j2", "j3"]]},
    "Jround": dict(),
    "Jtrack": {"S2": [["j1", "j2"]]},
    "Jswitch": {"S1": [{"j2":"out", "j3":"in"}], "S2": [{"j2":"in", "j3":"out"}]}, # swithes from the single track line
    "add_swithes_at_s": ["S2"]  # additional τ(res.)(j, "B") in Eq. 18 to I track on the station
}

d_max = 10


#####  D-Wave output   ######


def save_Qmat(train_sets, timetable, d_max, f):

    if not os.path.isfile(f):
        print(f"save Q file to {f}")
        p_sum = 2.5
        p_pair = 1.25
        p_qubic = 2.1

        Q = make_Q(train_sets, timetable, d_max, p_sum,
                   p_pair, p_pair, p_qubic)

        np.savez(f, Q=Q)



if __name__ == "__main__":

    #####   Q matrix generation #########

    save_Qmat(train_sets, timetable, d_max, 'files/Qfile.npz')
    save_Qmat(train_sets_rerouted, timetable, d_max, 'files/Qfile_r.npz')

    print_timetables()
