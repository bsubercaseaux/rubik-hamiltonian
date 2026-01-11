def check_hamiltonian_path(G, path, s, t):
    """
    Check if the given path is a Hamiltonian path in the graph G from node s to node t.
    
    :param G: The graph represented as an adjacency list.
    :param path: The list of nodes representing the path.
    :param s: The starting node of the path.
    :param t: The ending node of the path.
    :return: True if the path is a Hamiltonian path, False otherwise.
    """
    n = len(G)
    
    # Check if the path starts with s and ends with t
    if path[0] != s or path[-1] != t:
        print(f"Path does not start with {s} or end with {t}.")
        return False
    
    # Check if the path visits all nodes exactly once
    visited = set()
    for node in path:
        if node in visited or node < 0 or node >= n:
            print(f"Node {node} is either visited multiple times or out of bounds.")
            return False
        visited.add(node)
    
    if len(visited) != n:
        print(f"Path does not visit all nodes exactly once, expected {n} unique nodes, found {len(visited)}.")
        return False
    
    # Check if each consecutive pair of nodes in the path are connected by an edge
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        if v not in G[u]:
            print(f"Nodes {u} and {v} are not connected by an edge.")
            return False
    
    return True