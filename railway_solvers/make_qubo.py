import itertools

import numpy as np

from .helpers_functions import *

# this is the direct QUBO / HOBO implemntation for arXiv:2107.03234
# there is no BQM / CQM approach
# I want to leave this comparison

def indexing4qubo(train_sets, d_max):
    """returns vector of dicts of trains stations and delays
     in the form {"j": j, "s": s, "d": d}

     the index of vector od these correspond to the index in Q matrix
    """

    S = train_sets["Paths"]
    inds = []
    for j in train_sets["J"]:
        for s in S[j]:
            if not skip_station(j,s, train_sets):
                for d in range(d_max + 1):
                    inds.append({"j": j, "s": s, "d": d})
    return inds, len(inds)


# constrains

def Psum(k, k1, jsd_dicts):
    """sum to one constrain

    returns the not wieghted contribution from the  ∑_i x_i  = 1 constrain
    to Qmat at indices k and k1

    Input:
    k, k1 -- indexes on the Q matrix
    jsd_dicts -- vector of {"j": j, "s": s, "d": d}  form indexing4qubo
    """
    if jsd_dicts[k]["j"] == jsd_dicts[k1]["j"] and jsd_dicts[k]["s"] == jsd_dicts[k1]["s"]:
        if jsd_dicts[k]["d"] == jsd_dicts[k1]["d"]:
            return -1.0
        else:
            return 1.0
    return 0.0


def Pspan(timetable, k, k1, jsd_dicts, train_sets):
    """minimal span constrain
    returns not weighted contribution to Qmat at indices k and k1,
    symmetrised Qmat approach

    Input:
    timetable -- time timetable
    k, k1 -- indexes on the Q matrix
    jsd_dicts -- vector of {"j": j, "s": s, "d": d}  form indexing4qubo
    train_sets -- train set dict containing trains paths

    [s1] ..... j1 -> ....... j2 -> ..... [s2]
                      span
    """

    S = train_sets["Paths"]
    j = jsd_dicts[k]["j"]
    j1 = jsd_dicts[k1]["j"]
    s = jsd_dicts[k]["s"]
    s1 = jsd_dicts[k1]["s"]

    s_next = subsequent_station(S[j], s)

    if s == s1 and s_next != None and s_next == subsequent_station(S[j1], s1):

        if s in train_sets["Jd"].keys():
            if s_next in train_sets["Jd"][s].keys():
                if occurs_as_pair(j, j1, train_sets["Jd"][s][s_next]):

                    t = jsd_dicts[k]["d"] + earliest_dep_time(S, timetable, j, s)
                    t1 = jsd_dicts[k1]["d"] + earliest_dep_time(S, timetable, j1, s)

                    A = -tau(
                        timetable,
                        "headway",
                        first_train=j1,
                        second_train=j,
                        first_station=s,
                        second_station=s_next,
                    )

                    B = tau(
                        timetable,
                        "headway",
                        first_train=j,
                        second_train=j1,
                        first_station=s,
                        second_station=s_next,
                    )

                    if A < t1 - t < B:
                        return 1.0
    return 0.0


def P1track(timetable, k, k1, jsd_dicts, train_sets):
    """single track line and deadlock constrain
    returns not weighted contribution to Qmat at indices k and k1,
    symmetrised Qmat approach

    Input:
    timetable -- time timetable
    k, k1 -- indexes on the Q matrix
    jsd_dicts -- vector of {"j": j, "s": s, "d": d}  form indexing4qubo
    train_sets -- train set dict containing trains paths

         ......                            ... <-j2 ..
        [s1]    .                        .      [s2]
       ..j1 ->.......................................

     """

    p = penalty_single_track_condition(timetable, k, k1, jsd_dicts, train_sets)
    p += penalty_single_track_condition(timetable, k1, k, jsd_dicts, train_sets)
    return p

