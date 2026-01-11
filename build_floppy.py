from collections import deque

### NOTE: Large parts of this file were created by ChatGPT 5.2. ###
### I have reviewed and edited as needed. ###
### I have also checked using the Algebra system GAP that the generated graphs match their group descriptions. ###

# ----------------------------
# 3x3x1 (aka 1x3x3) "floppy cube" model via facelets
# State = permutation of facelets from the solved position.
# Moves = 180-degree turns of outer layers: U2, D2, R2, L2.
# ----------------------------

def build_facelets(nx, ny, nz):
    """
    Facelet is identified by (cubie_position, outward_normal).
    cubie_position = (x,y,z) with x in [0..nx-1], etc.
    outward_normal in {±x, ±y, ±z}.
    """
    facelets = []
    for x in range(nx):
        for y in range(ny):
            for z in range(nz):
                if x == 0:      facelets.append(((x, y, z), (-1, 0, 0)))
                if x == nx - 1: facelets.append(((x, y, z), ( 1, 0, 0)))
                if y == 0:      facelets.append(((x, y, z), (0, -1, 0)))
                if y == ny - 1: facelets.append(((x, y, z), (0,  1, 0)))
                if z == 0:      facelets.append(((x, y, z), (0, 0, -1)))
                if z == nz - 1: facelets.append(((x, y, z), (0, 0,  1)))
    return facelets


def rotate_point_180(p, axis, dims):
    """Rotate a cubie position by 180 degrees around axis through the cuboid center."""
    x, y, z = p
    nx, ny, nz = dims
    if axis == 'x':
        return (x, (ny - 1) - y, (nz - 1) - z)
    if axis == 'y':
        return ((nx - 1) - x, y, (nz - 1) - z)
    if axis == 'z':
        return ((nx - 1) - x, (ny - 1) - y, z)
    raise ValueError("bad axis")


def rotate_normal_180(v, axis):
    """Rotate an outward normal vector by 180 degrees around axis."""
    vx, vy, vz = v
    if axis == 'x':
        return (vx, -vy, -vz)
    if axis == 'y':
        return (-vx, vy, -vz)
    if axis == 'z':
        return (-vx, -vy, vz)
    raise ValueError("bad axis")


def move_perm(nx, ny, nz, move):
    """
    Return a permutation 'perm' on facelet indices such that:
      new_state[j] = old_state[perm[j]]
    """
    dims = (nx, ny, nz)
    facelets = build_facelets(nx, ny, nz)
    idx = {f: i for i, f in enumerate(facelets)}
    perm = list(range(len(facelets)))

    if move == 'U2':
        axis, layer = 'y', ny - 1
        in_layer = lambda p: p[1] == layer
    elif move == 'D2':
        axis, layer = 'y', 0
        in_layer = lambda p: p[1] == layer
    elif move == 'R2':
        axis, layer = 'x', nx - 1
        in_layer = lambda p: p[0] == layer
    elif move == 'L2':
        axis, layer = 'x', 0
        in_layer = lambda p: p[0] == layer
    else:
        raise ValueError("move must be one of U2, D2, R2, L2")

    for i, (pos, normal) in enumerate(facelets):
        if in_layer(pos):
            pos2 = rotate_point_180(pos, axis, dims)
            normal2 = rotate_normal_180(normal, axis)
            j = idx[(pos2, normal2)]
            perm[j] = i

    return perm


def apply_perm(state, perm):
    return tuple(state[perm[j]] for j in range(len(perm)))


def generate_floppy_graph():
    # 1x3x3 floppy cube is 3x3x1 as a cuboid discretization
    nx, ny, nz = 3, 3, 1
    gens = ['U2', 'D2', 'R2', 'L2']
    perms = [move_perm(nx, ny, nz, g) for g in gens]

    facelets = build_facelets(nx, ny, nz)
    m = len(facelets)
    start = tuple(range(m))  # solved labeling

    # BFS enumerate all reachable states
    q = deque([start])
    state_to_id = {start: 0}
    id_to_state = [start]

    while q:
        s = q.popleft()
        for p in perms:
            t = apply_perm(s, p)
            if t not in state_to_id:
                state_to_id[t] = len(id_to_state)
                id_to_state.append(t)
                q.append(t)

    n_states = len(id_to_state)

    # Build adjacency list (4-regular)
    adj = [[] for _ in range(n_states)]
    for sid, s in enumerate(id_to_state):
        for p in perms:
            t = apply_perm(s, p)
            adj[sid].append(state_to_id[t])

    # sanity checks
    assert n_states == 192, f"Expected 192 states, got {n_states}"
    assert all(len(set(nei)) == 4 for nei in adj), "Graph is not 4-regular (unexpected duplicate neighbors)."

    return adj, state_to_id
