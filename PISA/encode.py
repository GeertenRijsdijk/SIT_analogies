from .graphs import Graph, Sgraph, LeftAgraph, RightAgraph, \
    concatenate_hyperstrings
from .QUIS import QUIS, create_labels

def get_PISA_codes(string, return_loads = False):
    g = Graph(string)
    encode(g)
    all_paths = g.find_all_paths(0, len(string))
    all_edges = []
    for path in all_paths:
        code, load = '', 0
        for i in range(len(path)-1):
            edge_code, edge_load = g.edges[path[i]][path[i+1]]
            code += edge_code
            load += edge_load
        all_edges.append((code, load))

    if return_loads:
        all_edges = list(set(all_edges))
    else:
        all_edges = list(set([e[0] for e in all_edges]))
    return all_edges

# Creates a dictionary of S-Graphs for a given hyperstring
def create_sgraphs(h, Q):
    Sgraphs = {}
    n_from = h.nodes[0]
    n_to = h.next(n_from)

    # For one of the two first or last ...
    while n_to != None and h.next(n_to) != None and h.next(n_to, 2) != None:
        # ... create Sgraphs for the possible pivots
        if n_from != h.nodes[0]:
            Sgraphs[n_to] = Sgraph()
            Sgraphs[n_to].construct_from_hyperstring(h, n_to, Q)
        Sgraphs[n_to+0.5] = Sgraph()
        Sgraphs[n_to+0.5].construct_from_hyperstring(h, n_to+0.5, Q)

        n_from = n_to
        n_to = h.next(n_from)

    # Remove empyt Sgraphs.
    for k, sg in Sgraphs.items():
        if sg.edges == {}:
            Sgraphs[k] = None

    return Sgraphs

# Creates two dictionaries of A-graphs for a given hyperstring
def create_agraphs(h, Q):
    l_agraphs = {}
    r_agraphs = {}
    # Calculate maximum possible repeat length
    N = int(h.len()/2)
    # For each repeat length ...
    for i in range(1, N):
        # ... create a left Agraph ...
        l_agraphs[i] = LeftAgraph()
        l_agraphs[i].construct_from_hyperstring(h, i, Q)
        # ... and a right Agraph.
        r_agraphs[i] = RightAgraph()
        r_agraphs[i].construct_from_hyperstring(h, i, Q)
    return l_agraphs, r_agraphs

'''
Given a Graph object, for every two connected nodes in the graph, this
function finds the minimal encoding of the labels between those nodes.

Based on the PISA algorithm:
https://perswww.kuleuven.be/~u0084530/doc/pisa.html

Input:
    - A Graph object
Returns:
    - The same graph object, altered
'''
def encode(g):
    hyperstrings = g.split_hyperstrings()
    # Process individual hyperstrings
    new_hyperstrings = []

    # For each hyperstring:
    for h in hyperstrings:

        # Create an identity matrix
        labels = create_labels(h)
        Q = QUIS(h, labels)

        # For each node w in the hyperstring (except the first) ...
        for i_w, w in enumerate(h.nodes[1:], start = 1):
            # ... create S-graphs ...
            Sgraphs = create_sgraphs(h, Q)
            for k, sg in Sgraphs.items():
                encode(sg)

            # ... and create A-graphs.
            subgraph = h.subgraph(h.nodes[0], w)
            l_agraphs, r_agraphs = create_agraphs(subgraph, Q)
            for k, ag in l_agraphs.items():
                encode(ag)
            for k, ag in r_agraphs.items():
                encode(ag)

            # For each node v before node w:
            for i_v in range(i_w-1, -1, -1):
                v = h.nodes[i_v]
                pivot = h.nodes[int((i_w + i_v)/2)]
                if (i_w - i_v) % 2 == 1:
                    pivot += 0.5

                # Get the current code and load.
                init_code, init_load = h.get_edge(v, w)
                best_code, best_load = init_code, init_load
                # Try to find a better code using iteration ...
                code, load = h.find_best_iteration(v, w)
                if code and load < best_load:
                    best_code, best_load = code, load
                # ... symmetry ...
                if pivot in Sgraphs and Sgraphs[pivot]:
                    code, load = Sgraphs[pivot].get_symmetry(v, w)
                    if code and load < best_load:
                        best_code, best_load = code, load
                # ... left-alternation ...
                for ag in l_agraphs.values():
                    code, load = ag.get_alternation(v, w)
                    if code and load < best_load:
                        best_code, best_load = code, load
                # ... or right-alternation ...
                for ag in r_agraphs.values():
                    code, load = ag.get_alternation(v, w)
                    if code and load < best_load:
                        best_code, best_load = code, load
                # ... and add the best code as an edge to the graph.
                h.add_edge(v, w, best_code, best_load)

                # For each node u before v:
                for i_u in range(i_v):
                    u = h.nodes[i_u]
                    c_uv, d_uv = h.get_edge(u, v)
                    c_uw, d_uw = h.get_edge(u, w)
                    # If distance u_w > u->v + v->w ...
                    if d_uw > d_uv + best_load:
                        # ... Create a code from u->v + v->w and add an edge.
                        h.add_edge(u, w, c_uv + best_code, d_uv + best_load)

        new_hyperstrings.append(h)

    # Combine all hyperstrings into
    g.clear()
    concatenate_hyperstrings(new_hyperstrings, graph = g)
