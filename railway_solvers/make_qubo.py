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

    returns not wieghted (by peanlty constant) contribution from ∑_i x_i  = 1
    constrain to Qmat[k, k1]

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


def P_headway(k, l, jsd_dicts, trains_timing, trains_paths):
    """
    Minimal headway condition - Eq. (42)

    Returns 0.0 or 1.0, i.e. not weighted contribution to Qmat[k, l]
    and Qmat[l, k]

    Input:
    - k, l -- indices
    - jsd_dicts -- vector {"j": j, "s": s, "d": d}
      of trains, stations, delays tied to index k or l
    - trains_timing - dict
    - trains_paths -- dict


     ..... j1 -> ....... j2 -> .......
    [s1]          headway         [s2]
    """

    S = trains_paths["Paths"]
    j = jsd_dicts[k]["j"]
    j1 = jsd_dicts[l]["j"]
    s = jsd_dicts[k]["s"]
    s1 = jsd_dicts[l]["s"]

    s_next = subsequent_station(S[j], s)

    if s == s1 and s_next != None and s_next == subsequent_station(S[j1], s1):

        if s in trains_paths["Jd"].keys():
            if s_next in trains_paths["Jd"][s].keys():
                if occurs_as_pair(j, j1, trains_paths["Jd"][s][s_next]):

                    t = jsd_dicts[k]["d"] + earliest_dep_time(S, trains_timing, j, s)
                    t1 = jsd_dicts[l]["d"] + earliest_dep_time(S, trains_timing, j1, s)

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


def P_single_track_line(k, l, jsd_dicts, trains_timing, trains_paths):
    """
    Single track line condition - Eq. (43)

    Returns 0.0 or 1.0, i.e. not weighted contribution to Qmat[k, l]
    and Qmat[l, k]

    Input:
    - k, l -- indices
    - jsd_dicts -- vector {"j": j, "s": s, "d": d}
      of trains, stations, delays tied to index k or l
    - trains_timing - dict
    - trains_paths -- dict

         ......                            ... <-j2 ..
        [s1]    .                        .      [s2]
       ..j1 ->.......................................

     """

    #symetrisation
    p = penalty_single_track(k, l, jsd_dicts, trains_timing, trains_paths)
    p += penalty_single_track(l, k, jsd_dicts, trains_timing, trains_paths)
    return p

def penalty_single_track(k, l, jsd_dicts, trains_timing, trains_paths):
    """
    Helper for P_single_track_line

    Returns 0.0 or 1.0 as the contribution to Qmat[k, l]
    """
    S = trains_paths["Paths"]
    j = jsd_dicts[k]["j"]
    j1 = jsd_dicts[l]["j"]
    s = jsd_dicts[k]["s"]
    s1 = jsd_dicts[l]["s"]

    if not_the_same_rolling_stock(j, j1, trains_paths):

        if (s, s1) in trains_paths["Josingle"].keys() and [j, j1] in trains_paths[
            "Josingle"
        ][(s, s1)]:
            t = jsd_dicts[k]["d"] + earliest_dep_time(S, trains_timing, j, s)
            t2 = t
            t1 = jsd_dicts[l]["d"] + earliest_dep_time(S, trains_timing, j1, s1)

            t += -tau(
                trains_timing, "pass", first_train=j1, first_station=s1, second_station=s
            )
            t2 += tau(
                trains_timing, "pass", first_train=j, first_station=s, second_station=s1
            )

            if t < t1 < t2:
                return 1.0
    return 0.0


def P_minimal_stay(k, l, jsd_dicts, trains_timing, trains_paths):
    """
    Minimal stay condition - Eq. (44)

    Returns 0.0 or 1.0, i.e. not weighted contribution to Qmat[k, l]
    and Qmat[l, k]

    Input:
    - k, l -- indices
    - jsd_dicts -- vector {"j": j, "s": s, "d": d}
      of trains, stations, delays tied to index k or l
    - trains_timing - dict
    - trains_paths -- dict

    """
    S = trains_paths["Paths"]
    p = penalty_minimal_stay(k, l, jsd_dicts, trains_timing, S)
    p += penalty_minimal_stay(l, k, jsd_dicts, trains_timing, S)
    return p


