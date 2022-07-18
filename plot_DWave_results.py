""" plotter of results of computaiton on the DWave"""
import pickle
import matplotlib.pyplot as plt
from matplotlib import rc
from Qfile_solve import method_marker

rc('text',usetex=True)
rc('font', family='serif')

fig, axes = plt.subplots(ncols=2)
fig, ax = plt.subplots(1, 2, figsize=(5,3),sharey=True)


# annealing time = 250 μs
# number of runs = 3996

# default setting

for i, route in enumerate([ "enlarged", "5trains" ]):
    non_feasible_css = [3, 3.5, 4, 4.5]
    non_feasible_def = { 'en':[], 'cs':[] }
    print(route)
    f = method_marker(route)
    print(f)
    for cs in non_feasible_css:
        if route == 'Default':
            with open(f"files/dwave_data/Qfile_samples_sol_real-anneal_numread3996_antime250_chainst{cs}", 'rb') as fp:
                x = pickle.load(fp)
        elif route == 'Rerouting':
            with open(f"files/dwave_data/Qfile_samples_sol_real-anneal_numread3996_antime250_chainst{cs}_r", 'rb') as fp:
                x = pickle.load(fp)
        if route == 'enlarged':
            print(f)
            with open(f"files/dwave_data/Qfile_complete_sol_real-anneal_numread3996_antime250_chainst{cs}" +f, 'rb') as fp:
                x = pickle.load(fp)
        elif route == '5trains':
            with open(f"files/dwave_data/Qfile_complete_sol_real-anneal_numread3996_antime250_chainst{cs}" +f, 'rb') as fp:
                x = pickle.load(fp)

        non_feasible_def['en'].append(x[0][1])
        non_feasible_def['cs'].append(cs)

    feasible_ens = min(non_feasible_def['en'])
    feasible_index = non_feasible_def['en'].index(feasible_ens)
    feasible_css = non_feasible_def['cs'][feasible_index]
    non_feasible_def['en'].remove( feasible_ens )
    non_feasible_def['cs'].remove( feasible_css )

    if route == 'Default':
        with open('files/hybrid_data/Qfile_samples_sol_hybrid-anneal', 'rb') as fp:
            ground = [pickle.load(fp)[0][1]]
    elif route == 'Rerouting':
        with open('files/hybrid_data/Qfile_samples_sol_hybrid-anneal_r', 'rb') as fp:
            ground = [pickle.load(fp)[0][1]]
    elif route == 'enlarged':
        with open('files/hybrid_data/Qfile_samples_sol_hybrid-anneal' +f, 'rb') as fp:
            ground = [pickle.load(fp)[0][1]]
    elif route == '5trains':
        with open('files/hybrid_data/Qfile_samples_sol_hybrid-anneal' +f, 'rb') as fp:
            ground = [pickle.load(fp)[0][1]]

    non_feasible_css_mod = non_feasible_def['cs']
    non_feasible_ens_mod = non_feasible_def['en']

    title = "annealing t = 250 μs, 3996 runs, default"

    if i ==0:
        ax[i].plot(non_feasible_css_mod, non_feasible_ens_mod, 'rs', label = 'D-Wave non-feasible solution')
        ax[i].plot(feasible_css, feasible_ens, 'ko', label = 'D-Wave solution')
        ax[i].set_xticks(non_feasible_css)
        ax[i].set_title('6 trains, 2 stations')
        ax[i].axhline(y =ground, color = 'g', label = 'Ground state and hybrid solver')
    else:
        ax[i].plot(non_feasible_css_mod, non_feasible_ens_mod, 'rs')
        ax[i].plot(feasible_css, feasible_ens, 'ko')
        ax[i].set_xticks(non_feasible_css)
        ax[i].set_title('5 trains, 5 stations')
        ax[i].axhline(y =ground, color = 'g')
    ax[i].set_xlabel('Chain strength')

# fig.text(0.5, 0.01, 'Chain strength', ha='center')
fig.text(0.005, 0.42, 'Minimum energy', va='center', rotation='vertical')
fig.legend(title = 'Annealing time = $250$ $\mu$$s$, $3996$ reads', loc='upper center',  borderaxespad=0.5, ncol=2, title_fontsize = 9, fontsize = 9)

fig.tight_layout()
fig.subplots_adjust(top=0.68)
fig.savefig("plots/DW_trains.pdf")