def penalty_single_track_condition(timetable, k, k1, jsd_dicts, train_sets):
    """helper for P1track(timetable, k, k1, jsd_dicts, train_sets)"""
    S = train_sets["Paths"]
    j = jsd_dicts[k]["j"]
    j1 = jsd_dicts[k1]["j"]
    s = jsd_dicts[k]["s"]
    s1 = jsd_dicts[k1]["s"]

    if not_the_same_rolling_stock(j, j1, train_sets):

        if (s, s1) in train_sets["Josingle"].keys() and [j, j1] in train_sets[
            "Josingle"
        ][(s, s1)]:
            t = jsd_dicts[k]["d"] + earliest_dep_time(S, timetable, j, s)
            t2 = t
            t1 = jsd_dicts[k1]["d"] + earliest_dep_time(S, timetable, j1, s1)

            t += -tau(
                timetable, "pass", first_train=j1, first_station=s1, second_station=s
            )
            t2 += tau(
                timetable, "pass", first_train=j, first_station=s, second_station=s1
            )

            if t < t1 < t2:
                return 1.0
    return 0.0


def Pstay(timetable, k, k1, jsd_dicts, train_sets):
    """minimal stay constrain

    returns not weighted contribution to Qmat at indices k and k1,
    symmetrised Qmat approach

    Input:
    timetable -- time timetable
    k, k1 -- indexes on the Q matrix
    jsd_dicts -- vector of {"j": j, "s": s, "d": d}  form indexing4qubo
    train_sets -- train set dict containing trains paths

    """
    S = train_sets["Paths"]
    p = penalty_for_minimal_stay_condition(timetable, k, k1, jsd_dicts, S)
    p += penalty_for_minimal_stay_condition(timetable, k1, k, jsd_dicts, S)
    return p


def penalty_for_minimal_stay_condition(timetable, k, k1, jsd_dicts , S):
    """ helper for Pstay(timetable, k, k1, jsd_dicts, train_sets)"""
    j = jsd_dicts[k]["j"]

    if j == jsd_dicts[k1]["j"]:
        sp = jsd_dicts[k]["s"]
        s = jsd_dicts[k1]["s"]
        if s == subsequent_station(S[j], sp):
            LHS = jsd_dicts[k1]["d"]
            LHS += earliest_dep_time(S, timetable, j, s)

            RHS = jsd_dicts[k]["d"]
            RHS += earliest_dep_time(S, timetable, j, sp)
            RHS += tau(
                timetable, "pass", first_train=j, first_station=sp, second_station=s
            )
            RHS += tau(timetable, "stop", first_train=j, first_station=s)

            if LHS < RHS:  # timetable is ensured by nono-zero delay
                return 1.0
    return 0.0


def Pcirc(timetable, k, k1, inds, train_sets):
    """ rolling stock circulation condition

    returns not weighted contribution to Qmat at indices k and k1,
    symmetrised Qmat approach

    Input:
    timetable -- time timetable
    k, k1 -- indexes on the Q matrix
    jsd_dicts -- vector of {"j": j, "s": s, "d": d}  form indexing4qubo
    train_sets -- train set dict containing trains paths

    """
    p = p_circ(timetable, k, k1, inds, train_sets)
    p += p_circ(timetable, k1, k, inds, train_sets)
    return p


def p_circ(timetable, k, k1, inds, train_sets):
    """helper for Pcirc(timetable, k, k1, inds, train_sets) """
    S = train_sets["Paths"]
    j = inds[k]["j"]
    j1 = inds[k1]["j"]
    s = inds[k]["s"]
    s1 = inds[k1]["s"]

    if s1 in train_sets["Jround"].keys():
        if previous_station(S[j], s1) == s:
            if [j, j1] in train_sets["Jround"][s1]:
                LHS = inds[k]["d"] + earliest_dep_time(S, timetable, j, s)
                LHS += tau(timetable, "prep", first_train=j1, first_station=s1)
                LHS += tau(
                    timetable, "pass", first_train=j, first_station=s, second_station=s1
                )
                RHS = inds[k1]["d"] + earliest_dep_time(S, timetable, j1, s1)
                if LHS > RHS:
                    return 1.0
    return 0.0


