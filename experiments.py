import networkx as nx
from networkx.algorithms import bipartite
import numpy as np
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver
from pysat.card import CardEnc
import time
from incremental_ham_sat import incremental_hamilton_path
from build_graphs import build_no_grip_graph
from build_floppy import generate_floppy_graph


def hamiltonian_experiments(G):
    data = {}
    n = G.number_of_nodes()

    def bench(end_node, alg):
        start_time = time.time()
        path = alg(G, 0, end_node)
        end_time = time.time()
        elapsed = end_time - start_time
        return path, elapsed

    is_bipartite = bipartite.is_bipartite(G)
    print(f"Graph is bipartite: {is_bipartite}")
    bipartition = bipartite.color(G) if is_bipartite else None

    # algs = [solve_hamiltonian_ortools,  incremental_hamilton_path]
    algs = [incremental_hamilton_path]
    for end_node in range(1, n):
        if is_bipartite and bipartition[0] == bipartition[end_node]:
            continue
        data[end_node] = {}
        for alg in algs:
            _, t = bench(end_node, alg)
            data[end_node][alg.__name__] = t
            print(f"End Node {end_node}, Alg {alg.__name__}, Time: {t:.4f} seconds")

    return data
        

if __name__ == "__main__":
    adj, state_to_id = generate_floppy_graph()
    G_floppy = nx.Graph()
    for u, neighbors in enumerate(adj):
        for v in neighbors:
            G_floppy.add_edge(u, v)

    graphs = []
    graphs.append(( "floppy", G_floppy))

    data = {}

    for N in [3, 4, 5]:
        G, oriented, nogrip = build_no_grip_graph(N=N, store_rep_state=False)
        print(f"Generated 1x2x{N} graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
        graphs.append((f"1x2x{N}", G))

    for name, G in graphs:
        print(f"\n--- Hamiltonian Path Experiments for {name} Graph ---")
        data[name] = {}
        data[name]['bipartite'] = bipartite.is_bipartite(G)
        data[name]['num_nodes'] = G.number_of_nodes()
        data[name]['num_edges'] = G.number_of_edges()
        ham_data = hamiltonian_experiments(G)
        times = []
        for key in ham_data:
            times.append(ham_data[key]['incremental_hamilton_path'])
        # times = [ham_data[key]['time'] for key in ham_data]
        data[name]['avg_t'] = sum(times) / len(times)
        data[name]['max_t'] = max(times)
        data[name]['min_t'] = min(times)
        std_v = (np.std(times))
        data[name]['std_t'] = std_v
       
        print(f"Avg Time: {data[name]['avg_t']:.4f}, Max Time: {data[name]['max_t']:.4f}, Min Time: {data[name]['min_t']:.4f}, Std Dev: {data[name]['std_t']:.4f}")