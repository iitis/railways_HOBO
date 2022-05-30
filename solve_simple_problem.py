#!/usr/bin/env python3

import pickle as pk
import numpy as np
from railway_solvers import earliest_dep_time, indexing4qubo, make_Q
import os
Q_file_exists = os.path.isdir('files/Qfile.npz')


def energy(v, Q):
    if -1 in v:
        v = [(y + 1) / 2 for y in v]
    X = np.matrix(Q)
    V = np.matrix(v)
    return V * X * V.transpose()


def visualise_Qubo_solution(solution, timetable, train_sets, d_max):
    inds, q_bits = indexing4qubo(train_sets, d_max)
    l = q_bits
    print("x vars", l)
    print("all var", np.size(Q[0]))

    S = train_sets["Paths"]
    for i in range(l):
        if solution[i] == 1:
            j = inds[i]["j"]
            s = inds[i]["s"]
            d = inds[i]["d"]
            t = d + earliest_dep_time(S, timetable, j, s)
            print("train", j, "station", s, "delay", d, "time", t)


"""
                                        <- 2
...............................................
 [ A ]                             .   .   [ B ]
.....................................c.........
0 ->
1 ->
"""

taus = {"pass": {"0_A_B": 4, "1_A_B": 8, "2_B_A": 8},
        "headway": {"0_1_A_B": 2, "1_0_A_B": 6},
        "stop": {"0_B": 1, "1_B": 1},
        "res": 1
        }

timetable = {"tau": taus,
             "initial_conditions": {"0_A": 4, "1_A": 1, "2_B": 8},
             "penalty_weights": {"0_A": 2, "1_A": 1, "2_B": 1}}

d_max = 10

train_sets = {
    "skip_station": {
        2: "A",  # we do not count train 2 leaving A
    },
    "Paths": {0: ["A", "B"], 1: ["A", "B"], 2: ["B", "A"]},
    "J": [0, 1, 2],
    "Jd": {"A": {"B": [[0, 1]]}, "B": {"A": [[2]]}},
    "Josingle": dict(),
    "Jround": dict(),
    "Jtrack": {"B": [[0, 1]]},
    "Jswitch": dict(),
    "add_swithes_at_s": ["B"]
}

#rerouting

"""
1 ->                                       <- 2
...............................................
 [ A ]                             .   .  [ B ]
.....................................c.........
0 ->
"""


train_sets_rerouted = {
    "skip_station": {
        2: "A",
    },
    "Paths": {0: ["A", "B"], 1: ["A", "B"], 2: ["B", "A"]},
    "J": [0, 1, 2],
    "Jd": dict(),
    "Josingle": {("A", "B"): [[1,2]]},
    "Jround": dict(),
    "Jtrack": {"B": [[0, 1]]},
    "Jswitch": {"A": [{1:"out", 2:"in"}], "B": [{1:"in", 2:"out"}]},
    "add_swithes_at_s": ["B"]
}

d_max = 10


#####   Q matrix generation #########

if Q_file_exists == False:
    p_sum = 2.5
    p_pair = 1.25
    p_pair_qubic = 1.25
    p_qubic = 2.1

    Q = make_Q(train_sets, timetable, d_max, p_sum,
               p_pair, p_pair_qubic, p_qubic)
    print(np.sqrt(np.size(Q)))

    np.savez("files/Qfile.npz", Q=Q)
    Q = make_Q(train_sets_rerouted, timetable, d_max,
               p_sum, p_pair, p_pair_qubic, p_qubic)
    np.savez("files/Qfile_r.npz", Q=Q)

#####  D-Wave output   ######

if True:
    for i in [3, 3.5, 4, 4.5]:
        file = open(
            "files/dwave_data/Qfile_samples_sol_real-anneal_numread3996_antime250_chainst" + str(i), 'rb')
        print("css", i)

        x = pk.load(file)
        solution = x[0][0]
        print(x[0][1])

        Q = np.load("files/Qfile.npz")["Q"]
        print("default setting")
        print("ground energy", energy(solution, Q))
        visualise_Qubo_solution(solution, timetable, train_sets, d_max)
    print(" ##########   done  DW  results  ###################")

#####  D-Wave output rerouted ######

if True:
    for i in [3, 3.5, 4, 4.5]:
        file = open(
            f"files/dwave_data/Qfile_samples_sol_real-anneal_numread3996_antime250_chainst{i}_r", 'rb')
        print("css", i)

        x = pk.load(file)
        solution_r = x[0][0]
        Q_r = np.load("files/Qfile_r.npz")["Q"]
        print("rerouting")
        print("ground energy", energy(solution_r, Q_r))
        visualise_Qubo_solution(solution_r, timetable,
                                train_sets_rerouted, d_max)
    print(" ##########   done  DW  retouted results  ###################")

#####  D-Wave hybrid solver ######

if True:
    file = open("files/hybrid_data/Qfile_samples_sol_hybrid-anneal", 'rb')
    x = pk.load(file)
    solution = x[0][0]
    print(x[0][1])

    Q = np.load("files/Qfile.npz")["Q"]
    print("default setting")
    print("ground energy", energy(solution, Q))

    visualise_Qubo_solution(solution, timetable, train_sets, d_max)
    file = open("files/hybrid_data/Qfile_samples_sol_hybrid-anneal_r", 'rb')
    x = pk.load(file)
    solution_r = x[0][0]
    Q_r = np.load("files/Qfile_r.npz")["Q"]
    print("rerouting setting")
    print("ground energy", energy(solution_r, Q_r))
    visualise_Qubo_solution(solution_r, timetable, train_sets_rerouted, d_max)

    print(" ######### done  Hybrid  results ############ ")
