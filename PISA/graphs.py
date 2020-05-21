import sys
from numpy import argmin
sys.path.append('..')
from complexity_metrics import IT_WEIGHT, SYM_WEIGHT, ALT_WEIGHT

'''
Turns a list of separate hyperstrings into a graph.
Input:
    - A list of graph objects
    - An optional base graph object
Output:
    - A graph object containing all nodes + edges in all hyperstrings
'''
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

'''
A class representing Graphs. Also used as a parent class for Sgraph, LeftAgraph
and RightAgraph
'''
class Graph():
    def __init__(self, string = None):
        self.edges = {}
        if string:
            self.init_with_string(string)
        else:
            self.nodes = []
        # Nonexistent pivot
        self.pivot_node = -1

    # Creates a graph for a given string of length N.
    # Graph has N+1 nodes and N edges, one for each character.
    def init_with_string(self, string):
        self.nodes = [i for i in range(len(string)+1)]
        for i, c in enumerate(string):
            self.edges[i] = {i+1:(c,1)}
        self.edges[len(string)] = {}

    # Returns a printable string representing the graph
    def __str__(self):
        ret_str = ''
        for edge in self.edges:
            for edge2 in self.edges[edge]:
                ret_str += str(edge) + ' -> ' + str(edge2)
                ret_str += ' ' + str(self.edges[edge][edge2]) + '\n'
        return ret_str

    # Clears all edges of graph
    def clear(self):
        self.edges = {k:{} for k in self.nodes}

    # Returns the length of the graph. -1 because there is one more node than
    # there are edges in the hamilton path
    def len(self):
        return len(self.nodes)-1

    # Returns number of nodes in hamilton path between two nodes, inclusive.
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

    # Returns the edge between two nodes, consisting of a label and load.
    # If there is no edge between the nodes, the label is constructed from the
    # path between the nodes that visits every node in between.
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

    # Adds an edge to the graph.
    def add_edge(self, n_from, n_to, label, load):
        self.edges[n_from][n_to] = (label, load)

    # Returns a graph with only nodes and edges between the two specified nodes.
    def subgraph(self, n_from, n_to):
        g = Graph()
        g.nodes = [n for n in self.nodes if n >= n_from and n <= n_to]
        g.edges = {k:{} for k in g.nodes}
        for node, d in self.edges.items():
            for node_2, edge in d.items():
                if node in g.nodes and node_2 in g.nodes:
                    g.edges[node][node_2] = edge
        return g

    # Finds the hamilton path starting at a specified node n.
    # Returns the nodes and edges of the path.
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

    # Splits a graph into all hyperstrings it contains.
    def split_hyperstrings(self):
        sn = self.start_nodes()
        hyperstrings = []
        # For every start node:
        for start_n in sn:
            # Ignore pivot node of Sgraph.
            if start_n == self.pivot_node:
                continue
            # Get the hamilton path of the node ...
            hp, _ = self.get_hamil_path(start_n)
            if isinstance(self, RightAgraph) and len(hp) > 1:
                hp = [self.source] + hp
            # ... create a new graph ...
            g = Graph()
            g.nodes = hp
            if self.pivot_node in g.nodes:
                g.nodes.remove(self.pivot_node)
            g.edges = {k:{} for k in hp}
            # ... and add all nodes/edges in the hamilton path.
            for n_from in hp:
                for n_to in self.edges[n_from]:
                    if n_to in hp and n_to != self.pivot_node:
                        g.edges[n_from][n_to] = self.edges[n_from][n_to]
            hyperstrings.append(g)
        return hyperstrings

    # Given two nodes, finds the best way to represent the edges between the
    # nodes as an iteration, if any.
    def find_best_iteration(self, n_start, n_end):
        # Get the number of edges between the two nodes.
        N = self.path_len(n_start, n_end)
        if N == None:
            return None, None
        N -= 1
        # For each possible divisor i of the number of edges:
        for i in range(1, int(N/2+1)):
            n_from = n_start
            # ... check whether i divides d. if it does ...
            if N%i != 0:
                continue
            n_next = self.next(n_from, i)
            label = self.get_edge(n_from, n_next)
            # ... loop over the edges, i steps at a time ...
            while n_from != n_end:
                # ... and check whether the labels are identical.
                next_label = self.get_edge(n_from, n_next)
                if next_label != label:
                    break
                label = next_label

                n_from = n_next
                n_next = self.next(n_from, i)

            # If all labels were identical ...
            if n_from == n_end and label == next_label:
                # ... Create the code for the iteration.
                it_label, it_load = label
                multiplier = int(N/i)
                code = str(multiplier) + '*(' + it_label + ')'
                load = it_load + 0.5
                return code, load
        return None, None

    # Dijkstra's algorithm for finding shortest path between two nodes
    def find_shortest_path(self, n_from, n_to):
        # Initialize necessary lists
        N = max(self.nodes)+1
        visited = []
        unvisited = self.nodes[:]
        distances = [0 if v == n_from else float('inf') for v in range(N)]
        previous_node = [None]*N

        # While we have not yet reached the goal node:
        while n_to not in visited:
            # Find the node with the smallest distance to any visited node ...
            current_ind = argmin([distances[i] for i in unvisited])
            current = unvisited[current_ind]
            unvisited.remove(current)

            # ... update the distances to its neighbours ...
            for neighbour in self.edges[current]:
                if neighbour in visited:
                    continue
                d = self.edges[current][neighbour][1]
                new_dist = d + distances[current]
                if new_dist < distances[neighbour]:
                    distances[neighbour] = new_dist
                    previous_node[neighbour] = current
            # ... and add it to the visited nodes.
            visited.append(current)

        # Construct path from end to start.
        path = [n_to]
        while path[0] != n_from:
            if previous_node[path[0]] == None:
                return None, None
            path = [previous_node[path[0]]] + path
        return path, distances[n_to]

    def find_all_paths(self, n_from, n_to):
        queue = [[n_from]]
        paths = []
        while queue != []:
            path = queue.pop(0)
            for next in self.edges[path[-1]]:
                new_path = path + [next]
                if next == n_to:
                    paths.append(new_path)
                else:
                    queue.append(new_path)

        return paths


