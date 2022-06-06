""" test particular steps of QUBO creation """
import numpy as np
from railway_solvers import indexing4qubo, get_coupling, z_indices
from railway_solvers import get_z_coupling, penalty, P_rolling_stock_circulation
from railway_solvers import P_track_occupation_condition_quadratic_part, P_Rosenberg_decomposition
from railway_solvers import P_switch_occupation, P_headway, P_minimal_stay, P_single_track_line


def test_headway():

    """

    [ A ]                                  [ B ]
    ..............................................
    0 ->
    1 ->



    0, 1 - trains
    [A], [B] - stations
    -----    - line
    """

    taus = {"pass": {"0_A_B": 4, "1_A_B": 8},
            "headway": {"0_1_A_B": 2, "1_0_A_B": 6}
            }

    trains_timing = {"tau": taus,
                 "initial_conditions": {"0_A": 4, "1_A": 1}}


    trains_paths = {
        "Paths": {0: ["A", "B"], 1: ["A", "B"]},
        "J": [0, 1],
        "Jd": {"A": {"B": [[0, 1]]}}
    }

    inds, _ = indexing4qubo(trains_paths, 10)

    k = inds.index({'j': 0, 's': "A", 'd': 3})
    l = inds.index({'j': 1, 's': "A", 'd': 0})


    assert P_headway(k, l, inds, trains_timing, trains_paths) == 0.
    assert P_headway(l, k, inds, trains_timing, trains_paths) == 0.

    k = inds.index({'j': 0, 's': "A", 'd': 2})
    l = inds.index({'j': 1, 's': "A", 'd': 0})

    assert P_headway(k, l, inds, trains_timing, trains_paths) == 1.
    assert P_headway(l, k, inds, trains_timing, trains_paths) == 1.


def minimal_stay():


    """

    [ A ]                                  [ B ]
    ...............................................
    0 ->

    """

    taus = {"pass": {"0_A_B": 4}, "stop": {"0_B": 1}}

    trains_timing = {"tau": taus,
                 "initial_conditions": {"0_A": 4, "1_A": 1, "2_B": 8}}


    trains_paths = {
        "Paths": {0: ["A", "B"]},
        "J": [0],
        "Jd": {"A": {"B": [[0]]}}
    }

    inds, _ = indexing4qubo(trains_paths, 10)

    # can not make up delay by shortening the stay at "B"
    k = inds.index({'j': 0, 's': "A", 'd': 2})
    l = inds.index({'j': 0, 's': "B", 'd': 1})

    assert P_minimal_stay(k, l, inds, trains_timing, trains_paths) == 1.
    assert P_minimal_stay(l, k, inds, trains_timing, trains_paths) == 1.

    k = inds.index({'j': 0, 's': "A", 'd': 1})
    l = inds.index({'j': 0, 's': "B", 'd': 1})

    assert P_minimal_stay(k, l, inds, trains_timing, trains_paths) == 0.
    assert P_minimal_stay(l, k, inds, trains_timing, trains_paths) == 0.


def test_single_track_line():

    """
    1 ->                                    <- 2
    .............................................
    [ A ]                                   [ B ]

    """

    taus = {"pass": {"1_A_B": 8, "2_B_A": 8}, "stop": {"0_B": 1, "1_B": 1}}

    trains_timing = {"tau": taus, "initial_conditions": {"1_A": 1, "2_B": 8}}


    trains_paths_r = {
        "Paths": { 1: ["A", "B"], 2: ["B", "A"]},
        "J": [1, 2],
        "Josingle": {("A", "B"): [[1,2]]}
    }


    inds, _ = indexing4qubo(trains_paths_r, 10)


    k = inds.index({'j': 1, 's': "A", 'd': 0})
    l = inds.index({'j': 2, 's': "B", 'd': 0})

    assert P_single_track_line(k, l, inds, trains_timing, trains_paths_r) == 1.
    assert P_single_track_line(l, k, inds, trains_timing, trains_paths_r) == 1.

    k = inds.index({'j': 1, 's': "A", 'd': 6})
    l = inds.index({'j': 2, 's': "B", 'd': 0})

    assert P_single_track_line(k, l, inds, trains_timing, trains_paths_r) == 1.
    assert P_single_track_line(l, k, inds, trains_timing, trains_paths_r) == 1.

    k = inds.index({'j': 1, 's': "A", 'd': 10})
    l = inds.index({'j': 2, 's': "B", 'd': 0})

    assert P_single_track_line(k, l, inds, trains_timing, trains_paths_r) == 1.
    assert P_single_track_line(l, k, inds, trains_timing, trains_paths_r) == 1.


    k = inds.index({'j': 1, 's': "B", 'd': 0})
    l = inds.index({'j': 2, 's': "B", 'd': 1})

    assert P_single_track_line(k, l, inds, trains_timing, trains_paths_r) == 0.
    assert P_single_track_line(l, k, inds, trains_timing, trains_paths_r) == 0.


