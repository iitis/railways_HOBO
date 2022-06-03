import itertools
import numpy as np
from .helpers_functions import skip_station, not_the_same_rolling_stock, penalty_weights
from .helpers_functions import subsequent_station, previous_station, occurs_as_pair, earliest_dep_time
from .helpers_functions import tau, departure_station4switches, previous_train_from_Jround


# this is the direct QUBO / HOBO implemntation for arXiv:2107.03234


def indexing4qubo(trains_paths, d_max):
    """returns vector of dicts of trains stations and delays
     in the form {"j": j, "s": s, "d": d}

     the index of vector od these correspond to the index in Q matrix
    """

    S = trains_paths["Paths"]
    inds = []
    for j in trains_paths["J"]:
        for s in S[j]:
            if not skip_station(j,s, trains_paths):
                for d in range(d_max + 1):
                    inds.append({"j": j, "s": s, "d": d})
    return inds, len(inds)


################# constrains  #####################

def P_sum(k, k1, jsd_dicts):
    """
    Sum to one conditon - Eq. (41)

    each train leaves each station (on its path) once and only once

    returns not wieghted (by peanlty constant) contribution from ∑_i x_i  = 1 constrain
    to Qmat[k, k1]

    Input:
    k, k1 -- indices the the Qmat
    jsd_dicts -- vector {"j": j, "s": s, "d": d} -- train, station, delay.
    Each train leaves each station at one and only one delay.
    """
    if jsd_dicts[k]["j"] == jsd_dicts[k1]["j"] and jsd_dicts[k]["s"] == jsd_dicts[k1]["s"]:
        if jsd_dicts[k]["d"] == jsd_dicts[k1]["d"]:
            return -1.0
        else:
            return 1.0
    return 0.0


def P_headway(trains_timing, k, k1, jsd_dicts, trains_paths):
    """
    Minimal headway condition - Eq. (42)

    Returns 0.0 or 1.0, i.e. not weighted contribution to Qmat[k, k1] and Qmat[k1, k]

    Input:
    - trains_timing - dict
    - trains_paths -- dict
    - k, k1 -- indices
    - jsd_dicts -- vector {"j": j, "s": s, "d": d}
      of trains, stations, delays tied to index k ot k1


     ..... j1 -> ....... j2 -> .......
    [s1]          headway         [s2]
    """

    S = trains_paths["Paths"]
    j = jsd_dicts[k]["j"]
    j1 = jsd_dicts[k1]["j"]
    s = jsd_dicts[k]["s"]
    s1 = jsd_dicts[k1]["s"]

    s_next = subsequent_station(S[j], s)

    if s == s1 and s_next != None and s_next == subsequent_station(S[j1], s1):

        if s in trains_paths["Jd"].keys():
            if s_next in trains_paths["Jd"][s].keys():
                if occurs_as_pair(j, j1, trains_paths["Jd"][s][s_next]):

                    t = jsd_dicts[k]["d"] + earliest_dep_time(S, trains_timing, j, s)
                    t1 = jsd_dicts[k1]["d"] + earliest_dep_time(S, trains_timing, j1, s)

                    A = -tau(
                        trains_timing,
                        "headway",
                        first_train=j1,
                        second_train=j,
                        first_station=s,
                        second_station=s_next,
                    )

                    B = tau(
                        trains_timing,
                        "headway",
                        first_train=j,
                        second_train=j1,
                        first_station=s,
                        second_station=s_next,
                    )

                    if A < t1 - t < B:
                        return 1.0
    return 0.0


def P_single_track_line(trains_timing, k, k1, jsd_dicts, trains_paths):
    """
    Single track line condition - Eq. (43)

    Returns 0.0 or 1.0, i.e. not weighted contribution to Qmat[k, k1] and Qmat[k1, k]

    Input:
    - trains_timing - dict
    - trains_paths -- dict
    - k, k1 -- indices
    - jsd_dicts -- vector {"j": j, "s": s, "d": d}
      of trains, stations, delays tied to index k ot k1

         ......                            ... <-j2 ..
        [s1]    .                        .      [s2]
       ..j1 ->.......................................

     """

    #symetrisation
    p = penalty_single_track(trains_timing, k, k1, jsd_dicts, trains_paths)
    p += penalty_single_track(trains_timing, k1, k, jsd_dicts, trains_paths)
    return p

