import numpy as np
from railway_solvers import *


# testing particular QUBO element creation



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

    timetable = {"tau": taus,
                 "initial_conditions": {"0_A": 4, "1_A": 1, "2_B": 8},
                 "penalty_weights": {"0_A": 2, "1_A": 1, "2_B": 1}}

    # default
    train_sets = {
        "skip_station": {2: "A"},
        "Paths": {0: ["A", "B"], 1: ["A", "B"], 2: ["B", "A"]},
        "J": [0, 1, 2],
        "Jd": {"A": {"B": [[0, 1]]}, "B": {"A": [[2]]}},
        "Jtrack": {"B": [[0, 1]]}
    }

    inds, q_bits = indexing4qubo(train_sets, 10)

    k = inds.index({'j': 0, 's': "A", 'd': 3})
    k1 = inds.index({'j': 1, 's': "A", 'd': 0})

    # test penalites for span and stay

    assert Pspan(timetable, k, k1, inds, train_sets) == 0.
    assert Pspan(timetable, k1, k, inds, train_sets) == 0.

    k = inds.index({'j': 0, 's': "A", 'd': 2})
    k1 = inds.index({'j': 1, 's': "A", 'd': 0})

    assert Pspan(timetable, k, k1, inds, train_sets) == 1.
    assert Pspan(timetable, k1, k, inds, train_sets) == 1.

    k = inds.index({'j': 0, 's': "A", 'd': 2})
    k1 = inds.index({'j': 0, 's': "B", 'd': 0})

    assert Pstay(timetable, k, k1, inds, train_sets) == 1.
    assert Pstay(timetable, k1, k, inds, train_sets) == 1.

    k = inds.index({'j': 0, 's': "A", 'd': 1})
    k1 = inds.index({'j': 0, 's': "B", 'd': 1})

    assert Pstay(timetable, k, k1, inds, train_sets) == 0.
    assert Pstay(timetable, k1, k, inds, train_sets) == 0.

    #rerouting

    """
    1 ->                                    <- 2
    .............................................
    [ A ]                            . .    [ B ]
    ..................................c...........
    0 ->
    """

    train_sets_r = {
        "skip_station": {2: "A"},
        "Paths": {0: ["A", "B"], 1: ["A", "B"], 2: ["B", "A"]},
        "J": [0, 1, 2],
        "Josingle": {("A", "B"): [[1,2]]},
        "Jtrack": {"B": [[0, 1]]}
    }

    # test penalties for deadlock

    k = inds.index({'j': 1, 's': "A", 'd': 0})
    k1 = inds.index({'j': 2, 's': "B", 'd': 0})

    assert P1track(timetable, k, k1, inds, train_sets_r) == 1.
    assert P1track(timetable, k1, k, inds, train_sets_r) == 1.

    k = inds.index({'j': 1, 's': "A", 'd': 6})
    k1 = inds.index({'j': 2, 's': "B", 'd': 0})

    assert P1track(timetable, k, k1, inds, train_sets_r) == 1.
    assert P1track(timetable, k1, k, inds, train_sets_r) == 1.

    k = inds.index({'j': 1, 's': "A", 'd': 10})
    k1 = inds.index({'j': 2, 's': "B", 'd': 0})

    assert P1track(timetable, k, k1, inds, train_sets_r) == 1.
    assert P1track(timetable, k1, k, inds, train_sets_r) == 1.

    k = inds.index({'j': 1, 's': "B", 'd': 1})
    k1 = inds.index({'j': 0, 's': "A", 'd': 2})

    assert P1track(timetable, k, k1, inds, train_sets_r) == 0.
    assert P1track(timetable, k1, k, inds, train_sets_r) == 0.

    k = inds.index({'j': 1, 's': "B", 'd': 0})
    k1 = inds.index({'j': 2, 's': "B", 'd': 1})

    assert P1track(timetable, k, k1, inds, train_sets_r) == 0.
    assert P1track(timetable, k1, k, inds, train_sets_r) == 0.