def penalty_minimal_stay(k, l, jsd_dicts, trains_timing, S):
    """
    Helper for P_minimal_stay


    Returns 0.0 or 1.0 as the contribution to Qmat[k, l]
    """
    j = jsd_dicts[k]["j"]

    if j == jsd_dicts[l]["j"]:
        sp = jsd_dicts[k]["s"]
        s = jsd_dicts[l]["s"]
        if s == subsequent_station(S[j], sp):
            LHS = jsd_dicts[l]["d"]
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


def P_rolling_stock_circulation(k, l, inds, trains_timing, trains_paths):
    """
    Rolling stock circulation condition - Eq. (45)

    Returns 0.0 or 1.0, i.e. not weighted contribution to Qmat[k, l]
    and Qmat[l, k]

    Input:
    - k, l -- indices
    - jsd_dicts -- vector {"j": j, "s": s, "d": d}
      of trains, stations, delays tied to index k or l
    - trains_timing - dict
    - trains_paths -- dict

    """
    p = penalty_rolling_stock(k, l, inds, trains_timing, trains_paths)
    p += penalty_rolling_stock(l, k, inds, trains_timing, trains_paths)
    return p


def penalty_rolling_stock(k, l, inds, trains_timing, trains_paths):
    """
    Helper for P_rolling_stock_circulation

    Returns 0.0 or 1.0 as the contribution to Qmat[k, l]
    """
    S = trains_paths["Paths"]
    j = inds[k]["j"]
    j1 = inds[l]["j"]
    s = inds[k]["s"]
    s1 = inds[l]["s"]

    if s1 in trains_paths["Jround"].keys():
        if previous_station(S[j], s1) == s:
            if [j, j1] in trains_paths["Jround"][s1]:
                LHS = inds[k]["d"] + earliest_dep_time(S, trains_timing, j, s)
                LHS += tau(trains_timing, "prep", first_train=j1, first_station=s1)
                LHS += tau(
                    trains_timing, "pass", first_train=j, first_station=s, second_station=s1
                )
                RHS = inds[l]["d"] + earliest_dep_time(S, trains_timing, j1, s1)
                if LHS > RHS:
                    return 1.0
    return 0.0


def P_switch_occupation(k, l, inds, trains_timing, trains_paths):
    """
    Switch occupancy condition - Eq. (46)

    Returns 0.0 or 1.0, i.e. not weighted contribution to Qmat[k, l]
    and Qmat[l, k]

    Input:
    - k, l -- indices
    - jsd_dicts -- vector {"j": j, "s": s, "d": d}
      of trains, stations, delays tied to index k or l
    - trains_timing - dict
    - trains_paths -- dict

    j1 -> --------------
    [s1]                .
    j2 -> -------------- c ----
                          .  [s2]
                           .......
    """

    S = trains_paths["Paths"]
    jp = inds[k]["j"]
    jpp = inds[l]["j"]
    sp = inds[k]["s"]
    spp = inds[l]["s"]

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
                                s, sp, spp, jp, jpp, k, l, inds, trains_timing, trains_paths
                            )
                            if p > 0:
                                return p

    return 0.0



def penalty_switch(s, sp, spp, jp, jpp, k, l, inds, trains_timing, trains_paths):
    """
    helper for P_switch_occupation


    Returns 0.0 or 1.0 as the contribution to Qmat[k, l]
    """
    S = trains_paths["Paths"]

    t = inds[k]["d"] + earliest_dep_time(S, trains_timing, jp, sp)
    if s != sp:
        t += tau(trains_timing, "pass", first_train=jp, first_station=sp, second_station=s)

    t1 = inds[l]["d"] + earliest_dep_time(S, trains_timing, jpp, spp)
    if s != spp:
        t1 += tau(
            trains_timing, "pass", first_train=jpp, first_station=spp, second_station=s
        )

    if -tau(trains_timing, "res") < t1 - t < tau(trains_timing, "res"):
        return 1.0
    return 0.0


##### track occupancy condition   - QUBO creation ####