def penalty_single_track(trains_timing, k, k1, jsd_dicts, trains_paths):
    """
    Helper for P_single_track_line

    Returns 0.0 or 1.0 as the contribution to Qmat[k, k1]
    """
    S = trains_paths["Paths"]
    j = jsd_dicts[k]["j"]
    j1 = jsd_dicts[k1]["j"]
    s = jsd_dicts[k]["s"]
    s1 = jsd_dicts[k1]["s"]

    if not_the_same_rolling_stock(j, j1, trains_paths):

        if (s, s1) in trains_paths["Josingle"].keys() and [j, j1] in trains_paths[
            "Josingle"
        ][(s, s1)]:
            t = jsd_dicts[k]["d"] + earliest_dep_time(S, trains_timing, j, s)
            t2 = t
            t1 = jsd_dicts[k1]["d"] + earliest_dep_time(S, trains_timing, j1, s1)

            t += -tau(
                trains_timing, "pass", first_train=j1, first_station=s1, second_station=s
            )
            t2 += tau(
                trains_timing, "pass", first_train=j, first_station=s, second_station=s1
            )

            if t < t1 < t2:
                return 1.0
    return 0.0


def P_minimal_stay(trains_timing, k, k1, jsd_dicts, trains_paths):
    """
    Minimal stay condition - Eq. (44)

    Returns 0.0 or 1.0, i.e. not weighted contribution to Qmat[k, k1] and Qmat[k1, k]

    Input:
    - trains_timing - dict
    - trains_paths -- dict
    - k, k1 -- indices
    - jsd_dicts -- vector {"j": j, "s": s, "d": d}
      of trains, stations, delays tied to index k ot k1

    """
    S = trains_paths["Paths"]
    p = penalty_minimal_stay(trains_timing, k, k1, jsd_dicts, S)
    p += penalty_minimal_stay(trains_timing, k1, k, jsd_dicts, S)
    return p


def penalty_minimal_stay(trains_timing, k, k1, jsd_dicts , S):
    """
    Helper for P_minimal_stay


    Returns 0.0 or 1.0 as the contribution to Qmat[k, k1]
    """
    j = jsd_dicts[k]["j"]

    if j == jsd_dicts[k1]["j"]:
        sp = jsd_dicts[k]["s"]
        s = jsd_dicts[k1]["s"]
        if s == subsequent_station(S[j], sp):
            LHS = jsd_dicts[k1]["d"]
            LHS += earliest_dep_time(S, trains_timing, j, s)

            RHS = jsd_dicts[k]["d"]
            RHS += earliest_dep_time(S, trains_timing, j, sp)
            RHS += tau(
                trains_timing, "pass", first_train=j, first_station=sp, second_station=s
            )
            RHS += tau(trains_timing, "stop", first_train=j, first_station=s)

            if LHS < RHS:
                return 1.0
    return 0.0


def P_rolling_stock_circulation(trains_timing, k, k1, inds, trains_paths):
    """
    Rolling stock circulation condition - Eq. (45)

    Returns 0.0 or 1.0, i.e. not weighted contribution to Qmat[k, k1] and Qmat[k1, k]

    Input:
    - trains_timing - dict
    - trains_paths -- dict
    - k, k1 -- indices
    - jsd_dicts -- vector {"j": j, "s": s, "d": d}
      of trains, stations, delays tied to index k ot k1

    """
    p = penalty_rolling_stock(trains_timing, k, k1, inds, trains_paths)
    p += penalty_rolling_stock(trains_timing, k1, k, inds, trains_paths)
    return p


