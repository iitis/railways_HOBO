import matplotlib.pyplot as plt
import pickle
from matplotlib import rc

rc('text',usetex=True)
rc('font', family='serif')

fig, axes = plt.subplots(ncols=2)
fig, ax = plt.subplots(1, 2, figsize=(10,5))


# annealing time = 250 μs
# number of runs = 3996

# default setting

for i, route in enumerate([ 'Default', 'Rerouting' ]):
    non_feasible_css = [3, 3.5, 4, 4.5]
    non_feasible_def = { 'en':[], 'cs':[] }
    for cs in non_feasible_css:
        if route == 'Default':
            with open(f"files/dwave_data/Qfile_samples_sol_real-anneal_numread3996_antime250_chainst{cs}", 'rb') as fp:
                x = pickle.load(fp)
        elif route == 'Rerouting':
            with open(f"files/dwave_data/Qfile_samples_sol_real-anneal_numread3996_antime250_chainst{cs}_r", 'rb') as fp:
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

    non_feasible_css_mod = non_feasible_def['cs']
    non_feasible_ens_mod = non_feasible_def['en']

    title = "annealing t = 250 μs, 3996 runs, default"

    if i ==0:
        ax[i].plot(non_feasible_css_mod, non_feasible_ens_mod, 'rs', label = 'D-Wave non-feasible solution')
        ax[i].plot(feasible_css, feasible_ens, 'go', label = 'D-Wave feasible solution')
        ax[i].set_xticks(non_feasible_css)
        ax[i].set_title('Default settings', fontsize = 14)
        ax[i].axhline(y =ground, color = 'g', label = 'Ground state and hybrid solver')
    else:
        ax[i].plot(non_feasible_css_mod, non_feasible_ens_mod, 'rs')
        ax[i].plot(feasible_css, feasible_ens, 'go')
        ax[i].set_xticks(non_feasible_css)
        ax[i].set_title('Rerouting', fontsize = 14)
        ax[i].axhline(y =ground, color = 'g')


fig.text(0.5, 0.013, 'Chain strength', ha='center', fontsize = 15)
fig.text(0.05, 0.42, 'Minimum energy', va='center', rotation='vertical', fontsize = 15)
fig.legend(title = 'Annealing time = $250$ $\mu$$s$, $3996$ reads', loc='upper center',  borderaxespad=2.9, ncol=2, title_fontsize = 12, fontsize = 12)
fig.subplots_adjust(top=0.68)

fig.savefig("DW_trains.pdf")