def z_indices(trains_paths, d_max):
    """
    Auxiliary indexing for decomposition of qubic term,
    for track occupation condition

    Returns vector of dicts of 2 trains(j, j1) at delays(d, d1) at stations (s)

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


def P_track_occupation_condition_quadratic_part(k, k1, jsd_dicts, trains_timing, trains_paths):
    """
    A quadratic part of track occupartion condition, first term in Eq. (53)


    Returns not weighted contribution to Qmat[k, k1] = Qmat[k1, k]

    Input:
    - trains_timing -- dict
    - trains_paths -- dict
    - k, k1 -- indices
    - jsd_dicts -- vector of {"j": j, "j1": j1, "s": s, "d": d, "d1": d1}
    form z_indices and {"j": j, "s": s, "d": d}  form indexing4qubo


    j1 -> .............. j2 ->
    [s1]                  [s2]

    j1 can leave s1 in such time, that j2 has to reliese s2, before j1 arrives to s2

    """
    S = trains_paths["Paths"]
    # if trains have the same rolling stock we are not checking
    if not not_the_same_rolling_stock(jsd_dicts[k]["j"], jsd_dicts[k1]["j"], trains_paths):
        return 0.0

    if len(jsd_dicts[k].keys()) == 3 and len(jsd_dicts[k1].keys()) == 5:
        return pair_of_one_track_constrains(jsd_dicts, k, k1, trains_timing, trains_paths)

    elif len(jsd_dicts[k].keys()) == 5 and len(jsd_dicts[k1].keys()) == 3:
        return pair_of_one_track_constrains(jsd_dicts, k1, k, trains_timing, trains_paths)

    return 0.0


def pair_of_one_track_constrains(jsd_dicts, k, k1, trains_timing, trains_paths):
    """
    hepler for P_track_occupation_condition_quadratic_part


    """

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
                    jx, jz, jz1, sx, sz, d, d1, d2, trains_timing, trains_paths
                )
                if p > 0:
                    return p

        elif (j_rr == jz) and occurs_as_pair(j_rr, jz1, trains_paths["Jtrack"][sz]):

            p = one_track_constrains(
                    j_rr, jz, jz1, sx, sz, d, d1, d2, trains_timing, trains_paths
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
                    jx, jz1, jz, sx, sz, d, d2, d1, trains_timing, trains_paths
                )
                if p > 0:
                    return p


        elif (j_rr == jz1) and occurs_as_pair(j_rr, jz, trains_paths["Jtrack"][sz]):


            p = one_track_constrains(
                    j_rr, jz1, jz, sx, sz, d, d2, d1, trains_timing, trains_paths
            )
            if p > 0:
                return p

    return 0


def one_track_constrains(jx, jz, jz1, sx, sz, d, d1, d2, trains_timing, trains_paths):
    """
    hepler for pair_of_one_track_constrains

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



