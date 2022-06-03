import numpy as np
from railway_solvers import make_Q, energy


# trains_timing input is extected to be in the following form of dict of dicts
#  taus are given as
# taus = {"pass" : {"j_s_si" : τ^pass(j,s,s1), ...},
# "headway" : {"j_j1_s_s1" : τ^headway(j,j1,s,s1)  .... },
# "stop": {"j_s_None" : τ^stop(j,s)}, "res": τ^res}
# τ^res is just one for all situations, it may need to be extended

# train schedule if available (train can not leave before schedule)
# schedule = {"j_s" : t_schedule(j,s_out), ... }

# trains_timing = {"tau": taus, "schedule" : schedule,
#              "initial_conditions" : {"j_s" : t(j,s_out), ...},
#              "penalty_weights" : {"j_s" : w(j,s), ...}}


def test_headway_two_trains():

    """
    two trains, j1 and j2 going one way A -> B test headway condition


     j2 ->
     j1 ->  ------------------------------
             [ A ]                    [ B ]

    j1, j2 - trains
    [A], [B] - stations
    -----    - line
    """

    # if j1 go first from A to B and j2 second there is the headway between of 2,
    # if j2 go first form A to B and j1 second there is the headway between of 6

    taus = {"pass": {"j1_A_B": 4, "j2_A_B": 8},
            "headway": {"j1_j2_A_B": 2, "j2_j1_A_B": 6},
            "stop": {"j1_B": 1, "j2_B": 1}, "res": 1}
    trains_timing_1 = {"tau": taus,
                 "initial_conditions": {"j1_A": 3, "j2_A": 1}, # leaving times
                 "penalty_weights": {"j1_A": 2, "j2_A": 0.5}}  # these are w_j

    trains_paths = {
        "Paths": {"j1": ["A", "B"], "j2": ["A", "B"]}, # trains paths
        "J": ["j1", "j2"],  # set of all trains
        "Jd": {"A": {"B": [["j1", "j2"]]}}, # from A to B goes j1 and j2 on the same track
        "Josingle": dict(),  # no single line condition
        "Jround": dict(),  # no rolling stock circulation condition
        "Jtrack": dict(), # no single track occupation condition
        "Jswitch": dict() # no switch occupation condition
    }

    p_sum = 2
    p_pair = 1.
    p_qubic = 2.
    d_max = 5

    Q = make_Q(d_max, p_sum, p_pair, p_qubic, trains_timing_1, trains_paths)

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

    Q = make_Q(d_max, p_sum, p_pair, p_qubic, trains_timing_2, trains_paths)

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

    Q = make_Q(d_max, p_sum, p_pair, p_qubic, trains_timing_3, trains_paths)

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

    Q = make_Q(d_max, p_sum, p_pair, p_qubic, trains_timing, trains_paths)


    assert np.array_equal(Q, np.load("test/files/Qfile_circ.npz")["Q"])

    sol1 = np.load("test/files/solution_circ.npz")

    sol = [1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  1, -1, -1]

    assert np.array_equal(sol, sol1)

    assert energy(sol, Q) == -4+0.4




def test_Qmat_solved_on_DWave():
    #### particular problem solved on the DWave ######

    ###### original ############

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

    Q = make_Q(d_max, p_sum, p_pair, p_qubic, trains_timing, trains_paths)

    assert np.array_equal(Q, np.load("test/files/Qfile.npz")["Q"])

    ############## rerouted  ############

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


    Q_r = make_Q(d_max,p_sum, p_pair, p_qubic, trains_timing, trains_paths_rerouted)

    assert np.array_equal(Q_r, np.load("test/files/Qfile_r.npz")["Q"])