'''
A class representing Sgraphs.
'''
class Sgraph(Graph):
    def __init__(self):
        Graph.__init__(self)

    # Creates the necessary nodes and edges to become an S-graph of a given
    # hyperstring, with specified pivot.
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

        # Create graph:
        # For each two nodes b, b_2 with the same distance from the pivot
        for i, node in enumerate(left):
            b = hamil_path.index(node)
            # For each length k:
            for k in range(1, len(left)-i):
                b2 = hamil_path.index(right[-i-k-1])
                # If the edges on the side of the pivot are identical:
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

    # Given two nodes, finds the optimal way to represent the edges between the
    # nodes as a symmetry.
    def get_symmetry(self, n_from, n_to):
        # Find the shortest path (if any) from the start to the pivot.
        # This is the best symmetry.
        path, _ = self.find_shortest_path(n_from, self.pivot_node)
        if not path or len(path) <= 2:
            return None, None

        # Construct the symmetry code from the graph.
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

    # Special clear for Sgraphs, leaving edges towards pivot node.
    def clear(self):
        new_edges = {k:{} for k in self.nodes}
        for n_from, to_dict in self.edges.items():
            for n_to, edge in to_dict.items():
                if n_to == self.pivot_node:
                    new_edges[n_from][n_to] = edge
        self.edges = new_edges

