#!/usr/bin/env python3
""" proceeds data from DWave, prints timetable from results """
import pickle as pk
import os
import numpy as np
from railway_solvers import earliest_dep_time, indexing4qubo, make_Qubo, energy



def visualise_Qubo_solution(solution, Problem):
    """ visualise and pront timetable from the solution """
    trains_paths = Problem.trains_paths
    inds, q_bits = indexing4qubo(trains_paths, Problem.d_max)
    print("n.o. x vars", q_bits)
    print("n.o. all var", np.size(solution))

    for i in range(q_bits):
        if solution[i] == 1:
            j = inds[i]["j"]
            s = inds[i]["s"]
            d = inds[i]["d"]
            t = d + earliest_dep_time(trains_paths["Paths"], Problem.trains_timing, j, s)
            print("train", j, "station", s, "delay", d, "dep. time", t)
    print("--------------------------------------------------")


def load_train_solution(f, i):
    """ load particular DWave solution from file """
    file = open(
        f, 'rb')
    print("css", i)

    output = pk.load(file)
    solution = [sol[0] for sol in output]

    print("lowest energy")
    print("from file =", output[0][1])
    return solution


def method_marker(method):
    """ mark methods for output file"""
    if method == None:
        return ""
    if method == "rerouted":
        return "_r"
    if method == "enlarged":
        return "_e"
    if method == "5trains":
        return "_5t"


def no_feasible(solutions, Q_only_hard, offset):
    k = 0
    epsilon = 0.00001
    for solution in solutions:
        if energy(solution, Q_only_hard) <= offset + epsilon:
            k = k + 1
    return k

def analyseQ(Q):
    s = np.size(Q,0)
    k = 0
    for i in range(s):
        for j in range(i+1, s):
            if Q[i][j] != 0.:
                k = k+1

    print("n.o. qbits = ", s)
    print("n.o. connections = ", k)
    full = (s-1)*s/2
    print("n.o. connections, full graph", full)

    print("fraction of full graph", k/full)


def print_trains_timings(Problem_original, Q_only_hard, f_Q, method, offset):

    """ prints timetable """

    method_f = method_marker(method)

    print(" ##########   DW  results  ###################")
    Q = np.load(f_Q)["Q"]
    for i in [3, 3.5, 4, 4.5]:
        f = f"files/dwave_data/Qfile_samples_sol_real-anneal_numread3996_antime250_chainst{i}"+method_f
        solutions = load_train_solution(f, i)
        print("n.o. feasible =", no_feasible(solutions, Q_only_hard, offset))

        solution = solutions[0]
        print("from v Q vT = ", energy(solution, Q))
        visualise_Qubo_solution(solution, Problem_original)

    print(" #########  Hybrid  solver results ############ ")
    f = "files/hybrid_data/Qfile_samples_sol_hybrid-anneal"+method_f

    solutions = load_train_solution(f, "")

    print("n.o. feasible =", no_feasible(solutions, Q_only_hard, offset))

    solution = solutions[0]
    print("from v Q vT = ", energy(solution, Q))
    visualise_Qubo_solution(solution, Problem_original)



def save_Qmat(Problem, f):
    """ compute, analyse and save Qmat"""
    Q = make_Qubo(Problem)
    analyseQ(Q)
    if not os.path.isfile(f):
        print(f"save Q file to {f}")
        np.savez(f, Q=Q)



if __name__ == "__main__":

    #####   Q matrix generation #########

    from inputs.DW_example import DWave_problem, DWave_problem_enlarged, Problem_of_5_trains
    Problem_original = DWave_problem(rerouted = False)
    Problem_rerouted = DWave_problem(rerouted = True)
    Problem_enlarged= DWave_problem_enlarged()
    Problem_5trains = Problem_of_5_trains()

    f1_Q = 'files/Qfile.npz'
    f2_Q = 'files/Qfile_r.npz'
    f3_Q = 'files/Qfile_enlarged.npz'
    f4_Q = 'files/Qfile_5_trains.npz'

    print("original")
    save_Qmat(Problem_original, f1_Q)
    print("rerouted")
    save_Qmat(Problem_rerouted, f2_Q)
    print("enlarged")
    save_Qmat(Problem_enlarged, f3_Q)
    print("5trains")
    save_Qmat(Problem_5trains, f4_Q)

    print("  >>>>>>>>>>>>>>>>>  original problem  <<<<<<<<<<<<<<<<<<<")
    Problem_original_fesibility = DWave_problem(rerouted = False, soft_constrains = False)
    Q1 = make_Qubo(Problem_original_fesibility)
    print_trains_timings(Problem_original, Q1, f1_Q, None, offset = -12.5)

    print("  >>>>>>>>>>>>>>>>>  rerouted problem  <<<<<<<<<<<<<<<<<<<")
    Problem_rerouted_fesibility = DWave_problem(rerouted = True, soft_constrains = False)
    Q2 = make_Qubo(Problem_rerouted_fesibility)
    print_trains_timings(Problem_rerouted, Q2, f2_Q, "rerouted",  offset = -12.5)

    print("  >>>>>>>>>>>>>>>>>  enlarged problem  <<<<<<<<<<<<<<<<<<<")
    Problem_enlarged_fesibility = DWave_problem_enlarged(soft_constrains = False)
    Q3 = make_Qubo(Problem_enlarged_fesibility)
    print_trains_timings(Problem_enlarged, Q3, f3_Q, "enlarged",  offset = -15.0)


    print("  >>>>>>>>>>>>>>>>>  5 trains problem  <<<<<<<<<<<<<<<<<<<")
    Problem_5t_fesibility = Problem_of_5_trains(soft_constrains = False)
    Q4 = make_Qubo(Problem_5t_fesibility)
    print_trains_timings(Problem_5trains, Q4, f4_Q, "5trains",  offset = -(2*3+1+2)*2.5)
