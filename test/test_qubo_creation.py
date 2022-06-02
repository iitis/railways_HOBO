import numpy as np
from railway_solvers import make_Q, energy, indexing4qubo, get_coupling, z_indices
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


def test_minimal_span_two_trains():

    """
    two trains, 0 and 1 are going one way A -> B test minimal span

        A                            B
     1 ->
     0 ->  --------------------------
    """


    taus = {"pass": {"0_A_B": 4, "1_A_B": 8},
            "headway": {"0_1_A_B": 2, "1_0_A_B": 6},
            "stop": {"0_B": 1, "1_B": 1}, "res": 1}
    trains_timing_1 = {"tau": taus,
                 "initial_conditions": {"0_A": 3, "1_A": 1},
                 "penalty_weights": {"0_A": 2, "1_A": 0.5}}

    trains_paths = {
        "Paths": {0: ["A", "B"], 1: ["A", "B"]},
        "J": [0, 1],
        "Jd": {"A": {"B": [[0, 1]]}},
        "Josingle": dict(),
        "Jround": dict(),
        "Jtrack": dict(),
        "Jswitch": dict()
    }

    p_sum = 2
    p_pair = 1.
    p_qubic = 2.
    d_max = 5

    Q = make_Q(trains_paths, trains_timing_1, d_max, p_sum,
               p_pair, p_pair, p_qubic)

    assert np.array_equal(Q, np.load("test/files/Qfile_one_way.npz")["Q"])

    sol = np.load("test/files/solution_one_way.npz")

    assert energy(sol, Q) == -8+0.4


def  test_station_track_and_switches_two_trains():
    """
    Test single track at station and swithes constrain, switches simplified

    swith - c

    tracks - ......


                                                  .
      1 ->                                       .
    ..0 -> ...................................  c  .0-> ..  1->.....

      A                                                  B
                                                    simplifies swith condition
    """

    taus = {"pass": {"0_A_B": 4, "1_A_B": 4},
            "headway": {"0_1_A_B": 2, "1_0_B_A": 4},
            "stop": {"0_B": 1, "1_B": 1}, "res": 2}
    trains_timing_2 = {"tau": taus,
                 "initial_conditions": {"0_A": 1, "1_A": 1},
                 "penalty_weights": {"0_A": 2, "1_A": 0.5}}

    trains_paths = {
        "Paths": {0: ["A", "B"], 1: ["A", "B"]},
        "J": [0, 1],
        "Jd": dict(),
        "Josingle": dict(),
        "Jround": dict(),
        "Jtrack": {"B": [[0, 1]]},
        "Jswitch": dict(),
        "add_swithes_at_s": ["B"]
    }

    p_sum = 2
    p_pair = 1.
    p_qubic = 2.
    d_max = 5

    Q = make_Q(trains_paths, trains_timing_2, d_max, p_sum,
               p_pair, p_pair, p_qubic)

    assert np.array_equal(Q, np.load("test/files/Qfile_track.npz")["Q"])

    sol = np.load("test/files/solution_track.npz")

    assert energy(sol, Q) == -8+0.3


def test_deadlock_and_switches_two_trains():
    """
    Two trains going opposite direction on single track line
    and swithes constrain

    swith - c

    tracks - ......



    ..........                                        .. <- 1 ....
        A      .                                    .      B
    ..0 -> .... c ................................  c  ..........

    """
    trains_paths = {
        "Paths": {0: ["A", "B"], 1: ["B", "A"]},
        "J": [0, 1],
        "Jd": dict(),
        "Josingle": {("A","B"): [[0,1]]},
        "Jround": dict(),
        "Jtrack": dict(),
        "Jswitch": {"A": [{0: "out", 1: "in"}], "B": [{0: "in", 1: "out"}]}
    }

    taus = {"pass": {"0_A_B": 4, "1_B_A": 8},
            "stop": {"0_B": 1, "1_A": 1}, "res": 1}

    trains_timing_3 = {"tau": taus,
                "initial_conditions": {"0_A": 3, "1_B": 1},
                "penalty_weights": {"0_A": 2, "1_B": 0.5}}

    p_sum = 2.
    p_pair = 1.
    p_qubic = 2.
    d_max = 10

    Q = make_Q(trains_paths, trains_timing_3, d_max, p_sum,
               p_pair, p_pair, p_qubic)

    assert np.array_equal(Q, np.load("test/files/Qfile_two_ways.npz")["Q"])

    sol = np.load("test/files/solution_two_ways.npz")

    assert energy(sol, Q) == -8+0.35


def test_circ_Qmat():

    """
    At station B train 0 terminates and turns intro train 1 that starts there

    ....0 -> ..................................0 <-> 1.......
    A                                            B

    """

    trains_paths = {
        "skip_station": {
            0: "B",
            1: "A",
        },
        "Paths": {0: ["A", "B"], 1: ["B", "A"]},
        "J": [0, 1],
        "Jd": dict(),
        "Josingle": dict(),
        "Jround": {"B": [[0,1]]},
        "Jtrack": dict(),
        "Jswitch": dict()
    }

    taus = {"pass": {"0_A_B": 4, "1_B_A": 8}, "prep": {"1_B": 2}}
    trains_timing = {"tau": taus,
                 "initial_conditions": {"0_A": 3, "1_B": 1},
                 "penalty_weights": {"0_A": 2, "1_B": 0.5}}

    p_sum = 2.
    p_pair = 1.
    p_qubic = 2.
    d_max = 10

    Q = make_Q(trains_paths, trains_timing, d_max, p_sum,
               p_pair, p_pair, p_qubic)


    assert np.array_equal(Q, np.load("test/files/Qfile_circ.npz")["Q"])

    sol1 = np.load("test/files/solution_circ.npz")

    sol = [1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  1, -1, -1]

    assert np.array_equal(sol, sol1)

    assert energy(sol, Q) == -4+0.4




def test_Qmat_solved_on_DWave():
    #### particular problem solved on the DWave ######
    # original

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

    trains_timing = {"tau": taus,
                 "initial_conditions": {"j1_S1": 4, "j2_S1": 1, "j3_S2": 8},
                 "penalty_weights": {"j1_S1": 2, "j2_S1": 1, "j3_S2": 1}}

    d_max = 10

    trains_paths = {
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


    p_sum = 2.5
    p_pair = 1.25
    p_qubic = 2.1

    d_max = 10

    Q = make_Q(trains_paths, trains_timing, d_max, p_sum,
               p_pair, p_pair, p_qubic)

    assert np.array_equal(Q, np.load("test/files/Qfile.npz")["Q"])

    # rerouted
    """
    j2 ->                                      <- j3
    ...........c.......................c...c.......
     [ S1 ]  .  .                       . .    [ S2 ]
    .........c...c.......................c.........
    j1 ->


    """


    trains_paths_rerouted = {
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
        "add_swithes_at_s": ["S2"]  # additional τ(res.)(j, "B") in Eq. 18
    }


    Q_r = make_Q(trains_paths_rerouted, trains_timing, d_max,
                 p_sum, p_pair, p_pair, p_qubic)

    assert np.array_equal(Q_r, np.load("test/files/Qfile_r.npz")["Q"])