def test_pswith():

    """
    ..........                                .... <- 2 ..
    [ A ]     .                              .    [ B ]
    .. 1 -> .. c .......................... c ... .......

    swithes at A (1 out, 2 in) and B (1 in 12out )
    """

    taus = {"pass": {"1_A_B": 8, "2_B_A": 8}, "res": 1}


    train_sets_r = {
        "skip_station": {2: "A"},
        "Paths": {1: ["A", "B"], 2: ["B", "A"]},
        "J": [1, 2],
        "Jd": dict(),
        "Josingle": {("A", "B"): [[1,2]]},
        "Jround": dict(),
        "Jtrack": dict(),
        "Jswitch": {"A": [{1: "out", 2: "in"}], "B": [{1: "in", 2: "out"}]}
    }

    timetable = {"tau": taus,
                 "initial_conditions": { "1_A": 1, "2_B": 8},
                 "penalty_weights": {"1_A": 1, "2_B": 1}}

    inds, q_bits = indexing4qubo(train_sets_r, 10)

    k = inds.index({'j': 1, 's': "A", 'd': 0})
    k1 = inds.index({'j': 2, 's': "B", 'd': 0})

    assert Pswitch(timetable, k, k1, inds, train_sets_r) == 0.
    assert Pswitch(timetable, k1, k, inds, train_sets_r) == 0.

    k = inds.index({'j': 1, 's': "A", 'd': 0})
    k1 = inds.index({'j': 2, 's': "B", 'd': 2})

    assert Pswitch(timetable, k, k1, inds, train_sets_r) == 0.
    assert Pswitch(timetable, k1, k, inds, train_sets_r) == 0.

    k = inds.index({'j': 1, 's': "A", 'd': 0})
    k1 = inds.index({'j': 2, 's': "B", 'd': 1})

    assert Pswitch(timetable, k, k1, inds, train_sets_r) == 1.
    assert Pswitch(timetable, k1, k, inds, train_sets_r) == 1.

    k = inds.index({'j': 1, 's': "A", 'd': 5})
    k1 = inds.index({'j': 2, 's': "B", 'd': 6})

    assert Pswitch(timetable, k, k1, inds, train_sets_r) == 1.
    assert Pswitch(timetable, k1, k, inds, train_sets_r) == 1.


def test_rolling_stock_circulation():

    """
     [ A ]                                            [ B ]
    .....0 -> ......................................0 <-> 1......
    """

    train_sets = {
        "Paths": {0: ["A", "B"], 1: ["B", "A"]},
        "J": [0, 1],
        "Jd": dict(),
        "Josingle": dict(),
        "Jround": {"B": [[0,1]]},
        "Jtrack": dict()
    }

    taus = {"pass": {"0_A_B": 4, "1_B_A": 8}, "prep": {"1_B": 2}}
    timetable = {"tau": taus,
                 "initial_conditions": {"0_A": 3, "1_B": 1},
                 "penalty_weights": {"0_A": 2, "1_B": 0.5}}

    inds, q_bits = indexing4qubo(train_sets, 10)

    k = inds.index({'j': 0, 's': "A", 'd': 0})
    k1 = inds.index({'j': 1, 's': "B", 'd': 7})

    assert Pcirc(timetable, k, k1, inds, train_sets) == 1.
    assert Pcirc(timetable, k1, k, inds, train_sets) == 1.

    k = inds.index({'j': 0, 's': "A", 'd': 2})
    k1 = inds.index({'j': 1, 's': "B", 'd': 9})

    assert Pcirc(timetable, k, k1, inds, train_sets) == 1.
    assert Pcirc(timetable, k1, k, inds, train_sets) == 1.

    k = inds.index({'j': 0, 's': "A", 'd': 0})
    k1 = inds.index({'j': 1, 's': "B", 'd': 8})

    assert Pcirc(timetable, k, k1, inds, train_sets) == 0.
    assert Pcirc(timetable, k1, k, inds, train_sets) == 0.

    k = inds.index({'j': 0, 's': "A", 'd': 2})
    k1 = inds.index({'j': 1, 's': "B", 'd': 10})

    assert Pcirc(timetable, k, k1, inds, train_sets) == 0.
    assert Pcirc(timetable, k1, k, inds, train_sets) == 0.



