import sys
from numpy import argmin
sys.path.append('..')
from .QUIS import QUIS, create_labels

def concatenate_hyperstrings(hyperstrings, graph = None):
    if not graph:
        graph = Graph()

    for hs in hyperstrings:
        for node in hs.nodes:
            if node not in graph.nodes:
                graph.nodes.append(node)
        for n_from in hs.edges:
            if n_from not in graph.edges:
                graph.edges[n_from] = {}
            for n_to in hs.edges[n_from]:
                graph.edges[n_from][n_to] = hs.edges[n_from][n_to]
    graph.nodes.sort()
    return graph

class Graph():
    def __init__(self, string = None):
        self.edges = {}
        if string:
            self.init_with_string(string)
        else:
            self.nodes = []
        # Nonexistent pivot
        self.pivot_node = -1

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

    def clear(self):
        self.edges = {k:{} for k in self.nodes}

    def len(self):
        return len(self.nodes)-1

    # Number of nodes in hamilton path between n_from and n_to, inclusive
    def path_len(self, n_from, n_to):
        if n_from == None or n_to == None:
            return None
        length = 1
        n_next = self.next(n_from)
        while n_from != n_to and n_next != None:
            length += 1
            n_from = n_next
            n_next = self.next(n_from)
        if n_from != n_to and n_next == None:
            return None
        return length

    # Returns nth next node after n_from in hamilton path.
    def next(self, n_from, n = 1):
        for i in range(n):
            if len(self.edges[n_from]) == 0:
                return None
            n_from = min([k for k in self.edges[n_from]])
        return n_from

    # Returns list of all nodes without incoming edges.
    def start_nodes(self):
        return [n for n in self.nodes if self.is_start_node(n)]

    # Check whether a node has incoming edges.
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

    def add_edge(self, n_from, n_to, label, load):
        self.edges[n_from][n_to] = (label, load)

    def subgraph(self, n_from, n_to):
        g = Graph()
        g.nodes = [n for n in self.nodes if n >= n_from and n <= n_to]
        g.edges = {k:{} for k in g.nodes}
        for node, d in self.edges.items():
            for node_2, edge in d.items():
                if node in g.nodes and node_2 in g.nodes:
                    g.edges[node][node_2] = edge
        return g

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
            if start_n == self.pivot_node:
                continue
            hp, _ = self.get_hamil_path(start_n)
            if isinstance(self, RightAgraph) and len(hp) > 1:
                hp = [self.source] + hp
            g = Graph()
            g.nodes = hp
            if self.pivot_node in g.nodes:
                g.nodes.remove(self.pivot_node)
            g.edges = {k:{} for k in hp}
            for n_from in hp:
                for n_to in self.edges[n_from]:
                    if n_to in hp and n_to != self.pivot_node:
                        g.edges[n_from][n_to] = self.edges[n_from][n_to]
            hyperstrings.append(g)
        return hyperstrings

    def find_best_iteration(self, n_start, n_end):
        N = self.path_len(n_start, n_end)
        if N == None:
            return None, None
        N -= 1
        for i in range(1, int(N/2+1)):
            n_from = n_start
            if N%i != 0:
                continue
            n_next = self.next(n_from, i)
            label = self.get_edge(n_from, n_next)
            while n_from != n_end:
                next_label = self.get_edge(n_from, n_next)
                if next_label != label:
                    break
                label = next_label

                n_from = n_next
                n_next = self.next(n_from, i)

            if n_from == n_end and label == next_label:
                it_label, it_load = label
                multiplier = int(N/i)
                code = str(multiplier) + '*(' + it_label + ')'
                load = it_load + 0.5
                return code, load
        return None, None

    # Dijkstra's algorithm for finding shortest path between two nodes
    def find_shortest_path(self, n_from, n_to):
        N = max(self.nodes)+1
        visited = []
        unvisited = self.nodes[:]
        distances = [0 if v == n_from else float('inf') for v in range(N)]
        previous_node = [None]*N

        while n_to not in visited:
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
        path = [n_to]
        while path[0] != n_from:
            if previous_node[path[0]] == None:
                return None, None
            path = [previous_node[path[0]]] + path
        return path, distances[n_to]

class Sgraph(Graph):
    def __init__(self):
        # Initialize Graph
        Graph.__init__(self)

    def construct_from_hyperstring(self, hs, pivot, Q):
        # Set variables
        self.pivot = pivot
        #self.pivot_node = int(pivot + 1)
        self.N = hs.len()
        max_len = min(self.N - pivot - 1, pivot)

        hamil_path, hamil_edges = hs.get_hamil_path()
        self.pivot_node = min([h for h in hamil_path if h > pivot])

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
                b2 = hamil_path.index(right[-i-k-1])
                if Q[b, k-1] == Q[b2, k-1]:
                    start_node, end_node = node, left[i + k]
                    # Add S-chunk edge
                    label, load = hs.get_edge(start_node, end_node)
                    label = '(' + label + ')'
                    self.edges[start_node][end_node] = (label, load)

                    # Add pivot edge
                    label, load = hs.get_edge(end_node, right[-i-k-1])
                    label = '(' + label + ')'
                    self.edges[end_node][self.pivot_node] = (label, load)

    def get_symmetry(self, n_from, n_to):
        path, _ = self.find_shortest_path(n_from, self.pivot_node)
        if not path or len(path) <= 2:
            return None, None

        total_complexity = 0.5
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

    # Special clear for Sgraphs, leaving edges towards pivot node
    def clear(self):
        new_edges = {k:{} for k in self.nodes}
        for n_from, to_dict in self.edges.items():
            for n_to, edge in to_dict.items():
                if n_to == self.pivot_node:
                    new_edges[n_from][n_to] = edge
        self.edges = new_edges

