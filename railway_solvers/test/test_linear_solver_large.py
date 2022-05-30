import pytest

from railway_solvers import *


def energy(v, Q):
    if -1 in v:
        v = [(y + 1) / 2 for y in v]
    X = np.array(Q)
    V = np.array(v)
    return V @ X @ V.transpose()


def test_5_trains_all_cases():
    """
    We have the following trains: 21,22,23,24,25
    and stations: A,B,C,D    [  ] - corresponds to the platform
    and tracks: ----     .....

    the way trains go ->
    22 <-> 23 means that 22 ends, and then starts back as 23
    (rolling stock circ)

    the example sitation map is following:



       -21, 22, -> --------------------------21 ->-- <-24--
       [  A   ]        [ B  ]         .   .       [ C ]
       -------------------------<- 23--c ---- 22 <-> 23 ---
                                      .
          . -- 25-> - .             .
      --- .  [ D  ]   . ----<- 24---
            .........

    """

    taus = {
        "pass": {
            "21_A_B": 4,
            "22_A_B": 8,
            "21_B_C": 4,
            "22_B_C": 8,
            "23_C_B": 6,
            "23_B_A": 6,
            "24_C_D": 3,
            "25_D_C": 3,
        },
        "headway": {"21_22_A_B": 2, "22_21_A_B": 6, "21_22_B_C": 2, "22_21_B_C": 6},
        "stop": {"21_B": 1, "22_B": 1, "21_C": 1, "23_B": 1},
        "prep": {"23_C": 3},
        "res": 1,
    }
    timetable = {
        "tau": taus,
        "initial_conditions": {
            "21_A": 6,
            "22_A": 1,
            "23_C": 26,
            "24_C": 25,
            "25_D": 28,
        },
        "penalty_weights": {
            "21_B": 2,
            "22_B": 0.5,
            "21_A": 2,
            "22_A": 0.5,
            "23_B": 0.8,
            "24_C": 0.5,
            "25_D": 0.5,
        },
    }

    train_sets = {
        "skip_station": {22: "C", 23: "A", 24: "D", 25: "C"},
        "Paths": {
            21: ["A", "B", "C"],
            22: ["A", "B", "C"],
            23: ["C", "B", "A"],
            24: ["C", "D"],
            25: ["D", "C"],
        },
        "J": [21, 22, 23, 24, 25],
        "Jd": {"A": {"B": [[21, 22]]}, "B": {"C": [[21, 22]]}},
        "Josingle": {("C", "D"): [[24, 25]]},
        "Jround": {"C": [[22, 23]]},
        "Jtrack": {"B": [[21, 22]], "C": [[21, 24], [22, 23]]},
        "Jswitch": {
            "B": [{21: "out", 22: "out"}, {21: "in", 22: "in"}],
            "C": [
                {23: "out", 24: "out"},
                {22: "in", 24: "out"},
                {22: "in", 23: "out"},
                {21: "in", 24: "out"},
            ],
            "D": [{24: "in", 25: "out"}],
        },
        "add_swithes_at_s": []  # it adss automatically swithes at stations in
        # bracket if two trains are in "Jtrack"
        # if empty or no performs no action
    }

    d_max = 10


    p_sum = 2.5
    p_pair = 1.25
    p_pair_qubic = 1.25
    p_qubic = 2.1

    Q = make_Q(train_sets, timetable, d_max, p_sum, p_pair, p_pair_qubic,
               p_qubic
               )

    # np.savez("test/files/Qfile_5trains.npz", Q=Q)

    sol = np.load("test/files/solution_5trains.npz")

    # offset = (2*3+1+2)*2.5 = -22.5

    assert energy(sol, Q) == pytest.approx(-22.5 + 1.01)
