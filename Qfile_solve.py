""" calls DWave solver TODO AK please specify """
import pickle
import neal
import numpy as np
from dwave.system import EmbeddingComposite, DWaveSampler, LeapHybridSampler
import dimod
import sys
import dwave.inspector

#import dwave.inspector
# from edge_helpers import *
# from generate_ham_edge import *
# from generate_ham_ilp import *
# from ilp_helpers import *

def anneal_solutuon(method = None):
    if method == '5trains':
        Q_init = np.load('files/Qfile_5_trains.npz')
    elif method == 'rerouted':
        Q_init = np.load('files/Qfile_r.npz')
    elif method == 'enlarged':
        Q_init = np.load('files/Qfile_enlarged.npz')
    else:
        Q_init = np.load('files/Qfile.npz')

    Q = Q_init['Q'].astype(np.float32)
    model = dimod.BinaryQuadraticModel(Q, "BINARY")

    # model = dimod.BinaryQuadraticModel.from_numpy_matrix(Q)
    qubo, offset = model.to_qubo()
    return qubo


def method_name(method):
    """ mark methods for output file"""
    if method == None:
        return "Default"
    if method == "enlarged": 
        return "4 trains, 2 stations"
    if method == "rerouted":
        return "Rerouted"
    if method == "5trains": 
        return "_5 tarins, 5 stations"


def method_marker(method):
    """ mark methods for output file"""
    if method == None:
        return ""
    if method == "enlarged": 
        return "_e"
    if method == "rerouted":
        return "_r"
    if method == "5trains": 
        return "_5t"


############################
def sim_anneal(method):
    s = neal.SimulatedAnnealingSampler()
    sampleset = s.sample_qubo(anneal_solutuon(method), beta_range=(5,100), num_sweeps=4000, num_reads=1000,
                               beta_schedule_type='geometric')
    return sampleset


def real_anneal(method, num_reads, annealing_time, chain_strength):
    sampler = EmbeddingComposite(DWaveSampler())
    sampleset = sampler.sample_qubo(anneal_solutuon(method), num_reads=num_reads, auto_scale='true', annealing_time=annealing_time, chain_strength=chain_strength) #annealing time in micro second, 20 is default.
    return sampleset

def hybrid_anneal(method):
    sampler = LeapHybridSampler()
    sampleset = sampler.sample_qubo(anneal_solutuon(method))
    return sampleset


def annealing_results(annealing, num_reads, annealing_time, method):

    if method == 'default':
        method = None

    print('------------STARTING--------------')
    print()
    print(f'{method_name(method)} settings model, solving with {annealing} annealing')

    if annealing == 'simulated':
        
        sampleset = sim_anneal(method)         
        results=[]
        for datum in sampleset.data():
            x = dimod.sampleset.as_samples(datum.sample)[0][0]
            results.append((x, datum.energy))

        sdf = sampleset.to_serializable()
        f = method_marker(method)
        with open("files/Qfile_complete_sol_sim-anneal"+f, 'wb') as handle:
            pickle.dump(sdf, handle)
        with open("files/Qfile_samples_sol_sim-anneal"+f, 'wb') as handle:
            pickle.dump(results, handle)

    elif annealing == 'hybrid':

        sampleset = hybrid_anneal(method)
        results = []
        for datum in sampleset.data():
            x = dimod.sampleset.as_samples(datum.sample)[0][0]
            results.append((x, datum.energy))

        sdf = sampleset.to_serializable()

        f = method_marker(method)

        with open("files/hybrid_data/Qfile_complete_sol_hybrid-anneal"+f, 'wb') as handle:
            pickle.dump(sdf, handle)
        with open("files/hybrid_data/Qfile_samples_sol_hybrid-anneal"+f, 'wb') as handle:
            pickle.dump(results, handle)


    elif annealing == 'quantum':
        for chain_strength in [3,3.5,4,4.5]:

            sampleset = real_anneal(method, num_reads, annealing_time, chain_strength)

            results=[]
            for datum in sampleset.data():
                x = dimod.sampleset.as_samples(datum.sample)[0][0]
                results.append((x, datum.energy))

            sdf = sampleset.to_serializable()
            f = method_marker(method)
            
            fname_comp = "files/dwave_data/Qfile_complete_sol_real-anneal_numread{}_antime{}_chainst{}" + f
            fname_samp = "files/dwave_data/Qfile_samples_sol_real-anneal_numread{}_antime{}_chainst{}" + f
            with open(fname_comp.format(num_reads, annealing_time,chain_strength), 'wb') as handle:
                pickle.dump(sdf, handle)
            with open(fname_samp.format(num_reads, annealing_time,chain_strength), 'wb') as handle:
                pickle.dump(results, handle)


            print('Energy {} with chain strength {} run'.format(sampleset.first, chain_strength))
    
    print()
    print('------------END--------------')


# print(len(sys.argv))

if len(sys.argv) < 2:
    print("You should put some inputs here. If you don't know, type '-h','--help' for instructions.")
    exit(0)

if sys.argv[1] in ["--help", "-h"]:
    print()
    print("Please specify:")
    print()
    print("     - annealer --> 'simulated', 'hybrid', 'quantum' ")
    print()
    print("     - number of reads (eg. 3996), annelaing_time (eg.250) for running quantum annealing")
    print()
    print("     - the method: 'default' (for default setting), 'rerouted' (under rerouting), 'enlarged' (4 trains, 2 stations), '5trains' (5 trains, 5 stations)     ")
    print()
    print("EXAMPLE!! python Qfile_solve.py 'simulated' 0 0 'enlarged'")
    print()
    print("NOTE: For 'simulated' and 'hybrid' annealer, the 'annealing_time' and 'number of reads' can be set arbitrarily")
    exit(0)

annealing = str(sys.argv[1]) #'quantum'
num_reads = int(sys.argv[2]) #3996
annealing_time = int(sys.argv[3]) #250
method = str(sys.argv[4]) #'enlarged'

annealing_results(annealing, num_reads, annealing_time, method)