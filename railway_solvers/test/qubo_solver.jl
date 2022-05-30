using LightGraphs
using LinearAlgebra
using NPZ

using SpinGlassMetropolisHastings
using SpinGlassPEPS


"""
    read_trains_qubos(file::String)
reads train instances form the csv file
returns instance in the form of Matrix{Float64}
"""
function read_trains_qubos(file::String)
    csv_reader = CSV.File(file)
    s = 0
    for row in csv_reader
        s = maximum([s, row[:x]+1])
    end

    M = zeros(s,s)
    for row in csv_reader
        x = row[:x]+1
        y = row[:y]+1
        M[x,y] = M[y,x] = row[:J]
    end
    M
end


"""
    Mat_qubo2ising(Q::Matrix{T}) where T <: AbstractFloat
convert the matrix of interactions from qubo representation to the Ising one.
"""
function Mat_qubo2ising(Q::Matrix{T}) where T <: AbstractFloat
    J = (Q - diagm(diag(Q)))/4
    v = dropdims(sum(J; dims=1); dims = 1)

    h = diagm(diag(Q)/2 + v*2)
    - J - h
end


"""
    ising2bin(i::Int)
changes an ising variable to a binary variable
"""
ising2bin(i::Int) = (i == -1) ? 0 : 1

"""
    M2graph(M::Matrix{Float64}, sgn::Int = 1)
Convert the symmetric matrix if interactions into the Ising graph
```jldoctest
julia> M = ones(2,2);
julia> g = M2graph(M)
{2, 1} undirected Int64 metagraph with Float64 weights defined by :weight (default weight 1.0)
```
"""
function M2graph(M::Matrix{Float64}; k::Int = 2, sgn::Int = 1)
    @assert size(M,1) == size(M,2) "Instance matrix must be squared"
    D = Dict{Tuple{Int64,Int64},Float64}()
    for j ∈ 1:size(M, 1)
        for i ∈ 1:j
            if i == j
                push!(D, (i,j) => M[j,i])
            elseif M[j,i] != 0.
                @assert M[j,i] ≈ M[i,j] "Instance matrix must by symmetric"
                # factor of k is due to the convention
                push!(D, (i,j) => k*M[i,j])
            end
        end
    end
    ising_graph(D, sgn=sgn)
end



p = MH_parameters(2.0)

#Qs = ["files/Qfile_one_way.npz", "files/Qfile_two_ways.npz", "files/Qfile_track.npz"]
#solutions = ["files/solution_one_way.npz", "files/solution_two_ways.npz", "files/solution_track.npz"]
Qs = ["files/Qfile_circ.npz"]
solutions = ["files/solution_circ.npz"]


for i in 1:length(Qs)
    x = npzread(Qs[i]);



    Q = x["Q"]

    println("Q mat size", size(Q))

    JJ = Mat_qubo2ising(Q);
    ig = M2graph(JJ; sgn = -1)

    t = 1000
    #t = 5000

    @time sol = mh_solve(ig, p, t, sort = true);

    println("minimal energy", sol.energies[1])
    npzwrite(solutions[i] , sol.states[1])

end
