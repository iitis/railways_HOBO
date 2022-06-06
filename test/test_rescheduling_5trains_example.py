""" test on larger example with 5 trains and all scenarios """
import pytest
import numpy as np
from railway_solvers import make_Q, energy


def test_5_trains_all_Js():
    """
    21,22,23,24,25  - trains
    [A],[B],[C],[D] - stations
    -------         - tracks
    c               - switches
    and tracks: ----     .....

    22 <-> 23 means that 22 ends, and then starts back as 23
    (22 and 23 shares the same rolling stock)



       -21, 22, -> --- c ------------------ c --21 ->-- <-24--
       [  A   ]      [   B  ]         .  .  [   C      ]
       -------------------------<- 23--c ---- 22 <-> 23 ------
                                       .
                                       .
                                      .
          ---- 25-> - .              .
             [ D  ]    c -- <- 24 --
          ------------

    """

    taus = {
        "pass": {           # passing times of particular trains between stations
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
        # there are headways of combinations of trailns that may follow each others
        "stop": {"21_B": 1, "22_B": 1, "21_C": 1, "23_B": 1},
        "prep": {"23_C": 3}, # 22 termiantes at C, than it turns into 23, this is minimal preparation time
        "res": 1,
    }
    trains_timing = {
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

    trains_paths = {
        # departuring these stations by particular trains is not considered in the model
        "skip_station": {22: "C", 23: "A", 24: "D", 25: "C"},
        "Paths": {
            21: ["A", "B", "C"],
            22: ["A", "B", "C"],
            23: ["C", "B", "A"],
            24: ["C", "D"],
            25: ["D", "C"],
        },
        "J": [21, 22, 23, 24, 25], #set of trains
        "Jd": {"A": {"B": [[21, 22]]}, "B": {"C": [[21, 22]]}}, #trains following each other (headway)
        "Josingle": {("C", "D"): [[24, 25]]}, # trains heading in opossite direction on the single track line
        "Jround": {"C": [[22, 23]]},  # at C 22 ands and starts then as 23
        # trains that shares the same track at stations, note at C ,there are 2 such tracks
        "Jtrack": {"B": [[21, 22]], "C": [[21, 24], [22, 23]]},
        # trains that pasz through common swithes while enetering or leaving given station
        "Jswitch": {
            "B": [{21: "out", 22: "out"}, {21: "in", 22: "in"}],
            "C": [
                {23: "out", 24: "out"},
                {22: "in", 24: "out"},
                {22: "in", 23: "out"},
                {21: "in", 24: "out"},
            ],
            "D": [{24: "in", 25: "out"}],
        }
    }

    # parameters
    d_max = 10
    p_sum = 2.5
    p_pair = 1.25
    p_qubic = 2.1

    Q = make_Q(d_max, p_sum, p_pair, p_qubic, trains_timing, trains_paths
               )

    assert np.array_equal(Q, np.load("test/files/Qfile_5trains.npz")["Q"])


    # additional tests on already recorded solution form Hetropolis-Hastings
    sol = np.load("test/files/solution_5trains.npz")

    offset = -(2*3+1+2)*2.5
    objective = 1.01
    assert energy(sol, Q) == pytest.approx(offset + objective)
