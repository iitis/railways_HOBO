""" reads files ... TODO AK pleas specify"""
import pickle

# with open('Qfile_samples_sol_real-anneal_numread1998_antime500_chainst4.5_r', 'rb') as fp:
# x = pickle.load(fp)
# print(x)

print('Non-Reroute:')
for j in [3, 3.5, 4, 4.5]:
    with open(f"files/dwave_data/Qfile_samples_sol_real-anneal_numread3996_antime250_chainst{j}", 'rb') as fp:
        x = pickle.load(fp)
        print(x[0][1], 'chain strenght', j)

print('------------')

print('Reroute:')
for j in [3, 3.5, 4, 4.5]:
    with open(f"files/dwave_data/Qfile_samples_sol_real-anneal_numread3996_antime250_chainst{j}_r", 'rb') as fp:
        x = pickle.load(fp)
        print(x[0][1], 'chain strenght', j)

print()
print('---------')
print('Hybrid - non-Reroute:')
with open('files/hybrid_data/Qfile_samples_sol_hybrid-anneal', 'rb') as fp:
    x = pickle.load(fp)

print(x[0][1])

print('Hybrid - non-Reroute:')
with open('files/hybrid_data/Qfile_samples_sol_hybrid-anneal_r', 'rb') as fp:
    x = pickle.load(fp)
print(x[0][1])