def Pswitch(timetable, k, k1, inds, train_sets):
    """switch occupancy condition

    returns not weighted contribution to Qmat at indices k and k1,
    symmetrised Qmat approach

    Input:
    timetable -- time timetable
    k, k1 -- indexes on the Q matrix
    jsd_dicts -- vector of {"j": j, "s": s, "d": d}  form indexing4qubo
    train_sets -- train set dict containing trains paths

    j1 -> --------------
    [s1]                .
    j2 -> -------------- c ----
                          .  [s2]
                           .......
    """

    S = train_sets["Paths"]
    jp = inds[k]["j"]
    jpp = inds[k1]["j"]
    sp = inds[k]["s"]
    spp = inds[k1]["s"]

    if not_the_same_rolling_stock(jp, jpp, train_sets):

        for s in train_sets["Jswitch"].keys():
            for pairs_of_switch in train_sets["Jswitch"][s]:
                if [jp, jpp] == list(pairs_of_switch.keys()) or [jpp, jp] == list(
                    pairs_of_switch.keys()
                ):  # here is symmetrisation
                    if sp == departure_station4switches(
                        s, jp, pairs_of_switch, train_sets
                    ):
                        if spp == departure_station4switches(
                            s, jpp, pairs_of_switch, train_sets
                        ):

                            p = p_switch(
                                s, sp, spp, jp, jpp, timetable, k, k1, inds, train_sets
                            )
                            if p > 0:
                                return p

    return 0.0



def p_switch(s, sp, spp, jp, jpp, timetable, k, k1, inds, train_sets):
    """ helper for Pswitch(timetable, k, k1, inds, train_sets) """
    S = train_sets["Paths"]

    t = inds[k]["d"] + earliest_dep_time(S, timetable, jp, sp)
    if s != sp:
        t += tau(timetable, "pass", first_train=jp, first_station=sp, second_station=s)

    t1 = inds[k1]["d"] + earliest_dep_time(S, timetable, jpp, spp)
    if s != spp:
        t1 += tau(
            timetable, "pass", first_train=jpp, first_station=spp, second_station=s
        )

    if -tau(timetable, "res") < t1 - t < tau(timetable, "res"):
        return 1.0
    return 0.0


# single track occupation at station condition

def z_indices(train_sets, d_max):
    """ returns vector of dicts of two trains (j, j1)  at common stations (s)
    at delays (d, d1) in the form :
    {"j": j, "j1": j1, "s": s, "d": d, "d1": d1}

    indexing is consitent with auxiliary variable used to decompose 3'rd
    order terms used to handle track occupancy condition

    """
    jsd_dicts = []
    for s in train_sets["Jtrack"].keys():
        for js in train_sets["Jtrack"][s]:
            for (j, j1) in itertools.combinations(js, 2):
                if not_the_same_rolling_stock(j, j1, train_sets):
                    for d in range(d_max + 1):
                        for d1 in range(d_max + 1):
                            jsd_dicts.append({"j": j, "j1": j1, "s": s, "d": d, "d1": d1})
    return jsd_dicts, len(jsd_dicts)

def P1qubic(timetable, k, k1, jsd_dicts, train_sets):
    """
    Single track occupation at station condition, part 1 with no interactions with
    auxiliary variables

    Returns not weighted contribution to Qmat at indices k and k1,
    symmetrised Qmat approach

    Input:
    timetable -- time timetable

    k, k1 -- indexes on the Q matrix

    jsd_dicts -- vector of {"j": j, "j1": j1, "s": s, "d": d, "d1": d1}
    form z_indices and {"j": j, "s": s, "d": d}  form indexing4qubo

    train_sets -- train set dict containing trains paths

    """
    S = train_sets["Paths"]
    # if trains have the same rolling stock we are not checking
    if not not_the_same_rolling_stock(jsd_dicts[k]["j"], jsd_dicts[k1]["j"], train_sets):
        return 0.0

    if len(jsd_dicts[k].keys()) == 3 and len(jsd_dicts[k1].keys()) == 5:
        return pair_of_one_track_constrains(jsd_dicts, k, k1, train_sets, timetable)

    elif len(jsd_dicts[k].keys()) == 5 and len(jsd_dicts[k1].keys()) == 3:
        return pair_of_one_track_constrains(jsd_dicts, k1, k, train_sets, timetable)

    return 0.0


