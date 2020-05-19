from .graphs import Graph, Sgraph, LeftAgraph, RightAgraph, \
    concatenate_hyperstrings
from .QUIS import QUIS, create_labels

# Create S-Graphs
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

def create_agraphs(h, Q):
    l_agraphs = {}
    r_agraphs = {}
    # Calculate maximum possible repeat length
    N = int(h.len()/2)
    for i in range(1, N):
        l_agraphs[i] = LeftAgraph()
        l_agraphs[i].construct_from_hyperstring(h, i, Q)
        r_agraphs[i] = RightAgraph()
        r_agraphs[i].construct_from_hyperstring(h, i, Q)
    return l_agraphs, r_agraphs

def encode(g):
    hyperstrings = g.split_hyperstrings()
    # Process individual hyperstrings
    new_hyperstrings = []

    for h in hyperstrings:

        labels = create_labels(h)
        Q = QUIS(h, labels)

        for i_w, w in enumerate(h.nodes[1:], start = 1):
            Sgraphs = create_sgraphs(h, Q)
            for k, sg in Sgraphs.items():
                encode(sg)

            subgraph = h.subgraph(h.nodes[0], w)
            l_agraphs, r_agraphs = create_agraphs(subgraph, Q)
            for k, ag in l_agraphs.items():
                encode(ag)
            for k, ag in r_agraphs.items():
                encode(ag)

            for i_v in range(i_w-1, -1, -1):
                v = h.nodes[i_v]
                pivot = h.nodes[int((i_w + i_v)/2)]
                if (i_w - i_v) % 2 == 1:
                    pivot += 0.5

                # Code and load without organization
                init_code, init_load = h.get_edge(v, w)
                best_code, best_load = init_code, init_load
                # Try to find better code using iteration
                code, load = h.find_best_iteration(v, w)
                if code and load < best_load:
                    best_code, best_load = code, load
                # Try to find better code using symmetry
                if pivot in Sgraphs and Sgraphs[pivot]:
                    code, load = Sgraphs[pivot].get_symmetry(v, w)
                    if code and load < best_load:
                        best_code, best_load = code, load

                for ag in l_agraphs.values():
                    code, load = ag.get_alternation(v, w)
                    if code and load < best_load:
                        best_code, best_load = code, load

                for ag in r_agraphs.values():
                    code, load = ag.get_alternation(v, w)
                    if code and load < best_load:
                        best_code, best_load = code, load

                h.add_edge(v, w, best_code, best_load)

                for i_u in range(i_v):
                    u = h.nodes[i_u]
                    c_uv, d_uv = h.get_edge(u, v)
                    c_uw, d_uw = h.get_edge(u, w)
                    if d_uw > d_uv + best_load:
                        h.add_edge(u, w, c_uv + best_code, d_uv + best_load)

        new_hyperstrings.append(h)

    g.clear()
    concatenate_hyperstrings(new_hyperstrings, graph = g)
