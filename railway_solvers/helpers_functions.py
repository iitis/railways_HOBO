import numpy as np


def occurs_as_pair(a, b, vecofvec):
    """checks whether a and b occurs together in the same vector of vectors """
    for v in vecofvec:
        if a in v and b in v and a != b:
            return True
    return False



def update_dictofdicts(d1, d2):
    """updates d1 (nested dict of dict ...)
    by d2 -nested dict of dict ... (with the same structure but single element)
    update at the lowest possible level of nesting
    """
    assert np.size(d2.keys()) == 1

    for k in d2.keys():
        if k in d1.keys():
            update_dictofdicts(d1[k], d2[k])
        else:
            d1.update(d2)
    return d1


def subsequent_station(path, s):
    """given a train path and atation returns next station in this path"""
    k = path.index(s)
    if k == len(path) - 1:
        return None
    else:
        return path[k + 1]


def previous_station(path, s):
    """given a train path and station s
    returns preceeding station in the path

    if there is no preceeding station returns None
    """
    k = path.index(s)
    if k == 0:
        return None
    else:
        return path[k - 1]


# timetable input is extected to be in the following form of dict of dicts
#  taus are given as
# taus = {"pass" : {"j_s_si" : τ^pass(j,s,s1), ...},
# "headway" : {"j_j1_s_s1" : τ^pass(j,j1,s,s1)  .... },
# "stop": {"j_s_None" : τ^stop(j,s)}, "res": τ^res}
# τ^res is just one for all situations, it may need to be extended

# train schedule if available (train can not leave before schedule)
# schedule = {"j_s" : t_schedule(j,s_out), ... }

# timetable = {"tau": taus, "schedule" : schedule,
#              "initial_conditions" : {"j_s" : t(j,s_out), ...},
#              "penalty_weights" : {"j_s" : w(j,s), ...}}


def tau(
    timetable,
    key,
    first_train=None,
    first_station=None,
    second_station=None,
    second_train=None,
):
    """given the timetable and the key returns particular time span τ(key)
    for given train and station or stations

    in the key is not in ["headway", "pass", "stop", "prep", "res"]
    return None
    """
    if key == "headway":
        return timetable["tau"]["headway"][
            f"{first_train}_{second_train}_{first_station}_{second_station}"
        ]
    elif key == "pass":
        string = f"{first_train}_{first_station}_{second_station}"
        return timetable["tau"][key][string]
    elif key == "stop":
        return timetable["tau"][key][f"{first_train}_{first_station}"]
    elif key == "prep":
        return timetable["tau"][key][f"{first_train}_{first_station}"]
    elif key == "res":
        return timetable["tau"]["res"]
    return None


def penalty_weights(timetable, train, station):
    """given timetable returns penalty weight for
    a delay above unaviodable at the given station"""

    train_station = f"{train}_{station}"
    if train_station in timetable["penalty_weights"]:
        return timetable["penalty_weights"][train_station]
    else:
        return 0.0


def earliest_dep_time(S, timetable, train, station):
    """returns earlies possible departure of a train from the given station
    including unavoidlable delays and the schedule if the schedule is given
    """
    if "schedule" in timetable:
        sched = timetable["schedule"][f"{train}_{station}"]
    else:
        sched = -np.inf
    train_station = f"{train}_{station}"

    if train_station in timetable["initial_conditions"]:
        unaviodable = timetable["initial_conditions"][train_station]
        return np.maximum(sched, unaviodable)
    else:
        s = previous_station(S[train], station)
        τ_pass = tau(
            timetable,
            "pass",
            first_train=train,
            first_station=s,
            second_station=station,
        )
        τ_stop = tau(timetable, "stop", first_train=train, first_station=station)
        unavoidable = earliest_dep_time(S, timetable, train, s) + τ_pass
        unavoidable += τ_stop
        return np.maximum(sched, unavoidable)


# helpers for trains set


def not_the_same_rolling_stock(j, jp, train_sets):
    """checks if two trains (j, jp) are not served by the same rolling stock"""
    if "Jround" not in train_sets:
        return True
    for s in train_sets["Jround"].keys():
        if occurs_as_pair(j, jp, train_sets["Jround"][s]):
            return False
    return True


def departure_station4switches(s, j, place_of_switch, train_sets):
    """returns the station symbol from which train j departes prior to passing
    the swith at station s
    """
    if place_of_switch[j] == "out":
        return s
    elif place_of_switch[j] == "in":
        S = train_sets["Paths"]
        return previous_station(S[j], s)


def get_M(LHS, RHS, d_max):
    """computes minimal value of the large number M for the order variable
    y ∈ [0,1] conditional inequality such that:

      LHS + delay >= RHS + delay - M y

      The inequality should be checked for y = 0 and always hold for y = 1
      """
    return np.max([RHS + d_max - LHS, 1.0])


def skip_station(j,s, train_sets):
    """ determines whether the station s should be skipped for train j
    while construtiong constrains, or delay variables
     """
    if "skip_station" not in train_sets:
        return False
    elif j not in train_sets["skip_station"]:
        return False
    elif s != train_sets["skip_station"][j]:
        return False
    return True

#####   the round specific cases for track occupation ####

def previous_train_from_Jround(train_sets,j, s):
    """
    returns the id of the train from which j gets a train set at station s if j
    starts at s as an continuation of some other train
    """
    previous_train = None
    Jround = train_sets["Jround"]
    if s in Jround:
        pairs = Jround[s]
        leave_trains = [el[1] for el in pairs]
        if j in leave_trains:
            i = leave_trains.index(j)
            previous_train = pairs[i][0]
    return previous_train


def subsequent_train_at_Jround(train_sets, j, s):
    """
    returns the id of the train to which j gives a train set at station s if j
    terminates at s and is continiued be the other train
    """
    next_train = None
    Jround = train_sets["Jround"]
    if s in Jround:
        pairs = Jround[s]
        enter_trains = [el[0] for el in pairs]
        if j in enter_trains:
            i = enter_trains.index(j)
            next_train = pairs[i][1]
    return next_train



def can_MO_on_line(j, jp, s, train_sets):
    """ returns true if trains j and j' can M_) in the line between s and  previous sp"""
    Jd = train_sets["Jd"]
    S = train_sets["Paths"]
    sp = previous_station(S[j], s)
    spp = previous_station(S[jp], s)

    if sp == None or spp == None:
        return False
    if sp != spp:
        return True
    elif occurs_as_pair(j, jp, Jd[sp][s]):
        return False
    else:
        return True

def are_two_trains_entering_via_the_same_switches(train_sets, s, j, jp):
    if s in train_sets["Jswitch"].keys():
        v = train_sets["Jswitch"][s]
        are_swithes = np.array([j in e and jp in e for e in v])
        if True in are_swithes:
            return ('in', 'in') in [(v[i][j], v[i][jp]) for i in np.where(are_swithes == True)[0]]
        else:
            return False
    else:
        return False


def energy(v, Q):
    if -1 in v:
        v = [(y + 1) / 2 for y in v]
    X = np.array(Q)
    V = np.array(v)
    return V @ X @ V.transpose()
