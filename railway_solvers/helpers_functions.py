
"""heplers for QUBO creation """
import numpy as np

def occurs_as_pair(a, b, vecofvec):
    """checks whether a and b occurs together in the same vector of vectors """
    for v in vecofvec:
        if a in v and b in v and a != b:
            return True
    return False



def subsequent_station(path, s):
    """given a train path and atation returns next station in this path"""
    k = path.index(s)
    if k == len(path) - 1:
        return None
    return path[k + 1]


def previous_station(path, s):
    """given a train path and station s
    returns preceeding station in the path

    if there is no preceeding station returns None
    """
    k = path.index(s)
    if k == 0:
        return None
    return path[k - 1]



def tau(
    trains_timing,
    key,
    first_train=None,
    first_station=None,
    second_station=None,
    second_train=None,
):
    """given the trains_timing and the key returns particular time span τ(key)
    for given train and station or stations

    in the key is not in ["headway", "pass", "stop", "prep", "res"]
    return None
    """
    if key == "headway":
        return trains_timing["tau"]["headway"][
            f"{first_train}_{second_train}_{first_station}_{second_station}"
        ]
    if key == "pass":
        string = f"{first_train}_{first_station}_{second_station}"
        return trains_timing["tau"][key][string]
    if key == "stop":
        return trains_timing["tau"][key][f"{first_train}_{first_station}"]
    if key == "prep":
        return trains_timing["tau"][key][f"{first_train}_{first_station}"]
    if key == "res":
        return trains_timing["tau"]["res"]
    return -1000


def penalty_weights(trains_timing, train, station):
    """given trains_timing returns penalty weight for
    a delay above unaviodable at the given station"""

    train_station = f"{train}_{station}"
    if train_station in trains_timing["penalty_weights"]:
        return trains_timing["penalty_weights"][train_station]
    return 0.0


def earliest_dep_time(S, trains_timing, train, station):
    """returns earlies possible departure of a train from the given station
    including unavoidlable delays and the schedule if the schedule is given
    """
    if "schedule" in trains_timing:
        sched = trains_timing["schedule"][f"{train}_{station}"]
    else:
        sched = -np.inf
    train_station = f"{train}_{station}"

    if train_station in trains_timing["initial_conditions"]:
        unaviodable = trains_timing["initial_conditions"][train_station]
        return np.maximum(sched, unaviodable)

    s = previous_station(S[train], station)
    tau_pass = tau(
        trains_timing,
        "pass",
        first_train=train,
        first_station=s,
        second_station=station,
    )
    tau_stop = tau(trains_timing, "stop", first_train=train, first_station=station)
    unavoidable = earliest_dep_time(S, trains_timing, train, s) + tau_pass
    unavoidable += tau_stop
    return np.maximum(sched, unavoidable)


# helpers for trains set


def not_the_same_rolling_stock(j, jp, trains_paths):
    """checks if two trains (j, jp) are not served by the same rolling stock"""
    if "Jround" not in trains_paths:
        return True
    for s in trains_paths["Jround"].keys():
        if occurs_as_pair(j, jp, trains_paths["Jround"][s]):
            return False
    return True


def departure_station4switches(s, j, place_of_switch, trains_paths):
    """returns the station symbol from which train j departes prior to passing
    the swith at station s
    """
    if place_of_switch[j] == "out":
        return s
    if place_of_switch[j] == "in":
        S = trains_paths["Paths"]
        return previous_station(S[j], s)
    return 0


def skip_station(j,s, trains_paths):
    """ determines whether the station s should be skipped for train j
    while construtiong constrains, or delay variables
     """
    if "skip_station" not in trains_paths:
        return False
    if j not in trains_paths["skip_station"]:
        return False
    if s != trains_paths["skip_station"][j]:
        return False
    return True

#####   the round specific cases for track occupation ####

def previous_train_from_Jround(trains_paths,j, s):
    """
    returns the id of the train from which j gets a train set at station s if j
    starts at s as an continuation of some other train
    """
    previous_train = None
    Jround = trains_paths["Jround"]
    if s in Jround:
        pairs = Jround[s]
        leave_trains = [el[1] for el in pairs]
        if j in leave_trains:
            i = leave_trains.index(j)
            previous_train = pairs[i][0]
    return previous_train


def energy(v, Q):
    """compute energy from QUBO """
    if -1 in v:
        v = [(y + 1) / 2 for y in v]
    X = np.array(Q)
    V = np.array(v)
    return V @ X @ V.transpose()
