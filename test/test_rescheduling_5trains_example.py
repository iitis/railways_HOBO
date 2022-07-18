""" test on larger example with 5 trains and all scenarios """
import pytest
import numpy as np
from railway_solvers import make_Qubo, energy


def test_5_trains_all_Js():
    """
    5 trains prolem
    """

    from inputs.DW_example import Problem_of_5_trains

    Q = make_Qubo(Problem_of_5_trains())

    assert np.array_equal(Q, np.load("test/files/Qfile_5trains.npz")["Q"])


    # additional tests on already recorded solution form Hetropolis-Hastings
    sol = np.load("test/files/solution_5trains.npz")

    offset = -(2*3+1+2)*2.5
    objective = 1.01
    assert energy(sol, Q) == pytest.approx(offset + objective)

    # feasibility check
    Problem_feasibility = Problem_of_5_trains(soft_constrains = False)

    Q_f = make_Qubo(Problem_feasibility)

    assert energy(sol, Q_f) == pytest.approx(offset)