def penalty_rolling_stock(trains_timing, k, k1, inds, trains_paths):
    """
    Helper for P_rolling_stock_circulation

    Returns 0.0 or 1.0 as the contribution to Qmat[k, k1]
    """
    S = trains_paths["Paths"]
    j = inds[k]["j"]
    j1 = inds[k1]["j"]
    s = inds[k]["s"]
    s1 = inds[k1]["s"]

    if s1 in trains_paths["Jround"].keys():
        if previous_station(S[j], s1) == s:
            if [j, j1] in trains_paths["Jround"][s1]:
                LHS = inds[k]["d"] + earliest_dep_time(S, trains_timing, j, s)
                LHS += tau(trains_timing, "prep", first_train=j1, first_station=s1)
                LHS += tau(
                    trains_timing, "pass", first_train=j, first_station=s, second_station=s1
                )
                RHS = inds[k1]["d"] + earliest_dep_time(S, trains_timing, j1, s1)
                if LHS > RHS:
                    return 1.0
    return 0.0


def P_switch_occupation(trains_timing, k, k1, inds, trains_paths):
    """
    Switch occupancy condition - Eq. (46)

    Returns 0.0 or 1.0, i.e. not weighted contribution to Qmat[k, k1] and Qmat[k1, k]

    Input:
    - trains_timing - dict
    - trains_paths -- dict
    - k, k1 -- indices
    - jsd_dicts -- vector {"j": j, "s": s, "d": d}
      of trains, stations, delays tied to index k ot k1

    j1 -> --------------
    [s1]                .
    j2 -> -------------- c ----
                          .  [s2]
                           .......
    """

    S = trains_paths["Paths"]
    jp = inds[k]["j"]
    jpp = inds[k1]["j"]
    sp = inds[k]["s"]
    spp = inds[k1]["s"]

    if not_the_same_rolling_stock(jp, jpp, trains_paths): # train can not collide with itself

        for s in trains_paths["Jswitch"].keys():
            for pairs_of_switch in trains_paths["Jswitch"][s]:
                if [jp, jpp] == list(pairs_of_switch.keys()) or [jpp, jp] == list(
                    pairs_of_switch.keys()
                ):  # here is symmetrisation
                    if sp == departure_station4switches(
                        s, jp, pairs_of_switch, trains_paths
                    ):
                        if spp == departure_station4switches(
                            s, jpp, pairs_of_switch, trains_paths
                        ):

                            p = penalty_switch(
                                s, sp, spp, jp, jpp, trains_timing, k, k1, inds, trains_paths
                            )
                            if p > 0:
                                return p

    return 0.0



def penalty_switch(s, sp, spp, jp, jpp, trains_timing, k, k1, inds, trains_paths):
    """
    helper for P_switch_occupation


    Returns 0.0 or 1.0 as the contribution to Qmat[k, k1]
    """
    S = trains_paths["Paths"]

    t = inds[k]["d"] + earliest_dep_time(S, trains_timing, jp, sp)
    if s != sp:
        t += tau(trains_timing, "pass", first_train=jp, first_station=sp, second_station=s)

    t1 = inds[k1]["d"] + earliest_dep_time(S, trains_timing, jpp, spp)
    if s != spp:
        t1 += tau(
            trains_timing, "pass", first_train=jpp, first_station=spp, second_station=s
        )

    if -tau(trains_timing, "res") < t1 - t < tau(trains_timing, "res"):
        return 1.0
    return 0.0


##### track occupancy condition ####

def z_indices(trains_paths, d_max):
    """
    auxiliary indexing for decomposition of qubic term, for track occupation condition

    returns vector of dicts of two trains (j, j1)  at common stations (s)
    at delays (d, d1) in the form :
    {"j": j, "j1": j1, "s": s, "d": d, "d1": d1}
    """
    jsd_dicts = []
    for s in trains_paths["Jtrack"].keys():
        for js in trains_paths["Jtrack"][s]:
            for (j, j1) in itertools.combinations(js, 2):
                if not_the_same_rolling_stock(j, j1, trains_paths):
                    for d in range(d_max + 1):
                        for d1 in range(d_max + 1):
                            jsd_dicts.append({"j": j, "j1": j1, "s": s, "d": d, "d1": d1})
    return jsd_dicts, len(jsd_dicts)

