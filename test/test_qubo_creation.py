import numpy as np
from railway_solvers import indexing4qubo, get_coupling, z_indices
from railway_solvers import get_z_coupling, penalty, P1qubic, P2qubic, Pcirc
from railway_solvers import Pswitch, Pspan, Pstay, P1track


####### testing particular QUBO element creation   ######



def test_pspan_pstay_p1track():

    """
                                          <- 2
    .............................................
    [ A ]                            . .    [ B ]
    ..................................c...........
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

    # default
    trains_paths = {
        "skip_station": {2: "A"},
        "Paths": {0: ["A", "B"], 1: ["A", "B"], 2: ["B", "A"]},
        "J": [0, 1, 2],
        "Jd": {"A": {"B": [[0, 1]]}, "B": {"A": [[2]]}},
        "Jtrack": {"B": [[0, 1]]}
    }

    inds, q_bits = indexing4qubo(trains_paths, 10)

    k = inds.index({'j': 0, 's': "A", 'd': 3})
    k1 = inds.index({'j': 1, 's': "A", 'd': 0})

    # test penalites for span and stay

    assert Pspan(trains_timing, k, k1, inds, trains_paths) == 0.
    assert Pspan(trains_timing, k1, k, inds, trains_paths) == 0.

    k = inds.index({'j': 0, 's': "A", 'd': 2})
    k1 = inds.index({'j': 1, 's': "A", 'd': 0})

    assert Pspan(trains_timing, k, k1, inds, trains_paths) == 1.
    assert Pspan(trains_timing, k1, k, inds, trains_paths) == 1.

    k = inds.index({'j': 0, 's': "A", 'd': 2})
    k1 = inds.index({'j': 0, 's': "B", 'd': 0})

    assert Pstay(trains_timing, k, k1, inds, trains_paths) == 1.
    assert Pstay(trains_timing, k1, k, inds, trains_paths) == 1.

    k = inds.index({'j': 0, 's': "A", 'd': 1})
    k1 = inds.index({'j': 0, 's': "B", 'd': 1})

    assert Pstay(trains_timing, k, k1, inds, trains_paths) == 0.
    assert Pstay(trains_timing, k1, k, inds, trains_paths) == 0.


    """
    1 ->                                    <- 2
    .............................................
    [ A ]                            . .    [ B ]
    ..................................c...........
    0 ->
    """

    trains_paths_r = {
        "skip_station": {2: "A"},
        "Paths": {0: ["A", "B"], 1: ["A", "B"], 2: ["B", "A"]},
        "J": [0, 1, 2],
        "Josingle": {("A", "B"): [[1,2]]},
        "Jtrack": {"B": [[0, 1]]}
    }

    # test penalties for deadlock

    k = inds.index({'j': 1, 's': "A", 'd': 0})
    k1 = inds.index({'j': 2, 's': "B", 'd': 0})

    assert P1track(trains_timing, k, k1, inds, trains_paths_r) == 1.
    assert P1track(trains_timing, k1, k, inds, trains_paths_r) == 1.

    k = inds.index({'j': 1, 's': "A", 'd': 6})
    k1 = inds.index({'j': 2, 's': "B", 'd': 0})

    assert P1track(trains_timing, k, k1, inds, trains_paths_r) == 1.
    assert P1track(trains_timing, k1, k, inds, trains_paths_r) == 1.

    k = inds.index({'j': 1, 's': "A", 'd': 10})
    k1 = inds.index({'j': 2, 's': "B", 'd': 0})

    assert P1track(trains_timing, k, k1, inds, trains_paths_r) == 1.
    assert P1track(trains_timing, k1, k, inds, trains_paths_r) == 1.

    k = inds.index({'j': 1, 's': "B", 'd': 1})
    k1 = inds.index({'j': 0, 's': "A", 'd': 2})

    assert P1track(trains_timing, k, k1, inds, trains_paths_r) == 0.
    assert P1track(trains_timing, k1, k, inds, trains_paths_r) == 0.

    k = inds.index({'j': 1, 's': "B", 'd': 0})
    k1 = inds.index({'j': 2, 's': "B", 'd': 1})

    assert P1track(trains_timing, k, k1, inds, trains_paths_r) == 0.
    assert P1track(trains_timing, k1, k, inds, trains_paths_r) == 0.


def test_pswith():

    """
    ..........                                .... <- 2 ..
    [ A ]     .                              .    [ B ]
    .. 1 -> .. c .......................... c ... .......

    swithes at A (1 out, 2 in) and B (1 in 12out )
    """

    taus = {"pass": {"1_A_B": 8, "2_B_A": 8}, "res": 1}


    trains_paths_r = {
        "skip_station": {2: "A"},
        "Paths": {1: ["A", "B"], 2: ["B", "A"]},
        "J": [1, 2],
        "Jd": dict(),
        "Josingle": {("A", "B"): [[1,2]]},
        "Jround": dict(),
        "Jtrack": dict(),
        "Jswitch": {"A": [{1: "out", 2: "in"}], "B": [{1: "in", 2: "out"}]}
    }

    trains_timing = {"tau": taus,
                 "initial_conditions": { "1_A": 1, "2_B": 8},
                 "penalty_weights": {"1_A": 1, "2_B": 1}}

    inds, q_bits = indexing4qubo(trains_paths_r, 10)

    k = inds.index({'j': 1, 's': "A", 'd': 0})
    k1 = inds.index({'j': 2, 's': "B", 'd': 0})

    assert Pswitch(trains_timing, k, k1, inds, trains_paths_r) == 0.
    assert Pswitch(trains_timing, k1, k, inds, trains_paths_r) == 0.

    k = inds.index({'j': 1, 's': "A", 'd': 0})
    k1 = inds.index({'j': 2, 's': "B", 'd': 2})

    assert Pswitch(trains_timing, k, k1, inds, trains_paths_r) == 0.
    assert Pswitch(trains_timing, k1, k, inds, trains_paths_r) == 0.

    k = inds.index({'j': 1, 's': "A", 'd': 0})
    k1 = inds.index({'j': 2, 's': "B", 'd': 1})

    assert Pswitch(trains_timing, k, k1, inds, trains_paths_r) == 1.
    assert Pswitch(trains_timing, k1, k, inds, trains_paths_r) == 1.

    k = inds.index({'j': 1, 's': "A", 'd': 5})
    k1 = inds.index({'j': 2, 's': "B", 'd': 6})

    assert Pswitch(trains_timing, k, k1, inds, trains_paths_r) == 1.
    assert Pswitch(trains_timing, k1, k, inds, trains_paths_r) == 1.


def test_rolling_stock_circulation():

    """
     [ A ]                                            [ B ]
    .....0 -> ......................................0 <-> 1......
    """

    trains_paths = {
        "Paths": {0: ["A", "B"], 1: ["B", "A"]},
        "J": [0, 1],
        "Jd": dict(),
        "Josingle": dict(),
        "Jround": {"B": [[0,1]]},
        "Jtrack": dict()
    }

    taus = {"pass": {"0_A_B": 4, "1_B_A": 8}, "prep": {"1_B": 2}}
    trains_timing = {"tau": taus,
                 "initial_conditions": {"0_A": 3, "1_B": 1},
                 "penalty_weights": {"0_A": 2, "1_B": 0.5}}

    inds, q_bits = indexing4qubo(trains_paths, 10)

    k = inds.index({'j': 0, 's': "A", 'd': 0})
    k1 = inds.index({'j': 1, 's': "B", 'd': 7})

    assert Pcirc(trains_timing, k, k1, inds, trains_paths) == 1.
    assert Pcirc(trains_timing, k1, k, inds, trains_paths) == 1.

    k = inds.index({'j': 0, 's': "A", 'd': 2})
    k1 = inds.index({'j': 1, 's': "B", 'd': 9})

    assert Pcirc(trains_timing, k, k1, inds, trains_paths) == 1.
    assert Pcirc(trains_timing, k1, k, inds, trains_paths) == 1.

    k = inds.index({'j': 0, 's': "A", 'd': 0})
    k1 = inds.index({'j': 1, 's': "B", 'd': 8})

    assert Pcirc(trains_timing, k, k1, inds, trains_paths) == 0.
    assert Pcirc(trains_timing, k1, k, inds, trains_paths) == 0.

    k = inds.index({'j': 0, 's': "A", 'd': 2})
    k1 = inds.index({'j': 1, 's': "B", 'd': 10})

    assert Pcirc(trains_timing, k, k1, inds, trains_paths) == 0.
    assert Pcirc(trains_timing, k1, k, inds, trains_paths) == 0.



def test_qubic():


    """
    1 ->                                    <- 2
    .............................................
    [ A ]                            . .    [ B ]
    ..................................c...........
    0 ->
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
        "Jd": dict(),
        "Josingle": {("A", "B"): [[1,2]]},
        "Jround": dict(),
        "Jtrack": {"B": [[0, 1]]}
    }

    inds, q_bits = indexing4qubo(trains_paths, 10)
    inds_z, l = z_indices(trains_paths, 10)

    assert l == 121

    inds1 = list(np.concatenate([inds, inds_z]))
    assert len(inds1) == 176

    k = inds1.index({'j': 0, 's': "A", 'd': 1})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': "B", 'd': 1, 'd1': 4})

    assert P1qubic(trains_timing, k, k1, inds1, trains_paths) == 0.
    assert P1qubic(trains_timing, k1, k, inds1, trains_paths) == 0.


    k = inds1.index({'j': 0, 's': "A", 'd': 1})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': "B", 'd': 4, 'd1': 1})

    assert P1qubic(trains_timing, k, k1, inds1, trains_paths) == 1.
    assert P1qubic(trains_timing, k1, k, inds1, trains_paths) == 1.

    k = inds1.index({'j': 1, 's': "A", 'd': 0})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': "B", 'd': 4, 'd1': 8})

    assert P1qubic(trains_timing, k, k1, inds1, trains_paths) == 1.
    assert P1qubic(trains_timing, k1, k, inds1, trains_paths) == 1.


    k = inds1.index({'j': 0, 'j1': 1, 's': "B", 'd': 4, 'd1': 1})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': "B", 'd': 4, 'd1': 2})

    assert P2qubic(k, k, inds1, trains_paths) == 3.
    assert P2qubic(k, k1, inds1, trains_paths) == 0.

    k = inds1.index({'j': 0, 's': "A", 'd': 10})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': "B", 'd': 4, 'd1': 8})

    assert P2qubic(k, k1, inds1, trains_paths) == 0.

    k = inds1.index({'j': 0, 's': "B", 'd': 10})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': "B", 'd': 10, 'd1': 8})

    assert P2qubic(k, k1, inds1, trains_paths) == -1.
    assert P2qubic(k1, k, inds1, trains_paths) == -1.

    k = inds1.index({'j': 0, 's': "B", 'd': 1})
    k1 = inds1.index({'j': 1, 's': "B", 'd': 0})

    assert P2qubic(k, k1, inds1, trains_paths) == 0.5
    assert P2qubic(k1, k, inds1, trains_paths) == 0.5

    k = inds1.index({'j': 0, 's': "B", 'd': 1})
    k1 = inds1.index({'j': 2, 's': "B", 'd': 0})

    assert P2qubic(k, k1, inds1, trains_paths) == 0.
    assert P2qubic(k1, k, inds1, trains_paths) == 0.

    k = inds1.index({'j': 0, 's': "A", 'd': 1})
    k1 = inds1.index({'j': 1, 's': "A", 'd': 0})

    assert P2qubic(k, k1, inds1, trains_paths) == 0.
    assert P2qubic(k1, k, inds1, trains_paths) == 0.

    k = inds1.index({'j': 0, 's': "B", 'd': 1})
    k1 = inds1.index({'j': 1, 's': "A", 'd': 0})

    assert P2qubic(k, k1, inds1, trains_paths) == 0.
    assert P2qubic(k1, k, inds1, trains_paths) == 0.


def test_penalties_and_couplings():

    """
                                          <- 2
    .............................................
    [ A ]                            . .    [ B ]
    ..................................c...........
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
        "Josingle": dict(),
        "Jround": dict(),
        "Jtrack": {"B": [[0, 1]]},
        "Jswitch": dict()
    }

    p_sum = 2.5
    p_pair = 1.25
    p_qubic = 2.1

    d_max = 10

    inds, q_bits = indexing4qubo(trains_paths, d_max)
    assert get_coupling(trains_timing, 0, 0, trains_paths,
                        inds, p_sum, p_pair) == -2.5
    assert get_coupling(trains_timing, 0, 24, trains_paths,
                        inds, p_sum, p_pair) == 1.25

    inds_z, l = z_indices(trains_paths, d_max)
    inds1 = list(np.concatenate([inds, inds_z]))

    k = inds1.index({'j': 1, 's': "A", 'd': 0})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': "B", 'd': 4, 'd1': 8})

    assert get_z_coupling(trains_timing, k, k1, trains_paths,
                          inds1, p_pair, p_qubic) == 1.25

    assert penalty(trains_timing, 1, inds, d_max) == 0.2
