from railway_solvers import skip_station, not_the_same_rolling_stock, penalty_weights
from railway_solvers import subsequent_station, previous_station, occurs_as_pair, earliest_dep_time
from railway_solvers import tau, departure_station4switches, previous_train_from_Jround
from railway_solvers import energy

def test_pairs():
    assert occurs_as_pair(1, 2, [[1, 2, 3], [4], [5, 6]])
    assert occurs_as_pair(2, 1, [[1, 2, 3], [4], [5, 6]])
    assert not occurs_as_pair(1, 4, [[1, 2, 3], [4], [5, 6]])



def test_trains_paths():
    S = {0: [0, 1, 2, 4], 1: [0, 1, 2], 2: [1, 0]}

    assert previous_station(S[0], 4) == 2
    assert previous_station(S[2], 1) is None

    assert subsequent_station(S[1], 2) is None
    assert subsequent_station(S[0], 2) == 4
    assert subsequent_station(S[2], 1) == 0


def test_auxiliary_trains_timing_functions():
    taus = {
        "pass": {"0_0_1": 5, "1_0_1": 7, "2_1_0": 10},
        "headway": {
            "0_1_0_1": 2,
            "1_0_0_1": 5,
        },
        "stop": {"0_1": 1, "1_1": 2, "2_0": 1},
        "res": 3,
    }
    schedule = {"0_0": -10, "1_0": 0, "2_1": 0, "0_1": -3, "1_1": 9, "2_0": 11}
    trains_timing = {
        "tau": taus,
        "schedule": schedule,
        "initial_conditions": {"0_0": 4, "1_0": 1, "2_1": 8},
        "penalty_weights": {"0_0": 2, "1_0": 1, "2_1": 1},
    }

    assert tau(trains_timing, "pass", first_train=0, first_station=0, second_station=1) == 5
    assert tau(trains_timing, "res") == 3

    assert penalty_weights(trains_timing, 1, 0) == 1
    assert penalty_weights(trains_timing, 1, 1) == 0
    assert penalty_weights(trains_timing, 2, 1) == 1

    S = {0: [0, 1], 1: [0, 1], 2: [1, 0]}

    assert earliest_dep_time(S, trains_timing, 0, 0) == 4
    assert earliest_dep_time(S, trains_timing, 0, 1) == 10

    assert earliest_dep_time(S, trains_timing, 2, 0) == 19
    assert earliest_dep_time(S, trains_timing, 2, 1) == 8


def test_helpers_of_trains_paths():

    trains_paths = {
        "Paths": {1: ["A", "B"], 2: ["B", "A"], 3: ["A", "B"]},
        "Jround": {"B": [[1, 2]]},
        "Jswitch": {"B": [{1: "out", 3: "out"}, {1: "in", 3: "in"}]},
    }

    assert not_the_same_rolling_stock(0, 1, trains_paths)
    assert not_the_same_rolling_stock(0, 1, trains_paths)
    assert not not_the_same_rolling_stock(1, 2, trains_paths) 

    assert departure_station4switches("B", 1, {1: "out", 3: "out"}, trains_paths) == "B"
    assert departure_station4switches("B", 1, {1: "in", 3: "in"}, trains_paths) == "A"
    assert skip_station(1, "A", trains_paths) == False

    assert previous_train_from_Jround(trains_paths, 2, "B") == 1
    assert previous_train_from_Jround(trains_paths, 1, "B") is None


def test_energy_computation():
    v = [-1, 1, 1]
    Q = [[1. for _ in range(3)] for _ in range(3)]
    assert energy(v, Q) == 4.