def P_Rosenberg_decomposition(k, k1, jsd_dicts, trains_paths):
    """
    The contribution to from Rosenberg decomposition of qubic term
    Eq. (52)


    Returns not weighted contribution to Qmat[k,k1]=Qmat[k1, k].
    Coificnets at k  ≠ k1 are divided by 2 because they are taken twice

    Input:
    - k, k1 -- indices of Qmat
    - jsd_dicts -- concatenated {"j": j, "s": s, "d": d}.... and
      {"j": j, "j1": j1, "s": s, "d": d, "d1": d1}....
      first part correspond to original varialbes second to auxiliary ones
      (pairs of that leaves common station at given delays)
    - trains_paths -- dict


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

            # -1 because in Eq. (52) it is taken twice due to the symmetrisation
            if jx == jz:
                if jsd_dicts[k]["d"] == jsd_dicts[k1]["d"]:
                    return -1.0
            if jx == jz1:
                if jsd_dicts[k]["d"] == jsd_dicts[k1]["d1"]:
                    return -1.0

    # z vs x
    # -1. 0 because in Eq. (52) it is taken twice due to the symmetrisation
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
    # 0.5 because in Eq. (52) it is taken twice due to the symmetrisation
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

def penalty(k, jsd_dicts, d_max, trains_timing):
    """
    Soft constrians,

    Returns weighted contribution to Qmat[k, k] drom objective

    Input:
    - trains_timing - dict
    - k -- index (of diagonal)
    - jsd_dicts -- vector {"j": j, "s": s, "d": d}
      of trains, stations, delays tied to index k
    - dmax -- maximal secondary delay
    """
    j = jsd_dicts[k]["j"]
    s = jsd_dicts[k]["s"]
    w = penalty_weights(trains_timing, j, s) / d_max
    return jsd_dicts[k]["d"] * w


def get_coupling(k, k1, jsd_dicts, p_sum, p_pair, trains_paths, trains_timing):
    """ returns weighted hard constrains contributions to Qmat at k,k1 in the
    case where no auxiliary variables: headway, minimal stay, single_line, circulation, switch


    Input:
    - trains_timing - dict
    - trains_paths -- dict
    - k, k1 -- indices
    - jsd_dicts -- vector {"j": j, "s": s, "d": d}
      of trains, stations, delays tied to index k of k1
    - p_sum -- weight for sum to one constrain
    - p_pair -- weight for quadratic constrains (it is then doubled due to quadratisation)
    """
    # each train leave each station onse and only once
    J = p_sum * P_sum(k, k1, jsd_dicts)
    # quadratic conditions
    J += p_pair * P_headway(k, k1, jsd_dicts, trains_timing, trains_paths)
    J += p_pair * P_minimal_stay(k, k1, jsd_dicts, trains_timing, trains_paths)
    J += p_pair * P_single_track_line(k, k1, jsd_dicts, trains_timing, trains_paths)
    J += p_pair * P_rolling_stock_circulation(k, k1, jsd_dicts, trains_timing, trains_paths)
    J += p_pair * P_switch_occupation(k, k1, jsd_dicts, trains_timing, trains_paths)
    return J


def get_z_coupling(k, k1, jsd_dicts, p_pair, p_qubic, trains_timing, trains_paths):
    """ returns weighted hard constrains contributions to Qmat at k,k1 in the
    case where auxiliary variables are included, i.e. in the single track
    occupancy at station case.

    Input:
    trains_timing -- time trains_timing
    k, k1 -- indexes on the Q matrix
    trains_paths -- train set dict containing trains paths
    jsd_dicts -- vector of {"j": j, "s": s, "d": d}  form indexing4qubo
    p_pair -- weight for quadratic constrains
    p_qubic -- weight for Rosenberg decomposition
    """
    J = p_pair * P_track_occupation_condition_quadratic_part(k, k1, jsd_dicts, trains_timing, trains_paths)
    J += p_qubic * P_Rosenberg_decomposition(k, k1, jsd_dicts, trains_paths)
    return J


def make_Q(d_max, p_sum, p_pair, p_qubic, trains_timing, trains_paths):
    """returns symmetric Q matrix for the particular problem encoded in
    trains_paths and trains_timing

    Parameters
    dmax -- maximal secondary delay
    p_sum -- panalty for ∑_i x_i = 1 hard constrains
    p_pair -- penalty for ∑_i,j x_i x_j = 0 hard constrains
    p_qubic -- weight for Rosenberg decomposition of qubic term
    """
    inds, q_bits = indexing4qubo(trains_paths, d_max) # indices of vars
    inds_z, q_bits_z = z_indices(trains_paths, d_max) # indices of auxiliary vars.

    inds1 = np.concatenate([inds, inds_z])

    l = q_bits
    l1 = q_bits + q_bits_z

    Q = [[0.0 for _ in range(l1)] for _ in range(l1)]

    # add soft panalties (objective)
    for k in range(l):
        Q[k][k] += penalty(k, inds, d_max, trains_timing)
    # quadratic headway, minimal stay, single_line, circulation, switch
    for k in range(l):
        for k1 in range(l):
            Q[k][k1] += get_coupling(k, k1, inds, p_sum, p_pair, trains_paths, trains_timing)
    # qubic track occupancy condition.
    for k in range(l1):
        for k1 in range(l1):
            Q[k][k1] += get_z_coupling(
                k, k1, inds1, p_pair, p_qubic, trains_timing, trains_paths
            )
    return Q
