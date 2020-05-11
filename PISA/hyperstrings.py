import sys
from numpy import argmin
sys.path.append('..')
from complexity_metrics import I_new_load
from QUIS import QUIS, create_labels

class Graph():
    def __init__(self, string = None):
        self.edges = {}
        if string:
            self.init_with_string()
        else:
            self.nodes = []

    def init_with_string(self, string):
        self.nodes = [i for i in range(len(string)+1)]
        for i, c in enumerate(string):
            self.edges[i] = {i+1:(c,1)}
        self.edges[len(string)] = {}

    def __str__(self):
        ret_str = ''
        for edge in self.edges:
            for edge2 in self.edges[edge]:
                ret_str += str(edge) + ' -> ' + str(edge2)
                ret_str += ' ' + str(self.edges[edge][edge2]) + '\n'
        return ret_str

    def len(self):
        return len(self.nodes)-1

    def add_edge(self, v_from, v_to, label):
        load = I_new_load(label)
        self.edges[v_from][v_to] = (label, load)

    # Dijkstra's algorithm for finding shortest path between two nodes
    def find_shortest_path(self, v_from, v_to):
        visited = []
        unvisited = self.nodes[:]
        distances = [0 if v == v_from else float('inf') for v in self.nodes]
        previous_node = [None for _ in self.nodes]

        while v_to not in visited:
            current_ind = argmin([distances[i] for i in unvisited])
            current = unvisited[current_ind]
            unvisited.remove(current)

            for neighbour in self.edges[current]:
                if neighbour in visited:
                    continue
                d = self.edges[current][neighbour][1]
                new_dist = d + distances[current]
                if new_dist < distances[neighbour]:
                    distances[neighbour] = new_dist
                    previous_node[neighbour] = current
            visited.append(current)

        # Construct path from end to start
        path = [v_to]
        while path[0] != v_from:
            path = [previous_node[path[0]]] + path
        return path

class Sgraph(Graph):
    def __init__(self, string, pivot):
        Graph.__init__(self)
        self.string = string
        self.pivot = pivot
        max_len = min(len(string) - pivot - 1, pivot)
        n_nodes = max_len + 1
        self.nodes = [i for i in range(n_nodes)]
        self.N = len(string)
        for n in self.nodes:
            self.edges[n] = {}
        self.pivots = {}

        for b in range(pivot - max_len, pivot):
            rhs = pivot+max_len-b+1
            for k in range(max_len - b):
                if Q[b, k] == Q[rhs - k - 1, k]:
                    chunk_str = '('+string[b:b+k+1]+')'
                    self.edges[b][b+k+1] = (chunk_str, k+1)
                    pivot_str = '('+string[b+k+1:rhs-k-1]+')'
                    complexity = (rhs-k-1) - (b+k+1)
                    self.pivots[b+k+1] = (pivot_str, complexity)
        print(self.edges)
        print(self.pivots)

class Agraph(Graph):
    def __init__(self, string, repeat_len):
        Graph.__init__(self)
        self.string = string
        self.rl = repeat_len
        self.nodes = [i for i in range(len(string)+1)]
        self.N = len(string)
        for n in self.nodes:
            self.edges[n] = {}

        for b in range(len(string)-1):
            for b2 in range(b+1, len(string)):

                if Q[b, self.rl-1] == Q[b2, self.rl-1]:
                    c1 = b2 - b
                    c2 = self.N - b2
                    self.edges[b][b2] = ('('+string[b:b2]+')', c1)
                    self.edges[b2][self.N] = ('('+string[b2:self.N]+')', c2)

        print(self.edges)


if __name__ == '__main__':
    s = 'abcdcba'
    labels = create_labels(s)
    Q = QUIS(list(s), labels)
    sg = Sgraph(s, 3)
    ag = Agraph(s, 2)