def pair_of_one_track_constrains(jsd_dicts, k, k1, train_sets, timetable):
    """ hepler for P1qubic(timetable, k, k1, jsd_dicts, train_sets) """

    S = train_sets["Paths"]

    jx = jsd_dicts[k]["j"]
    sx = jsd_dicts[k]["s"]
    sz = jsd_dicts[k1]["s"]
    d = jsd_dicts[k]["d"]
    d1 = jsd_dicts[k1]["d"]
    d2 = jsd_dicts[k1]["d1"]

    if sz == subsequent_station(S[jx], sx):
        jz = jsd_dicts[k1]["j"]
        jz1 = jsd_dicts[k1]["j1"]

        j_rr = previous_train_from_Jround(train_sets, jz, sz)

        if j_rr is None: # this is sophasticated exclusion, perhaps we will remove it

            if (jx == jz) and occurs_as_pair(jx, jz1, train_sets["Jtrack"][sz]):
                # jz, jz1, jx => j', j, j', according to Eq 32
                # tz, tz1, tx => t', t,  t'' according to Eq 32
                # sx, sz -> s', s

                p = one_track_constrains(
                    jx, jz, jz1, sx, sz, d, d1, d2, train_sets, timetable
                )
                if p > 0:
                    return p

        elif (j_rr == jz) and occurs_as_pair(j_rr, jz1, train_sets["Jtrack"][sz]):

            p = one_track_constrains(
                    j_rr, jz, jz1, sx, sz, d, d1, d2, train_sets, timetable
            )
            if p > 0:
                return p

        j_rr = previous_train_from_Jround(train_sets, jz1, sz)

        if j_rr is None: # this is sophasticated exclusion, perhaps we will remove it

            if (jx == jz1) and occurs_as_pair(jx, jz, train_sets["Jtrack"][sz]):
                # jz1, jz, tx => j', j, j', according to Eq 32
                # tz1, tz, tx => t', t,  t'' according to Eq 32
                # sx, sz -> s', s

                p = one_track_constrains(
                    jx, jz1, jz, sx, sz, d, d2, d1, train_sets, timetable
                )
                if p > 0:
                    return p


        elif (j_rr == jz1) and occurs_as_pair(j_rr, jz, train_sets["Jtrack"][sz]):


            p = one_track_constrains(
                    j_rr, jz1, jz, sx, sz, d, d2, d1, train_sets, timetable
            )
            if p > 0:
                return p

    return 0


def one_track_constrains(jx, jz, jz1, sx, sz, d, d1, d2, train_sets, timetable):
    """ hepler to
    pair_of_one_track_constrains(jsd_dicts, k, k1, train_sets, timetable)
    """
    S = train_sets["Paths"]

    tx = d + earliest_dep_time(S, timetable, jx, sx)
    tx += tau(timetable, "pass", first_train=jx, first_station=sx, second_station=sz)
    if "add_swithes_at_s" in train_sets.keys():
        if (
            sz in train_sets["add_swithes_at_s"]
        ):  # this is the approximation used in  ArXiv:2107.03234,
            tx -= tau(timetable, "res")
    tz = d1 + earliest_dep_time(S, timetable, jz, sz)
    tz1 = d2 + earliest_dep_time(S, timetable, jz1, sz)

    if tx < tz1 <= tz:
        return 1.0
    return 0.0




def P2qubic(k, k1, jsd_dicts, train_sets):
    """
    Single track occupation at station condition, part 2
    the Rosenberg polynomial approach

    Returns not weighted contribution to Qmat at indices k and k1,
    symmetrised Qmat approach

    Input:
    timetable -- time timetable

    k, k1 -- indexes on the Q matrix

    jsd_dicts -- vector of {"j": j, "j1": j1, "s": s, "d": d, "d1": d1}

    form z_indices and {"j": j, "s": s, "d": d}  form indexing4qubo

    train_sets -- train set dict containing trains paths

    """
    S = train_sets["Paths"]

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
            if s in train_sets["Jtrack"].keys():
                if occurs_as_pair(j, j1, train_sets["Jtrack"][s]):
                    return 0.5
    return 0.0



