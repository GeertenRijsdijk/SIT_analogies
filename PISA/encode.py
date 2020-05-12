from hyperstrings import Graph, Sgraph, Agraph
from QUIS import QUIS, create_labels

def encode(g):

    sgraphs = []
    for i in range(N):
        sgraphs.append(Sgraph(string, i, Q))
        if i != N-1:
            sgraphs.append(Sgraph(string, i+0.5, Q))


    for w in range(1, N+1):
        for v in range(w-1, -1, -1):
            init_code, init_load = g.get_edge(v, w)
            best_code, best_load = init_code, init_load
            code, load = g.find_best_iteration(v, w)
            if load < best_load:
                best_code, best_load = code, load
            for sg in sgraphs:
                code, load = sg.get_symmetry(v, w)
                if code != None:
                    print(code, load)
                if code and load < best_load:
                    best_code, best_load = code, load

            if best_load < init_load:
                g.add_edge(v, w, best_code)

            for u in range(v):
                c_uv, d_uv = g.get_edge(u, v)
                print(u, w)
                c_uw, d_uw = g.get_edge(u, w)
                if d_uw > d_uv + best_load:
                    g.add_edge(u, w, c_uv + best_code)


    print(g)
    print(g.find_shortest_path(0, len(string)))

if __name__ == '__main__':
    g = Graph(string = string)
    N = len(string)
    labels = create_labels(string)
    Q = QUIS(list(string), labels)
