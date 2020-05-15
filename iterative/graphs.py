import sys
from numpy import argmin
sys.path.append('..')
from complexity_metrics import I_new_load
from QUIS import QUIS, create_labels

def concatenate_hyperstrings(hyperstrings):
    g = Graph()
    for hs in hyperstrings:
        for node in hs.nodes:
            if node not in g.nodes:
                g.nodes.append(node)
        for n_from in hs.edges:
            if n_from not in g.edges:
                g.edges[n_from] = {}
            for n_to in hs.edges[n_from]:
                g.edges[n_from][n_to] = hs.edges[n_from][n_to]
    g.nodes.sort()
    return g

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

    def next(self, n_from):
        if len(self.edges[n_from]) == 0:
            return None
        return min([k for k in self.edges[n_from]])

    def start_nodes(self):
        return [n for n in self.nodes if self.is_start_node(n)]

    def is_start_node(self, n):
        for i in range(n):
            if i in self.edges.keys() and n in self.edges[i].keys():
                return False
        return True

    def get_edge(self, n_from, n_end):
        if n_end in self.edges[n_from]:
            return self.edges[n_from][n_end]

        total_label = ''
        total_load = 0
        n_to = self.next(n_from)
        while n_to != None and n_from != n_end:
            label, load = self.edges[n_from][n_to]
            total_label += label
            total_load += load
            n_from = n_to
            n_to = self.next(n_from)

        return total_label, total_load

    def add_edge(self, n_from, n_to, label, load = None):
        if load == None:
            load = I_new_load(label)
        self.edges[n_from][n_to] = (label, load)

    def get_hamil_path(self, n = None):
        if n == None:
            n = self.nodes[0]
        hamil_path = []
        hamil_edges = []
        n_next = n
        while n != None:
            n_next = self.next(n)
            hamil_path.append(n)
            if n_next != None:
                hamil_edges.append(self.edges[n][n_next])
            n = n_next

        return hamil_path, hamil_edges

    def split_hyperstrings(self):
        sn = self.start_nodes()
        hyperstrings = []
        for start_n in sn:
            hp, _ = self.get_hamil_path(start_n)
            g = Graph()
            g.nodes = hp
            g.edges = {k:{} for k in hp}
            for n_from in hp:
                for n_to in self.edges[n_from]:
                    if n_to in hp:
                        g.edges[n_from][n_to] = self.edges[n_from][n_to]
            hyperstrings.append(g)
        return hyperstrings

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
        return None, None

    # Check whether new label has a lower complexity than old label,
    # If so, replace the label
    def check_replace_edge(self, n_from, n_to, new_label, new_comp):
        if n_to in self.edges[n_from]:
            label, comp = self.edges[n_from][n_to]
            if new_comp < comp:
                self.edges[n_from][n_to] = (new_label, new_comp)

    # Dijkstra's algorithm for finding shortest path between two nodes
    def find_shortest_path(self, v_from, v_to):
        N = max(self.nodes)+1
        visited = []
        unvisited = self.nodes[:]
        distances = [0 if v == v_from else float('inf') for v in range(N)]
        previous_node = [None]*N

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
    def __init__(self, hyperstring, pivot, Q):
        # Initialize Graph
        Graph.__init__(self)
        # Set variables
        self.hs = hyperstring
        self.pivot = pivot
        self.pivot_node = int(pivot + 1)
        self.N = hyperstring.len()
        max_len = min(self.N - pivot - 1, pivot)
        hamil_path, hamil_edges = self.hs.get_hamil_path()
        hamil_codes = [he[0] for he in hamil_edges]
        hamil_loads = [he[1] for he in hamil_edges]
        #print(hamil_path)

        # split lists into left and right of pivot
        left, right = [], []
        for i, n in enumerate(hamil_path):
            if n <= pivot:
                left.append(n)
            if n >= pivot:
                right.append(n)

        # Remove nodes from either list to make them the same length
        diff = len(left) - len(right)
        if diff > 0:
            left = left[diff:]
        elif diff < 0:
            right = right[:diff]

        # Graph nodes are the nodes on the left of the pivot, +1 pivot node.
        self.nodes = left + [self.pivot_node]
        self.edges = {k:{} for k in self.nodes}

        # Create graph
        for i, node in enumerate(left):
            b = hamil_path.index(node)
            for k in range(1, len(left)-i):
                #print(-b-k-1)
                b2 = hamil_path.index(right[-i-k-1])
                if Q[b, k-1] == Q[b2, k-1]:
                    start_node, end_node = node, left[i + k]
                    # Add S-chunk edge
                    label, load = self.hs.get_edge(start_node, end_node)
                    label = '(' + label + ')'
                    if len(label) > 1:
                        load += 1
                    self.edges[start_node][end_node] = (label, load)

                    # Add pivot edge
                    label, load = self.hs.get_edge(end_node, b2)
                    label = '(' + label + ')'
                    if len(label) > 1:
                        load += 1
                    self.edges[end_node][self.pivot_node] = (label, load)

    def get_symmetry(self, v_from, v_to):
        if self.pivot != (v_to + v_from)/2:
            return None, None
        path = self.find_shortest_path(v_from, self.pivot_node)
        if not path or len(path) <= 2:
            return None, None
        if len(path) == 3 and self.get_edge(path[-2], path[-1])[0] == '()':
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

if __name__ == '__main__':

    g1 = Graph()
    g1.nodes = [0,2,4,6,7]
    g1.edges = {
        0:{2:('ab', 2), 4:('xxxx', 4)},
        2:{4:('cd', 2)},
        4:{6:('ef', 2)},
        6:{7:('g', 1)},
        7:{}
    }
    print(g1.get_edge(0,4))
    g1 = Graph('abbacacada')
    print(g1.get_edge(0,10))
    # labels = create_labels(g1)
    # Q = QUIS(g1, labels)
    #
    # sg = Sgraph(g1, 2, Q)
    # print(sg.get_symmetry(1, 3))