def test_qubic():

    # rerouting

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

    timetable = {"tau": taus,
                 "initial_conditions": {"0_A": 4, "1_A": 1, "2_B": 8},
                 "penalty_weights": {"0_A": 2, "1_A": 1, "2_B": 1}}

    train_sets = {
        "skip_station": {2: "A"},
        "Paths": {0: ["A", "B"], 1: ["A", "B"], 2: ["B", "A"]},
        "J": [0, 1, 2],
        "Jd": dict(),
        "Josingle": {("A", "B"): [[1,2]]},
        "Jround": dict(),
        "Jtrack": {"B": [[0, 1]]}
    }

    inds, q_bits = indexing4qubo(train_sets, 10)
    inds_z, l = z_indices(train_sets, 10)

    assert l == 121

    inds1 = list(np.concatenate([inds, inds_z]))
    assert len(inds1) == 176

    k = inds1.index({'j': 0, 's': "A", 'd': 1})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': "B", 'd': 1, 'd1': 4})

    assert P1qubic(timetable, k, k1, inds1, train_sets) == 0.
    assert P1qubic(timetable, k1, k, inds1, train_sets) == 0.


    k = inds1.index({'j': 0, 's': "A", 'd': 1})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': "B", 'd': 4, 'd1': 1})

    assert P1qubic(timetable, k, k1, inds1, train_sets) == 1.
    assert P1qubic(timetable, k1, k, inds1, train_sets) == 1.

    k = inds1.index({'j': 1, 's': "A", 'd': 0})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': "B", 'd': 4, 'd1': 8})

    assert P1qubic(timetable, k, k1, inds1, train_sets) == 1.
    assert P1qubic(timetable, k1, k, inds1, train_sets) == 1.


    k = inds1.index({'j': 0, 'j1': 1, 's': "B", 'd': 4, 'd1': 1})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': "B", 'd': 4, 'd1': 2})

    assert P2qubic(k, k, inds1, train_sets) == 3.
    assert P2qubic(k, k1, inds1, train_sets) == 0.

    k = inds1.index({'j': 0, 's': "A", 'd': 10})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': "B", 'd': 4, 'd1': 8})

    assert P2qubic(k, k1, inds1, train_sets) == 0.

    k = inds1.index({'j': 0, 's': "B", 'd': 10})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': "B", 'd': 10, 'd1': 8})

    assert P2qubic(k, k1, inds1, train_sets) == -1.
    assert P2qubic(k1, k, inds1, train_sets) == -1.

    k = inds1.index({'j': 0, 's': "B", 'd': 1})
    k1 = inds1.index({'j': 1, 's': "B", 'd': 0})

    assert P2qubic(k, k1, inds1, train_sets) == 0.5
    assert P2qubic(k1, k, inds1, train_sets) == 0.5

    k = inds1.index({'j': 0, 's': "B", 'd': 1})
    k1 = inds1.index({'j': 2, 's': "B", 'd': 0})

    assert P2qubic(k, k1, inds1, train_sets) == 0.
    assert P2qubic(k1, k, inds1, train_sets) == 0.

    k = inds1.index({'j': 0, 's': "A", 'd': 1})
    k1 = inds1.index({'j': 1, 's': "A", 'd': 0})

    assert P2qubic(k, k1, inds1, train_sets) == 0.
    assert P2qubic(k1, k, inds1, train_sets) == 0.

    k = inds1.index({'j': 0, 's': "B", 'd': 1})
    k1 = inds1.index({'j': 1, 's': "A", 'd': 0})

    assert P2qubic(k, k1, inds1, train_sets) == 0.
    assert P2qubic(k1, k, inds1, train_sets) == 0.


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

    timetable = {"tau": taus,
                 "initial_conditions": {"0_A": 4, "1_A": 1, "2_B": 8},
                 "penalty_weights": {"0_A": 2, "1_A": 1, "2_B": 1}}


    train_sets = {
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

    inds, q_bits = indexing4qubo(train_sets, d_max)
    assert get_coupling(timetable, 0, 0, train_sets,
                        inds, p_sum, p_pair) == -2.5
    assert get_coupling(timetable, 0, 24, train_sets,
                        inds, p_sum, p_pair) == 1.25

    inds_z, l = z_indices(train_sets, d_max)
    inds1 = list(np.concatenate([inds, inds_z]))

    k = inds1.index({'j': 1, 's': "A", 'd': 0})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': "B", 'd': 4, 'd1': 8})

    assert get_z_coupling(timetable, k, k1, train_sets,
                          inds1, p_pair, p_qubic) == 1.25

    assert penalty(timetable, 1, inds, d_max) == 0.2


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
    timetable_1 = {"tau": taus,
                 "initial_conditions": {"0_A": 3, "1_A": 1},
                 "penalty_weights": {"0_A": 2, "1_A": 0.5}}

    train_sets = {
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

    Q = make_Q(train_sets, timetable_1, d_max, p_sum,
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
    timetable_2 = {"tau": taus,
                 "initial_conditions": {"0_A": 1, "1_A": 1},
                 "penalty_weights": {"0_A": 2, "1_A": 0.5}}

    train_sets = {
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

    Q = make_Q(train_sets, timetable_2, d_max, p_sum,
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
    train_sets = {
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

    timetable_3 = {"tau": taus,
                "initial_conditions": {"0_A": 3, "1_B": 1},
                "penalty_weights": {"0_A": 2, "1_B": 0.5}}

    p_sum = 2.
    p_pair = 1.
    p_qubic = 2.
    d_max = 10

    Q = make_Q(train_sets, timetable_3, d_max, p_sum,
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

    train_sets = {
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
    timetable = {"tau": taus,
                 "initial_conditions": {"0_A": 3, "1_B": 1},
                 "penalty_weights": {"0_A": 2, "1_B": 0.5}}

    p_sum = 2.
    p_pair = 1.
    p_qubic = 2.
    d_max = 10

    Q = make_Q(train_sets, timetable, d_max, p_sum,
               p_pair, p_pair, p_qubic)


    assert np.array_equal(Q, np.load("test/files/Qfile_circ.npz")["Q"])

    sol1 = np.load("test/files/solution_circ.npz")

    sol = [1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  1, -1, -1]

    assert np.array_equal(sol, sol1)

    assert energy(sol, Q) == -4+0.4




def test_DWave_Qmat():
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


    p_sum = 2.5
    p_pair = 1.25
    p_qubic = 2.1

    d_max = 10

    Q = make_Q(train_sets, timetable, d_max, p_sum,
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
        "add_swithes_at_s": ["S2"]  # additional τ(res.)(j, "B") in Eq. 18
    }


    Q_r = make_Q(train_sets_rerouted, timetable, d_max,
                 p_sum, p_pair, p_pair, p_qubic)

    assert np.array_equal(Q_r, np.load("test/files/Qfile_r.npz")["Q"])
