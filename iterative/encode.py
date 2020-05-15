from graphs import Graph, Sgraph, concatenate_hyperstrings
from QUIS import QUIS, create_labels
import sys
sys.path.append('..')
from decompressor import decompress
from complexity_metrics import I_new_load

# Create S-Graphs
def create_sgraphs(h, Q):
    Sgraphs = {}
    n_from = h.nodes[0]
    n_to = h.next(n_from)
    while h.next(n_to) != None:
        Sgraphs[n_to] = Sgraph(h, n_to, Q)
        n_from = n_to
        n_to = h.next(n_from)
        if h.next(n_to) != None:
            Sgraphs[n_from + 0.5] = Sgraph(h, n_from + 0.5, Q)
    return Sgraphs

def encode(g):
    hyperstrings = g.split_hyperstrings()

    # Process individual hyperstrings
    new_hyperstrings = []
    for h in hyperstrings:
        labels = create_labels(h)
        Q = QUIS(h, labels)
        Sgraphs = create_sgraphs(h, Q)

        for i_w, w in enumerate(h.nodes[1:], start = 1):
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
                if pivot in Sgraphs:
                    code, load = Sgraphs[pivot].get_symmetry(v, w)
                    if code and load < best_load:
                        best_code, best_load = code, load

                h.add_edge(v, w, best_code, best_load)

                for i_u in range(i_v):
                    u = h.nodes[i_u]
                    c_uv, d_uv = h.get_edge(u, v)
                    c_uw, d_uw = h.get_edge(u, w)
                    if d_uw > d_uv + best_load:
                        h.add_edge(u, w, c_uv + best_code, d_uw)

            Sgraphs = create_sgraphs(h, Q)
            # for k, v in Sgraphs.items():
            #     Sgraphs[k] = encode(v)

        new_hyperstrings.append(h)

    new_graph = concatenate_hyperstrings(new_hyperstrings)
    return new_graph

if __name__ == '__main__':
    s = 'abcba'
    g = Graph(s)
    new_g = encode(g)
    path = new_g.find_shortest_path(new_g.nodes[0], new_g.nodes[-1])
    result_code = ''
    result_load = 0
    for i in range(len(path)-1):
        label, load = new_g.get_edge(path[i], path[i+1])
        result_code += label + ' '
        result_load += load
    print(result_code, )
    l = I_new_load(result_code)
    d = decompress(result_code)
    print(d, d == s)
    print(result_load, l, l == result_load)
    quit()

    # g1 = Graph()
    # g1.nodes = [0,2,4,6,7]
    # g1.edges = {
    #     0:{2:('ab', 2)},
    #     2:{4:('cd', 2)},
    #     4:{6:('ef', 2)},
    #     6:{7:('g', 1)},
    #     7:{}
    # }
    # shortest = encode(g1)
    # print(shortest)