def P1qubic(trains_timing, k, k1, jsd_dicts, trains_paths):
    """
    Single track occupation at station condition, part 1 with no interactions with
    auxiliary variables

    Returns not weighted contribution to Qmat at indices k and k1,
    symmetrised Qmat approach

    Input:
    trains_timing -- time trains_timing

    k, k1 -- indexes on the Q matrix

    jsd_dicts -- vector of {"j": j, "j1": j1, "s": s, "d": d, "d1": d1}
    form z_indices and {"j": j, "s": s, "d": d}  form indexing4qubo

    trains_paths -- train set dict containing trains paths

    """
    S = trains_paths["Paths"]
    # if trains have the same rolling stock we are not checking
    if not not_the_same_rolling_stock(jsd_dicts[k]["j"], jsd_dicts[k1]["j"], trains_paths):
        return 0.0

    if len(jsd_dicts[k].keys()) == 3 and len(jsd_dicts[k1].keys()) == 5:
        return pair_of_one_track_constrains(jsd_dicts, k, k1, trains_paths, trains_timing)

    elif len(jsd_dicts[k].keys()) == 5 and len(jsd_dicts[k1].keys()) == 3:
        return pair_of_one_track_constrains(jsd_dicts, k1, k, trains_paths, trains_timing)

    return 0.0


def pair_of_one_track_constrains(jsd_dicts, k, k1, trains_paths, trains_timing):
    """ hepler for P1qubic(trains_timing, k, k1, jsd_dicts, trains_paths) """

    S = trains_paths["Paths"]

    jx = jsd_dicts[k]["j"]
    sx = jsd_dicts[k]["s"]
    sz = jsd_dicts[k1]["s"]
    d = jsd_dicts[k]["d"]
    d1 = jsd_dicts[k1]["d"]
    d2 = jsd_dicts[k1]["d1"]

    if sz == subsequent_station(S[jx], sx):
        jz = jsd_dicts[k1]["j"]
        jz1 = jsd_dicts[k1]["j1"]

        j_rr = previous_train_from_Jround(trains_paths, jz, sz)

        if j_rr is None: # this is sophasticated exclusion, perhaps we will remove it

            if (jx == jz) and occurs_as_pair(jx, jz1, trains_paths["Jtrack"][sz]):
                # jz, jz1, jx => j', j, j', according to Eq 32
                # tz, tz1, tx => t', t,  t'' according to Eq 32
                # sx, sz -> s', s

                p = one_track_constrains(
                    jx, jz, jz1, sx, sz, d, d1, d2, trains_paths, trains_timing
                )
                if p > 0:
                    return p

        elif (j_rr == jz) and occurs_as_pair(j_rr, jz1, trains_paths["Jtrack"][sz]):

            p = one_track_constrains(
                    j_rr, jz, jz1, sx, sz, d, d1, d2, trains_paths, trains_timing
            )
            if p > 0:
                return p

        j_rr = previous_train_from_Jround(trains_paths, jz1, sz)

        if j_rr is None: # this is sophasticated exclusion, perhaps we will remove it

            if (jx == jz1) and occurs_as_pair(jx, jz, trains_paths["Jtrack"][sz]):
                # jz1, jz, tx => j', j, j', according to Eq 32
                # tz1, tz, tx => t', t,  t'' according to Eq 32
                # sx, sz -> s', s

                p = one_track_constrains(
                    jx, jz1, jz, sx, sz, d, d2, d1, trains_paths, trains_timing
                )
                if p > 0:
                    return p


        elif (j_rr == jz1) and occurs_as_pair(j_rr, jz, trains_paths["Jtrack"][sz]):


            p = one_track_constrains(
                    j_rr, jz1, jz, sx, sz, d, d2, d1, trains_paths, trains_timing
            )
            if p > 0:
                return p

    return 0