# panalties and objective

def penalty(timetable, k, jsd_dicts, d_max):
    """returns weighted contribution to Qmat  at k (diagnal)
    from the penalties on delays

    Input:
    timetable -- time timetable
    k -- index on the Q matrix
    jsd_dicts -- vector of {"j": j, "s": s, "d": d}  form indexing4qubo
    dmax -- maximal secondary delay
    """
    j = jsd_dicts[k]["j"]
    s = jsd_dicts[k]["s"]
    w = penalty_weights(timetable, j, s) / d_max
    return jsd_dicts[k]["d"] * w


def get_coupling(timetable, k, k1, train_sets, jsd_dicts, p_sum, p_pair):
    """ returns weighted hard constrains contributions to Qmat at k,k1 in the
    case where no auxiliary variables are included, i.e. no single track
    occupancy at station

    Input:
    timetable -- time timetable
    k, k1 -- indexes on the Q matrix
    train_sets -- train set dict containing trains paths
    jsd_dicts -- vector of {"j": j, "s": s, "d": d}  form indexing4qubo
    p_sum -- weight for sum to one constrain
    p_pair -- weight for quadratic constrains
    """
    J = p_sum * Psum(k, k1, jsd_dicts)
    J += p_pair * Pspan(timetable, k, k1, jsd_dicts, train_sets)
    J += p_pair * Pstay(timetable, k, k1, jsd_dicts, train_sets)
    J += p_pair * P1track(timetable, k, k1, jsd_dicts, train_sets)
    J += p_pair * Pcirc(timetable, k, k1, jsd_dicts, train_sets)
    J += p_pair * Pswitch(timetable, k, k1, jsd_dicts, train_sets)
    return J


def get_z_coupling(timetable, k, k1, train_sets, jsd_dicts, p_pair, p_qubic):
    """ returns weighted hard constrains contributions to Qmat at k,k1 in the
    case where auxiliary variables are included, i.e. in the single track
    occupancy at station case.

    Input:
    timetable -- time timetable
    k, k1 -- indexes on the Q matrix
    train_sets -- train set dict containing trains paths
    jsd_dicts -- vector of {"j": j, "s": s, "d": d}  form indexing4qubo
    p_pair -- weight for quadratic constrains
    p_qubic -- weight for qubic constrains
    """
    J = p_pair * P1qubic(timetable, k, k1, jsd_dicts, train_sets)
    J += p_qubic * P2qubic(k, k1, jsd_dicts, train_sets)
    return J


def make_Q(train_sets, timetable, d_max, p_sum, p_pair, p_pair_q, p_qubic):
    """returns symmetric Q matrix for the particular problem encoded in
    train_sets and timetable

    Parameters
    dmax -- maximal secondary delay
    p_sum -- weight for sum to one constrain
    p_pair -- weight for quadratic constrains
    p_pair_q -- weight for quadratic constrains for the single track
    occupancy at station
    p_qubic -- weight for qubic constrains for the single track
    occupancy at station
    """
    inds, q_bits = indexing4qubo(train_sets, d_max)
    inds_z, q_bits_z = z_indices(train_sets, d_max)

    inds1 = np.concatenate([inds, inds_z])

    l = q_bits
    l1 = q_bits + q_bits_z

    Q = [[0.0 for _ in range(l1)] for _ in range(l1)]

    for k in range(l):
        Q[k][k] += penalty(timetable, k, inds, d_max)
    for k in range(l):
        for k1 in range(l):
            Q[k][k1] += get_coupling(timetable, k, k1, train_sets, inds, p_sum, p_pair)
    for k in range(l1):
        for k1 in range(l1):
            Q[k][k1] += get_z_coupling(
                timetable, k, k1, train_sets, inds1, p_pair_q, p_qubic
            )
    return Q