def test_switches():

    """
    ..........                                .... <- 2 ..
    [ A ]     .                              .    [ B ]
    .. 1 -> .. c .......................... c ... .......
                 ..........................

    swithes at A (1 out, 2 in) and B (1 in 12out )
    """

    taus = {"pass": {"1_A_B": 8, "2_B_A": 8}, "res": 1}


    trains_paths_r = {
        "Paths": {1: ["A", "B"], 2: ["B", "A"]},
        "J": [1, 2],
        "Jswitch": {"A": [{1: "out", 2: "in"}], "B": [{1: "in", 2: "out"}]}
    }

    trains_timing = {"tau": taus,
                 "initial_conditions": { "1_A": 1, "2_B": 8}}

    inds, _ = indexing4qubo(trains_paths_r, 10)

    k = inds.index({'j': 1, 's': "A", 'd': 0})
    l = inds.index({'j': 2, 's': "B", 'd': 0})

    assert P_switch_occupation(k, l, inds, trains_timing, trains_paths_r) == 0.
    assert P_switch_occupation(l, k, inds, trains_timing, trains_paths_r) == 0.

    k = inds.index({'j': 1, 's': "A", 'd': 0})
    l = inds.index({'j': 2, 's': "B", 'd': 2})

    assert P_switch_occupation(k, l, inds, trains_timing, trains_paths_r) == 0.
    assert P_switch_occupation(l, k, inds, trains_timing, trains_paths_r) == 0.

    k = inds.index({'j': 1, 's': "A", 'd': 0})
    l = inds.index({'j': 2, 's': "B", 'd': 1})

    assert P_switch_occupation(k, l, inds, trains_timing, trains_paths_r) == 1.
    assert P_switch_occupation(l, k, inds, trains_timing, trains_paths_r) == 1.

    k = inds.index({'j': 1, 's': "A", 'd': 5})
    l = inds.index({'j': 2, 's': "B", 'd': 6})

    assert P_switch_occupation(k, l, inds, trains_timing, trains_paths_r) == 1.
    assert P_switch_occupation(l, k, inds, trains_timing, trains_paths_r) == 1.


def test_rolling_stock_circ():

    """
     [ A ]                                            [ B ]
    .....0 -> ......................................0 <-> 1......
    """

    trains_paths = {
        "Paths": {0: ["A", "B"], 1: ["B", "A"]},
        "J": [0, 1],
        "Jround": {"B": [[0,1]]}
    }

    taus = {"pass": {"0_A_B": 4, "1_B_A": 8}, "prep": {"1_B": 2}}
    trains_timing = {"tau": taus,
                 "initial_conditions": {"0_A": 3, "1_B": 1}}


    inds, _ = indexing4qubo(trains_paths, 10)

    k = inds.index({'j': 0, 's': "A", 'd': 0})
    l = inds.index({'j': 1, 's': "B", 'd': 7})

    assert P_rolling_stock_circulation(k, l, inds, trains_timing, trains_paths) == 1.
    assert P_rolling_stock_circulation(l, k, inds, trains_timing, trains_paths) == 1.

    k = inds.index({'j': 0, 's': "A", 'd': 2})
    l = inds.index({'j': 1, 's': "B", 'd': 9})

    assert P_rolling_stock_circulation(k, l, inds, trains_timing, trains_paths) == 1.
    assert P_rolling_stock_circulation(l, k, inds, trains_timing, trains_paths) == 1.

    k = inds.index({'j': 0, 's': "A", 'd': 0})
    l = inds.index({'j': 1, 's': "B", 'd': 8})

    assert P_rolling_stock_circulation(k, l, inds, trains_timing, trains_paths) == 0.
    assert P_rolling_stock_circulation(l, k, inds, trains_timing, trains_paths) == 0.

    k = inds.index({'j': 0, 's': "A", 'd': 2})
    l = inds.index({'j': 1, 's': "B", 'd': 10})

    assert P_rolling_stock_circulation(k, l, inds, trains_timing, trains_paths) == 0.
    assert P_rolling_stock_circulation(l, k, inds, trains_timing, trains_paths) == 0.