def one_track_constrains(jx, jz, jz1, sx, sz, d, d1, d2, trains_paths, trains_timing):
    """ hepler to
    pair_of_one_track_constrains(jsd_dicts, k, k1, trains_paths, trains_timing)
    """
    S = trains_paths["Paths"]

    tx = d + earliest_dep_time(S, trains_timing, jx, sx)
    tx += tau(trains_timing, "pass", first_train=jx, first_station=sx, second_station=sz)
    if "add_swithes_at_s" in trains_paths.keys():
        if (
            sz in trains_paths["add_swithes_at_s"]
        ):  # this is the approximation used in  ArXiv:2107.03234,
            tx -= tau(trains_timing, "res")
    tz = d1 + earliest_dep_time(S, trains_timing, jz, sz)
    tz1 = d2 + earliest_dep_time(S, trains_timing, jz1, sz)

    if tx < tz1 <= tz:
        return 1.0
    return 0.0




def P2qubic(k, k1, jsd_dicts, trains_paths):
    """
    Single track occupation at station condition, part 2
    the Rosenberg polynomial approach

    Returns not weighted contribution to Qmat at indices k and k1,
    symmetrised Qmat approach

    Input:
    trains_timing -- time trains_timing

    k, k1 -- indexes on the Q matrix

    jsd_dicts -- vector of {"j": j, "j1": j1, "s": s, "d": d, "d1": d1}

    form z_indices and {"j": j, "s": s, "d": d}  form indexing4qubo

    trains_paths -- train set dict containing trains paths

    """
    S = trains_paths["Paths"]

    # diagonal for z-ts
    if len(jsd_dicts[k].keys()) == len(jsd_dicts[k1].keys()) == 5:
        if k == k1:
            return 3.0
    # x vs z
    if len(jsd_dicts[k].keys()) == 3 and len(jsd_dicts[k1].keys()) == 5:
        jx = jsd_dicts[k]["j"]
        sx = jsd_dicts[k]["s"]
        sz = jsd_dicts[k1]["s"]
        if sz == sx:
            jz = jsd_dicts[k1]["j"]
            jz1 = jsd_dicts[k1]["j1"]

            # -1 because of the symmetrisation
            if jx == jz:
                if jsd_dicts[k]["d"] == jsd_dicts[k1]["d"]:
                    return -1.0
            if jx == jz1:
                if jsd_dicts[k]["d"] == jsd_dicts[k1]["d1"]:
                    return -1.0

    # z vs x
    if len(jsd_dicts[k].keys()) == 5 and len(jsd_dicts[k1].keys()) == 3:
        jx = jsd_dicts[k1]["j"]
        sx = jsd_dicts[k1]["s"]
        sz = jsd_dicts[k]["s"]
        if sz == sx:
            jz = jsd_dicts[k]["j"]
            jz1 = jsd_dicts[k]["j1"]
            if jx == jz:
                if jsd_dicts[k1]["d"] == jsd_dicts[k]["d"]:
                    return -1.0
            if jx == jz1:
                if jsd_dicts[k1]["d"] == jsd_dicts[k]["d1"]:
                    return -1.0
    # x vs x
    if len(jsd_dicts[k].keys()) == 3 and len(jsd_dicts[k1].keys()) == 3:
        s = jsd_dicts[k]["s"]
        if s == jsd_dicts[k1]["s"]:
            j = jsd_dicts[k]["j"]
            j1 = jsd_dicts[k1]["j"]
            sz = subsequent_station(S[j], s)
            if s in trains_paths["Jtrack"].keys():
                if occurs_as_pair(j, j1, trains_paths["Jtrack"][s]):
                    return 0.5
    return 0.0



# panalties and objective

