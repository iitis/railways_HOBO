""" inputs used for DWave calculation """


class DWave_problem():

    """
    original

                                            <- j3
    ..........c........................c....c......
     [ S1 ] .  .                        .  .   [ S2 ]
    .......c....c........................c.........
    j1 ->
    j2 ->

    rerouted

    j2 ->                                      <- j3
    ...........c.......................c...c.......
     [ S1 ]  .  .                       . .    [ S2 ]
    .........c...c.......................c.........
    j1 ->



    S1, S2 - stations
    j1, j2, j3 - trains
    .....  - track
    c - switch
    """
    def __init__(self, rerouted = False):

        self.taus = {"pass": {"j1_S1_S2": 4, "j2_S1_S2": 8, "j3_S2_S1": 8},
                "headway": {"j1_j2_S1_S2": 2, "j2_j1_S1_S2": 6},
                "stop": {"j1_S2": 1, "j2_S2": 1},
                "res": 1
                }

        self.trains_timing = {"tau": self.taus,
                     "initial_conditions": {"j1_S1": 4, "j2_S1": 1, "j3_S2": 8},
                     "penalty_weights": {"j1_S1": 2, "j2_S1": 1, "j3_S2": 1}}


        if not rerouted:
            self.trains_paths = {
                "skip_station": {
                    "j3": "S1",  # we do not count train j3 leaving S1
                },
                "Paths": {"j1": ["S1", "S2"], "j2": ["S1", "S2"], "j3": ["S2", "S1"]},
                "J": ["j1", "j2", "j3"],
                "Jd": {"S1": {"S2": [["j1", "j2"]]}, "S2": {"S1": [["j3"]]}},
                "Josingle": {},
                "Jround": {},
                "Jtrack": {"S2": [["j1", "j2"]]},
                "Jswitch": {},
                "add_swithes_at_s": ["S2"]  # additional τ(res.)(j, "B") in Eq. 18
            }
        else:
            self.trains_paths = {
                "skip_station": {
                    "j3": "S1",  # we do not count train j3 leaving S1
                },
                "Paths": {"j1": ["S1", "S2"], "j2": ["S1", "S2"], "j3": ["S2", "S1"]},
                "J": ["j1", "j2", "j3"],
                "Jd": {},
                "Josingle": {("S1", "S2"): [["j2", "j3"]]},
                "Jround": {},
                "Jtrack": {"S2": [["j1", "j2"]]},
                "Jswitch": {"S1": [{"j2":"out", "j3":"in"}], "S2": [{"j2":"in", "j3":"out"}]}, # swithes from the single track line
                "add_swithes_at_s": ["S2"]  # additional τ(res.)(j, "B") in Eq. 18
            }

        self.p_sum = 2.5
        self.p_pair = 1.25
        self.p_qubic = 2.1
        self.d_max = 10
