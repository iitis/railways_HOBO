import numpy as np
from railway_solvers import make_Q, energy


"""
tests on examples concerning particular scenarios
"""

############## general input ###########
# taus =
#{"pass" : {"j_s_s1" : τ^pass(j,s,s1), ...} ==>  passing time of j s -> s1
# "headway" : {"j_j1_s_s1" : τ^headway(j,j1,s,s1),  .... } ==> both j and j1 goes s->s1
# minimal time j1 must wait at s after j leaving s
# "stop": {"j_s" : τ^stop(j,s)}, ....  }  ==> minimal stopping time of j at s
#"res": τ^res} ==> switch occupation time, set globally

# headway, pass, block - Fig. 2
# prep, res. - Fig 3.


# trains_timing = {"tau": taus,
#              "initial_conditions" : {"j_s" : t(j,s_out), ...},
#              "penalty_weights" : {"j_s" : w(j,s), ...}}


# w(j,s) => penalty factor for j leaving s later than unaviodlable delay.


#to ensure train can not leave befor the due time, there also ben be added:
# "schedule": schedule = {"j_s" : t_schedule(j,s_out), ... }


############  trains path #########
# trains_paths = {
    #"Paths": {"j": ["s1", "s2", "s3", ...] ...} => path of j marked by stations
    # "J": ["j", "j1", "j2", ...] => se of all trains
    # "Jd": {"s": {"s1": [["j", "j1", "j2",...], ["i", "i1",...]]...}...} =>
    # from s to s1 goes "j", "j1", "j2",... on one track and "i", "i1",.. on another track
    #  "Josingle": {("s", "s1"): [[j, j1]]} => j goes s -> s1 while j1 goes s1 -> s on the same (single) track (pairs only)
    # "Jround": {"s": [[j, j1], [i, i1]] ...} => at s j terminates
    # and starts than as a new train j1 the same is with the pair i, i1  (pairs only)
    # "Jtrack": {"s": [[j, j1, j2] ..] ...} => at s j, j1 dna j2 uses the same track
    # "Jswitch": {"s": [{j: "out", j1: "in"}, ....]. ...}  => at s pair j and j1 uses the
    # same switch while j entering, and j1 leaving


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
    trains_timing = {"tau": taus,
                 "initial_conditions": {"j1_A": 3, "j2_A": 1}, # leaving times
                 "penalty_weights": {"j1_A": 2, "j2_A": 0.5}}  # these are w_j

    trains_paths = {
        "Paths": {"j1": ["A", "B"], "j2": ["A", "B"]}, # trains paths
        "J": ["j1", "j2"],  # set of all trains
        "Jd": {"A": {"B": [["j1", "j2"]]}}, # from A to B goes j1 and j2 on the same track
        "Josingle": {},  # no single line condition
        "Jround": {},  # no rolling stock circulation condition
        "Jtrack": {}, # no single track occupation condition
        "Jswitch": {} # no switch occupation condition
    }

    p_sum = 2
    p_pair = 1.
    p_qubic = 2.
    d_max = 5

    Q = make_Q(d_max, p_sum, p_pair, p_qubic, trains_timing, trains_paths)

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
    trains_timing = {"tau": taus,
                 "initial_conditions": {"0_A": 1, "1_A": 1},
                 "penalty_weights": {"0_A": 2, "1_A": 0.5}}

    trains_paths = {
        "Paths": {0: ["A", "B"], 1: ["A", "B"]},
        "J": [0, 1],
        "Jd": {},
        "Josingle": {},
        "Jround": {},
        "Jtrack": {"B": [[0, 1]]},
        "Jswitch": {},
        "add_swithes_at_s": ["B"]
    }

    p_sum = 2
    p_pair = 1.
    p_qubic = 2.
    d_max = 5

    Q = make_Q(d_max, p_sum, p_pair, p_qubic, trains_timing, trains_paths)

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
        "Jd": {},
        "Josingle": {("A","B"): [[0,1]]},
        "Jround": {},
        "Jtrack": {},
        "Jswitch": {"A": [{0: "out", 1: "in"}], "B": [{0: "in", 1: "out"}]}
    }

    taus = {"pass": {"0_A_B": 4, "1_B_A": 8},
            "stop": {"0_B": 1, "1_A": 1}, "res": 1}

    trains_timing = {"tau": taus,
                "initial_conditions": {"0_A": 3, "1_B": 1},
                "penalty_weights": {"0_A": 2, "1_B": 0.5}}

    p_sum = 2.
    p_pair = 1.
    p_qubic = 2.
    d_max = 10

    Q = make_Q(d_max, p_sum, p_pair, p_qubic, trains_timing, trains_paths)

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
        "Jd": {},
        "Josingle": {},
        "Jround": {"B": [[0,1]]},
        "Jtrack": {},
        "Jswitch": {}
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


    from inputs.DW_example import d_max, p_sum, p_pair, p_qubic, trains_timing, trains_paths


    Q = make_Q(d_max, p_sum, p_pair, p_qubic, trains_timing, trains_paths)

    assert np.array_equal(Q, np.load("test/files/Qfile.npz")["Q"])

def test_Qmat_on_DWave_rerouted():


    # need to import file inputs/DWave_example
    from inputs.DW_example import d_max, p_sum, p_pair, p_qubic, trains_timing, trains_paths_rerouted


    Q_r = make_Q(d_max,p_sum, p_pair, p_qubic, trains_timing, trains_paths_rerouted)

    assert np.array_equal(Q_r, np.load("test/files/Qfile_r.npz")["Q"])
