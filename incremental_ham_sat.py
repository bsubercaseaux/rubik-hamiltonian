from pysat.pb import *
from pysat.formula import CNF, IDPool
from pysat.solvers import Cadical195
import itertools
from checker import check_hamiltonian_path


def at_most_one(variables, vpool):
    if len(variables) <= 4:
        return [[-comb[0], -comb[1]] for comb in itertools.combinations(variables, 2)]
    else:
        new_var = vpool.id()
        return at_most_one(variables[:3] + [-new_var], vpool) + at_most_one([new_var] + variables[3:], vpool)
    

def base_hamilton_path(G, s, t):
    """
    Base encoding for Hamiltonian path in a graph G from node s to node t.
    
    :param G: The graph represented as an adjacency list.
    :param s: The starting node of the path.
    :param t: The ending node of the path.
    :return: A CNF formula representing the Hamiltonian path constraints.
    """
    cnf = CNF()
    n = len(G)
    
    # Create edge variables mapping
    edges = []
    edge_vars = {}
    vpool = IDPool()
    for u in range(n):
        for v in G[u]:
            edges.append((u, v))

    ev = lambda e: vpool.id(f"e_{e[0], e[1]}")

    # exact number of edges
    for u in range(n):
        if u != s and u != t:
            cnf.append([ev((u, v)) for v in G[u]]) # >= 1 outgoing edge
            cnf.append([ev((v, u)) for v in G[u]]) # >= 1 incoming edge
            cnf.extend(at_most_one([ev((u, v)) for v in G[u]], vpool)) # <= 1 outgoing edge
            cnf.extend(at_most_one([ev((v, u)) for v in G[u]], vpool)) # <= 1 incoming edge
        if u == s:
            cnf.append([ev((s, v)) for v in G[s]])
            cnf.extend(at_most_one([ev((s, v)) for v in G[s]], vpool)) # <= 1 outgoing edge
            cnf.extend([[-ev((v, s))] for v in G[s]])  # no incoming edges to s
        if u == t:
            cnf.append([ev((v, t)) for v in G[t]])
            cnf.extend(at_most_one([ev((v, t)) for v in G[t]], vpool)) # <= 1 incoming edge
            cnf.extend([[-ev((t, v))] for v in G[t]])  # no outgoing edges from t

    # no backtracks
    for u in range(n):
        for v in G[u]:
            cnf.append([-ev((u, v)), -ev((v, u))])  # if u -> v then not v -> u

    return cnf, vpool

def incremental_hamilton_path(G, s, t, verbose=False):
    base_cnf, vpool = base_hamilton_path(G, s, t)

    solver = Cadical195(base_cnf)
    

    while True:
        if verbose:
            print(solver.nof_clauses(), "clauses in the solver")
        solver.solve()
        model = solver.get_model()
        if model is None:
            print("No Hamiltonian path found.")
            return None 
        
        else:
            edges = []
            for u in range(len(G)):
                for v in G[u]:
                    # print(f"Checking edge {u} -- {v}: id = {vpool.id(f'e_{u, v}')}")
                    if model[vpool.id(f"e_{u, v}") - 1] > 0:
                        # print(f"Edge {u} -- {v} is part of the Hamiltonian path.")
                        edges.append((u, v))
            # identify cycles now
            path = [s]
            current = s
            visited = {s}
            while True:
                found = False
                for v in G[current]:
                    if (current, v) in edges or (v, current) in edges:
                        if v not in visited:
                            path.append(v)
                            visited.add(v)
                            current = v
                            found = True
                            break
                if not found:
                    if verbose:
                        print("No further path found, terminating early.")
                        print(f"Vertex {current} has no unvisited neighbors.")
                    break
            if len(path) == len(G):
                if verbose:
                    print(f"Hamiltonian path found: {' -> '.join(map(str, path))}")
                    print(f"Checking Hamiltonian path validity...")
                if check_hamiltonian_path(G, path, s, t):
                    if verbose:
                        print("Hamiltonian path is valid.")
                    return path
                else:
                    print("Hamiltonian path is invalid.")
                    break
                

            else:
                if verbose:
                    print(f"Path found is not Hamiltonian, only visited {len(path)} nodes out of {len(G)}.")
                    print(f"Visited nodes: {path}")
                
               
                for node in G:
                    if node not in visited:
                        # print(f"Node {node} was not visited.")
                        cycle = [node]
                        current = node
                        while True:
                            found = False
                            for v in G[current]:
                                if (current, v) in edges:
                                    if v not in cycle:
                                        cycle.append(v)
                                        current = v
                                        found = True
                                        visited.add(v)
                                        break
                            if not found:
                                if verbose:
                                    print(f"Cycle found: {' -> '.join(map(str, cycle))}")
                                solver.add_clause([-vpool.id(f"e_{cycle[i], cycle[i+1]}") for i in range(len(cycle)-1)] + [-vpool.id(f"e_{cycle[-1], cycle[0]}")])
                                break