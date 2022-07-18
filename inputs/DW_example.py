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
    def __init__(self, rerouted = False, soft_constrains = True):

        self.taus = {"pass": {"j1_S1_S2": 4, "j2_S1_S2": 8, "j3_S2_S1": 8},
                "headway": {"j1_j2_S1_S2": 2, "j2_j1_S1_S2": 6},
                "stop": {"j1_S2": 1, "j2_S2": 1},
                "res": 1
                }

        if soft_constrains:

            self.trains_timing = {"tau": self.taus,
                     "initial_conditions": {"j1_S1": 4, "j2_S1": 1, "j3_S2": 8},
                     "penalty_weights": {"j1_S1": 2, "j2_S1": 1, "j3_S2": 1}
                     }
        else:

            self.trains_timing = {"tau": self.taus,
                     "initial_conditions": {"j1_S1": 4, "j2_S1": 1, "j3_S2": 8},
                     "penalty_weights": {"j1_S1": 0, "j2_S1": 0, "j3_S2": 0}
                     }



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


class Problem_of_5_trains():
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
    def __init__(self, soft_constrains = True):
        """ parameters """

        self.taus = {
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

        if soft_constrains:

            self.trains_timing = {
                "tau": self.taus,
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

        else:

            self.trains_timing = {
                "tau": self.taus,
                "initial_conditions": {
                    "21_A": 6,
                    "22_A": 1,
                    "23_C": 26,
                    "24_C": 25,
                    "25_D": 28,
                },
                "penalty_weights": {
                    "21_B": 0,
                    "22_B": 0,
                    "21_A": 0,
                    "22_A": 0,
                    "23_B": 0,
                    "24_C": 0,
                    "25_D": 0,
                },
            }


        self.trains_paths = {
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
            # trains that pass through common swithes while enetering or leaving given station
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

        # QUBO parameters
        self.d_max = 10
        self.p_sum = 2.5
        self.p_pair = 1.25
        self.p_qubic = 2.1