def penalty(trains_timing, k, jsd_dicts, d_max):
    """returns weighted contribution to Qmat  at k (diagnal)
    from the penalties on delays

    Input:
    trains_timing -- time trains_timing
    k -- index on the Q matrix
    jsd_dicts -- vector of {"j": j, "s": s, "d": d}  form indexing4qubo
    dmax -- maximal secondary delay
    """
    j = jsd_dicts[k]["j"]
    s = jsd_dicts[k]["s"]
    w = penalty_weights(trains_timing, j, s) / d_max
    return jsd_dicts[k]["d"] * w


def get_coupling(trains_timing, k, k1, trains_paths, jsd_dicts, p_sum, p_pair):
    """ returns weighted hard constrains contributions to Qmat at k,k1 in the
    case where no auxiliary variables
    - headway ,
    minimal stay,

    Input:
    trains_timing -- time trains_timing
    k, k1 -- indexes on the Q matrix
    trains_paths -- train set dict containing trains paths
    jsd_dicts -- vector of {"j": j, "s": s, "d": d}  form indexing4qubo
    p_sum -- weight for sum to one constrain
    p_pair -- weight for quadratic constrains
    """
    # each train leave each station onse and only once
    J = p_sum * P_sum(k, k1, jsd_dicts)
    # quadratic conditions
    J += p_pair * P_headway(trains_timing, k, k1, jsd_dicts, trains_paths)
    J += p_pair * P_minimal_stay(trains_timing, k, k1, jsd_dicts, trains_paths)
    J += p_pair * P_single_track_line(trains_timing, k, k1, jsd_dicts, trains_paths)
    J += p_pair * P_rolling_stock_circulation(trains_timing, k, k1, jsd_dicts, trains_paths)
    J += p_pair * P_switch_occupation(trains_timing, k, k1, jsd_dicts, trains_paths)
    return J


def get_z_coupling(trains_timing, k, k1, trains_paths, jsd_dicts, p_pair, p_qubic):
    """ returns weighted hard constrains contributions to Qmat at k,k1 in the
    case where auxiliary variables are included, i.e. in the single track
    occupancy at station case.

    Input:
    trains_timing -- time trains_timing
    k, k1 -- indexes on the Q matrix
    trains_paths -- train set dict containing trains paths
    jsd_dicts -- vector of {"j": j, "s": s, "d": d}  form indexing4qubo
    p_pair -- weight for quadratic constrains
    p_qubic -- weight for qubic constrains
    """
    J = p_pair * P1qubic(trains_timing, k, k1, jsd_dicts, trains_paths)
    J += p_qubic * P2qubic(k, k1, jsd_dicts, trains_paths)
    return J


def make_Q(trains_paths, trains_timing, d_max, p_sum, p_pair, p_pair_q, p_qubic):
    """returns symmetric Q matrix for the particular problem encoded in
    trains_paths and trains_timing

    Parameters
    dmax -- maximal secondary delay
    p_sum -- panalty for ∑_i x_i = 1 hard constrains
    p_pair -- penalty for ∑_i,j x_i x_j = 0 hard constrains

    p_pair_q -- weight for quadratic constrains for the single track
    occupancy at station
    p_qubic -- weight for qubic constrains for the single track
    occupancy at station
    """
    inds, q_bits = indexing4qubo(trains_paths, d_max) # indices of vars
    inds_z, q_bits_z = z_indices(trains_paths, d_max) # indices of auxiliary vars.

    inds1 = np.concatenate([inds, inds_z])

    l = q_bits
    l1 = q_bits + q_bits_z

    Q = [[0.0 for _ in range(l1)] for _ in range(l1)]

    # add soft panalties (objective)
    for k in range(l):
        Q[k][k] += penalty(trains_timing, k, inds, d_max)
    # quadratic headway, stay, single_line, corculation, switch
    for k in range(l):
        for k1 in range(l):
            Q[k][k1] += get_coupling(trains_timing, k, k1, trains_paths, inds, p_sum, p_pair)
    # qubic track occupancy condition.
    for k in range(l1):
        for k1 in range(l1):
            Q[k][k1] += get_z_coupling(
                trains_timing, k, k1, trains_paths, inds1, p_pair_q, p_qubic
            )
    return Q