class LeftAgraph(Graph):
    def __init__(self):
        # Initialize Graph
        Graph.__init__(self)

    def construct_from_hyperstring(self, hs, rep_len, Q):
        # Set variables
        self.rep_len = rep_len
        self.hs = hs

        hamil_path, hamil_edges = hs.get_hamil_path()

        self.nodes = hs.nodes
        self.edges = {k:{} for k in self.nodes}
        self.sink = self.nodes[-1]
        self.sink_b = len(self.nodes)-1

        for b, node in enumerate(hamil_path[:-2]):
            for b_2, node_2 in enumerate(hamil_path[b+1:-1], start = b+1):
                if Q[b, rep_len-1] == Q[b_2, rep_len-1]:
                    _, testload_1 = hs.get_edge(node, node_2)
                    _, testload_2 = hs.get_edge(node_2, self.sink)
                    if testload_1 == float('inf') or testload_2 == float('inf'):
                        continue
                    inter_node = hs.next(node, rep_len)
                    if inter_node == None:
                        label, load = hs.get_edge(node_2, self.sink)
                        label = '(' + label + ')'
                    else:
                        label_1, _ = hs.get_edge(node, inter_node)
                        label_2, load = hs.get_edge(inter_node, node_2)
                        label = '(' + label_1 + label_2 + ')'
                    if b_2 - b <= rep_len:
                        load = float('inf')
                    self.edges[node][node_2] = (label, load)

                    inter_node = hs.next(node_2, rep_len)
                    if inter_node == None:
                        label, load = hs.get_edge(node_2, self.sink)
                        label = '(' + label + ')'
                    else:
                        label_1, _ = hs.get_edge(node_2, inter_node)
                        label_2, load = hs.get_edge(inter_node, self.sink)
                        label = '(' + label_1 + label_2 + ')'
                    if self.sink_b - b_2 <= rep_len:
                        load = float('inf')
                    self.edges[node_2][self.sink] = (label, load)

    def get_alternation(self, n_from, n_to):
        path, dist = self.find_shortest_path(n_from, n_to)
        if not path or dist == float('inf'):
            return None, None

        total_load = 0.5
        repeat_node = self.hs.next(path[0], self.rep_len)
        repeat, rep_load = self.hs.get_edge(path[0], repeat_node)
        code = '<(' + repeat + ')>/<'
        total_load += rep_load
        replace_str = '(' + repeat
        for i in range(len(path)-1):
            chunk, load = self.edges[path[i]][path[i+1]]
            chunk = chunk.replace(replace_str, '(')
            code += chunk
            total_load += load
        code += '>'
        return code, total_load

class RightAgraph(Graph):
    def __init__(self):
        # Initialize Graph
        Graph.__init__(self)

    def construct_from_hyperstring(self, hs, rep_len, Q):
        # Set variables
        self.rep_len = rep_len
        self.hs = hs

        hamil_path, hamil_edges = hs.get_hamil_path()

        self.nodes = hs.nodes
        self.edges = {k:{} for k in self.nodes}
        self.source = self.nodes[0]

        for b, node in enumerate(hamil_path[rep_len:-1], start = rep_len):
            for b_2, node_2 in enumerate(hamil_path[b+1:], start = b+1):
                if Q[b-rep_len, rep_len-1] == Q[b_2-rep_len, rep_len-1]:
                    inter_node = hs.next(self.source, b - rep_len)
                    _, testload_1 = hs.get_edge(self.source, node)
                    _, testload_2 = hs.get_edge(node, node_2)
                    if testload_1 == float('inf') or testload_2 == float('inf'):
                        continue
                    if inter_node == None:
                        label, load = hs.get_edge(self.source, node)
                        label = '(' + label + ')'
                    else:
                        label_1, load = hs.get_edge(self.source, inter_node)
                        label_2, _ = hs.get_edge(inter_node, node)
                        label = '(' + label_1 + label_2 + ')'
                    if b <= rep_len:
                        load = float('inf')
                    self.edges[self.source][node] = (label, load)

                    inter_node = hs.next(node, b_2 - b - rep_len)
                    if inter_node == None:
                        label, load = hs.get_edge(node, node_2)
                        label = '(' + label + ')'
                    else:
                        label_1, load = hs.get_edge(node, inter_node)
                        label_2, _ = hs.get_edge(inter_node, node_2)
                        label = '(' + label_1 + label_2 + ')'
                    if b_2 - b <= rep_len:
                        load = float('inf')
                    self.edges[node][node_2] = (label, load)

    # Check whether a node has incoming edges.
    def is_start_node(self, n):
        if n == self.source:
            return False
        for i in range(n):
            if i == self.source:
                continue
            if i in self.edges.keys() and n in self.edges[i].keys():
                return False
        return True

    def get_alternation(self, n_from, n_to):
        path, dist = self.find_shortest_path(n_from, n_to)
        if not path or dist == float('inf'):
            return None, None

        total_load = 0.5
        repeat_node = self.hs.nodes[self.hs.nodes.index(path[1])-self.rep_len]
        repeat, rep_load = self.hs.get_edge(repeat_node, path[1])
        replace_str = repeat + ')'
        code = '<'
        for i in range(len(path)-1):
            chunk, load = self.edges[path[i]][path[i+1]]
            chunk = chunk.replace(replace_str, ')')
            code += chunk
            total_load += load
        code += '>/<(' + repeat + ')>'
        total_load += rep_load
        return code, total_load
