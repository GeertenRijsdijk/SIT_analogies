import sys
from numpy import argmin
sys.path.append('..')
from complexity_metrics import I_new_load
from QUIS import QUIS, create_labels

class Graph():
    def __init__(self, string = None):
        self.edges = {}
        if string:
            self.init_with_string(string)
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

    def get_edge(self, v_from, v_to):
        if v_to in self.edges[v_from]:
            return self.edges[v_from][v_to]

        substring = ''
        load = 0
        v = v_from
        while v != v_to:
            if v in self.edges and v+1 in self.edges[v]:
                substring += self.edges[v][v+1][0]
                load += self.edges[v][v+1][1]
            else:
                return
            v += 1
        return substring, len(substring)

    def add_edge(self, v_from, v_to, label):
        load = I_new_load(label)
        self.edges[v_from][v_to] = (label, load)

    # Check whether new label has a lower complexity than old label,
    # If so, replace the label
    def check_replace_edge(self, v_from, v_to, new_label, new_comp):
        if v_to in self.edges[v_from]:
            label, comp = self.edges[v_from][v_to]
            if new_comp < comp:
                self.edges[v_from][v_to] = (new_label, new_comp)

    def find_best_iteration(self, v_from, v_to):
        k = v_to - v_from
        for i in range(1, int(k**0.5) + 1):
            if k%i != 0:
                continue
            v_next = v_from
            last_substr = None
            while v_next < v_to:
                next_substr = None
                if v_next + i in self.edges[v_next]:
                    next_substr = self.edges[v_next][v_next + i][0]
                v_next += i
                if not next_substr:
                    break
                elif not last_substr:
                    last_substr = next_substr
                    continue
                elif next_substr != last_substr:
                    break

            if last_substr and last_substr == next_substr:
                new_str = str(int(k/i)) + '*(' + last_substr + ')'
                load = I_new_load(new_str)
                return new_str, load
        return None, float('inf')

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
            if previous_node[path[0]] == None:
                return None
            path = [previous_node[path[0]]] + path
        return path

class Sgraph(Graph):
    def __init__(self, string, pivot, Q):
        Graph.__init__(self)
        self.string = string
        self.pivot = pivot
        self.pivot_node = int(pivot + 1.5)
        max_len = min(len(string) - pivot - 1, pivot)
        self.N = len(string)
        # +2.5: +1 because there is 1 more node than there are string elements,
        #       +1 because range does not include the top
        #       +0.5 to round up
        self.nodes = [i for i in range(int(pivot + 2.5))]

        for n in self.nodes:
            self.edges[n] = {}

        for b_offset in range(int(max_len+0.5)):
            b = int(pivot - max_len + b_offset)
            for k in range(1, int(max_len - b_offset + 1.5)):
                rhs = int(pivot + max_len - b_offset - k + 1)
                if Q[b, k-1] == Q[rhs, k-1]:
                    chunk_str = '('+string[b:b+k]+')'
                    self.edges[b][b+k] = (chunk_str, k + 1*(k>1))

                    pivot_str = '('+string[b+k:rhs]+')'
                    complexity = rhs - b - k
                    self.edges[b+k][self.pivot_node] = (pivot_str, complexity)

        # for k, d  in self.edges.items():
        #     print(k, d)

    def get_symmetry(self, v_from, v_to):
        if self.pivot != (v_to + v_from - 1)/2:
            return None, None
        path = self.find_shortest_path(v_from, self.pivot_node)
        if not path:
            return None, None

        total_complexity = 0
        ret_str = 'S['
        for i in range(len(path)-1):
            chunk, complexity = self.edges[path[i]][path[i+1]]
            if chunk != '()':
                if path[i+1] == self.pivot_node:
                    ret_str += ','
                ret_str += chunk
                total_complexity += complexity
        ret_str += ']'
        return ret_str, total_complexity

class Agraph(Graph):
    def __init__(self, string, repeat_len, Q):
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
    s = 'abccba'
    # labels = create_labels(s)
    # Q = QUIS(list(s), labels)
    # sg = Sgraph(s, 2.5, Q)
    # print(sg.get_symmetry(0, 6))
    g = Graph(s)
    print(g)
    g.add_edge(1, 5, 'S[(b)(c)]')
    print(g.get_edge(1, 5))
    print(g.get_edge(0, 6))
    print(g.get_edge(2, 3))