def test_track_occupation():


    """
    1 ->
    .................................
    [ A ]                            .      [ B ]
    ......................................common track..
    0 ->
    """

    taus = {"pass": {"0_A_B": 4, "1_A_B": 8},
            "stop": {"0_B": 1, "1_B": 1}
            }

    trains_timing = {"tau": taus,
                 "initial_conditions": {"0_A": 4, "1_A": 1}}

    trains_paths = {
        "Paths": {0: ["A", "B"], 1: ["A", "B"]},
        "J": [0, 1],
        "Jround": {},  # have to check if the train does not colide with itself
        "Jtrack": {"B": [[0, 1]]}
    }

    inds, _ = indexing4qubo(trains_paths, 10)
    inds_z, l = z_indices(trains_paths, 10)

    inds1 = list(np.concatenate([inds, inds_z]))


    k = inds1.index({'j': 0, 's': "A", 'd': 1})
    l = inds1.index({'j': 0, 'j1': 1, 's': "B", 'd': 1, 'd1': 4})

    assert P_track_occupation_condition_quadratic_part(k, l, inds1, trains_timing, trains_paths) == 0.
    assert P_track_occupation_condition_quadratic_part(l, k, inds1, trains_timing, trains_paths) == 0.


    k = inds1.index({'j': 0, 's': "A", 'd': 1})
    l = inds1.index({'j': 0, 'j1': 1, 's': "B", 'd': 4, 'd1': 1})

    assert P_track_occupation_condition_quadratic_part(k, l, inds1, trains_timing, trains_paths) == 1.
    assert P_track_occupation_condition_quadratic_part(l, k, inds1, trains_timing, trains_paths) == 1.

    k = inds1.index({'j': 1, 's': "A", 'd': 0})
    l = inds1.index({'j': 0, 'j1': 1, 's': "B", 'd': 4, 'd1': 8})

    assert P_track_occupation_condition_quadratic_part(k, l, inds1, trains_timing, trains_paths) == 1.
    assert P_track_occupation_condition_quadratic_part(l, k, inds1, trains_timing, trains_paths) == 1.


    k = inds1.index({'j': 0, 'j1': 1, 's': "B", 'd': 4, 'd1': 1})
    l = inds1.index({'j': 0, 'j1': 1, 's': "B", 'd': 4, 'd1': 2})

    assert P_Rosenberg_decomposition(k, k, inds1, trains_paths) == 3.
    assert P_Rosenberg_decomposition(k, l, inds1, trains_paths) == 0.

    k = inds1.index({'j': 0, 's': "A", 'd': 10})
    l = inds1.index({'j': 0, 'j1': 1, 's': "B", 'd': 4, 'd1': 8})

    assert P_Rosenberg_decomposition(k, l, inds1, trains_paths) == 0.

    k = inds1.index({'j': 0, 's': "B", 'd': 10})
    l = inds1.index({'j': 0, 'j1': 1, 's': "B", 'd': 10, 'd1': 8})

    assert P_Rosenberg_decomposition(k, l, inds1, trains_paths) == -1.
    assert P_Rosenberg_decomposition(l, k, inds1, trains_paths) == -1.

    k = inds1.index({'j': 0, 's': "B", 'd': 1})
    l = inds1.index({'j': 1, 's': "B", 'd': 0})

    assert P_Rosenberg_decomposition(k, l, inds1, trains_paths) == 0.5
    assert P_Rosenberg_decomposition(l, k, inds1, trains_paths) == 0.5


    k = inds1.index({'j': 0, 's': "A", 'd': 1})
    l = inds1.index({'j': 1, 's': "A", 'd': 0})

    assert P_Rosenberg_decomposition(k, l, inds1, trains_paths) == 0.
    assert P_Rosenberg_decomposition(l, k, inds1, trains_paths) == 0.

    k = inds1.index({'j': 0, 's': "B", 'd': 1})
    l = inds1.index({'j': 1, 's': "A", 'd': 0})

    assert P_Rosenberg_decomposition(k, l, inds1, trains_paths) == 0.
    assert P_Rosenberg_decomposition(l, k, inds1, trains_paths) == 0.


def test_penalties_and_couplings():

    """
    we examine following example


                                          <- 2
    .............................................
    [ A ]                                   [ B ]
    ..............................................
    0 ->
    1 ->
    """

    taus = {"pass": {"0_A_B": 4, "1_A_B": 8, "2_B_A": 8},
            "headway": {"0_1_A_B": 2, "1_0_A_B": 6},
            "stop": {"0_B": 1, "1_B": 1},
            "res": 1
            }

    trains_timing = {"tau": taus,
                 "initial_conditions": {"0_A": 4, "1_A": 1, "2_B": 8},
                 "penalty_weights": {"0_A": 2, "1_A": 1, "2_B": 1}}


    trains_paths = {
        "skip_station": {2: "A"},
        "Paths": {0: ["A", "B"], 1: ["A", "B"], 2: ["B", "A"]},
        "J": [0, 1, 2],
        "Jd": {"A": {"B": [[0, 1]]}, "B": {"A": [[2]]}},
        "Josingle": {},
        "Jround": {},
        "Jtrack": {"B": [[0, 1]]},
        "Jswitch": {}
    }

    p_sum = 2.5
    p_pair = 1.25
    p_qubic = 2.1

    d_max = 10

    inds, _ = indexing4qubo(trains_paths, d_max)
    assert get_coupling(0, 0, inds, p_sum, p_pair,
                       trains_paths, trains_timing) == -2.5
    assert get_coupling(0, 24, inds, p_sum, p_pair,
                    trains_paths, trains_timing) == 1.25

    inds_z, l = z_indices(trains_paths, d_max)
    inds1 = list(np.concatenate([inds, inds_z]))

    k = inds1.index({'j': 1, 's': "A", 'd': 0})
    l = inds1.index({'j': 0, 'j1': 1, 's': "B", 'd': 4, 'd1': 8})

    assert get_z_coupling(k, l, inds1, p_pair, p_qubic, trains_timing, trains_paths) == 1.25

    assert penalty(1, inds, d_max, trains_timing) == 0.2