'''
A class representing Left-Alternating graphs.
'''
class LeftAgraph(Graph):
    def __init__(self):
        # Initialize Graph
        Graph.__init__(self)

    # Creates the necessary nodes and edges to become an left-alternation graph
    # of a given hyperstring.
    def construct_from_hyperstring(self, hs, rep_len, Q):
        # Set variables
        self.rep_len = rep_len
        self.hs = hs

        hamil_path, hamil_edges = hs.get_hamil_path()

        self.nodes = hs.nodes
        self.edges = {k:{} for k in self.nodes}
        self.sink = self.nodes[-1]
        self.sink_b = len(self.nodes)-1

        # For each two nodes in the graph:
        for b, node in enumerate(hamil_path[:-2]):
            for b_2, node_2 in enumerate(hamil_path[b+1:-1], start = b+1):
                # If the edges of the nodes+repeat lengths are identical:
                if Q[b, rep_len-1] == Q[b_2, rep_len-1]:
                    # Test whether pseudo-Achunks are present
                    _, testload_1 = hs.get_edge(node, node_2)
                    _, testload_2 = hs.get_edge(node_2, self.sink)
                    if testload_1 == float('inf') or testload_2 == float('inf'):
                        continue

                    # 1: Create edge for node -> node_2.
                    inter_node = hs.next(node, rep_len)
                    if inter_node == None:
                        label, load = hs.get_edge(node_2, self.sink)
                        label = '(' + label + ')'
                    else:
                        rep_label, _ = hs.get_edge(node, inter_node)
                        label_2, load = hs.get_edge(inter_node, node_2)
                        label = '(' + rep_label + '|' + label_2 + ')'
                    if b_2 - b <= rep_len:
                        load = float('inf')
                    self.edges[node][node_2] = (label, load)

                    # 2: Create edge for node_2 -> sink.
                    inter_node = hs.next(node_2, rep_len)
                    if inter_node == None:
                        label, load = hs.get_edge(node_2, self.sink)
                        label = '(' + label + ')'
                    else:
                        rep_label, _ = hs.get_edge(node_2, inter_node)
                        label_2, load = hs.get_edge(inter_node, self.sink)
                        label = '(' + rep_label + '|' + label_2 + ')'
                    if self.sink_b - b_2 <= rep_len:
                        load = float('inf')
                    self.edges[node_2][self.sink] = (label, load)

    # Given two nodes, finds the optimal way to represent the edges between the
    # nodes as a left-alternation.
    def get_alternation(self, n_from, n_to):
        # Find the shortest path (if any) from the start to the pivot.
        # This is the best alternation.
        path, dist = self.find_shortest_path(n_from, n_to)
        if not path or dist == float('inf'):
            return None, None

        # Construct the edge for the alternation.
        total_load = 0.5
        repeat_node = self.hs.next(path[0], self.rep_len)
        repeat, rep_load = self.hs.get_edge(path[0], repeat_node)
        code = '<(' + repeat + ')>/<'
        total_load += rep_load
        replace_str = '(' + repeat + '|'
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

    # Creates the necessary nodes and edges to become an right-alternation graph
    # of a given hyperstring.
    def construct_from_hyperstring(self, hs, rep_len, Q):
        # Set variables
        self.rep_len = rep_len
        self.hs = hs

        hamil_path, hamil_edges = hs.get_hamil_path()

        self.nodes = hs.nodes
        self.edges = {k:{} for k in self.nodes}
        self.source = self.nodes[0]

        # For each two nodes in the graph:
        for b, node in enumerate(hamil_path[rep_len:-1], start = rep_len):
            for b_2, node_2 in enumerate(hamil_path[b+1:], start = b+1):
                # If the edges of the nodes+repeat lengths are identical:
                if Q[b-rep_len, rep_len-1] == Q[b_2-rep_len, rep_len-1]:
                    # Test whether pseudo-Achunks are present
                    _, testload_1 = hs.get_edge(self.source, node)
                    _, testload_2 = hs.get_edge(node, node_2)
                    if testload_1 == float('inf') or testload_2 == float('inf'):
                        continue

                    # 1: Create edge for source -> node.
                    inter_node = hs.next(self.source, b - rep_len)
                    if inter_node == None:
                        label, load = hs.get_edge(self.source, node)
                        label = '(' + label + ')'
                    else:
                        label_1, load = hs.get_edge(self.source, inter_node)
                        rep_label, _ = hs.get_edge(inter_node, node)
                        label = '(' + label_1 + '|' + rep_label + ')'
                    if b <= rep_len:
                        load = float('inf')
                    self.edges[self.source][node] = (label, load)

                    # 2: Create edge for node -> node_2.
                    inter_node = hs.next(node, b_2 - b - rep_len)
                    if inter_node == None:
                        label, load = hs.get_edge(node, node_2)
                        label = '(' + label + ')'
                    else:
                        label_1, load = hs.get_edge(node, inter_node)
                        rep_label, _ = hs.get_edge(inter_node, node_2)
                        label = '(' + label_1 + '|' + rep_label + ')'
                    if b_2 - b <= rep_len:
                        load = float('inf')
                    self.edges[node][node_2] = (label, load)

    # Special is_start function for Right-alternation graphs.
    # Checks whether a node has no incoming edges. Edges coming from the source
    # do not count.
    def is_start_node(self, n):
        if n == self.source:
            return False
        for i in range(n):
            if i == self.source:
                continue
            if i in self.edges.keys() and n in self.edges[i].keys():
                return False
        return True

    # Given two nodes, finds the optimal way to represent the edges between the
    # nodes as a right-alternation.
    def get_alternation(self, n_from, n_to):
        # Find the shortest path (if any) from the start to the pivot.
        # This is the best alternation.
        path, dist = self.find_shortest_path(n_from, n_to)
        if not path or dist == float('inf'):
            return None, None

        # Construct the edge for the alternation
        total_load = 0.5
        repeat_node = self.hs.nodes[self.hs.nodes.index(path[1])-self.rep_len]
        repeat, rep_load = self.hs.get_edge(repeat_node, path[1])
        replace_str = '|' + repeat + ')'
        code = '<'
        for i in range(len(path)-1):
            chunk, load = self.edges[path[i]][path[i+1]]
            chunk = chunk.replace(replace_str, ')')
            code += chunk
            total_load += load
        code += '>/<(' + repeat + ')>'
        total_load += rep_load
        return code, total_load
