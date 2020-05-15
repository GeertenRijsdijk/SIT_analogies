import numpy as np
from random import choice
#from graphs import Graph
import time

def QUIS(g, labels):
    # Step 0: Initialize arrays/variables
    N = g.len()+1
    _, hamil_edges = g.get_hamil_path()
    # Extra character at start of list to simulate 1-indexing
    hamil_edges = ['-'] + hamil_edges
    NextList = [None]*N
    NextOcc = ['-'] + [None]*N
    LastOcc = ['-'] + [None]*N
    new_list_pos = 0
    k = 1

    # Step 1: Create lists for 1-element substrings
    for str_index, c in enumerate(hamil_edges[1:], start = 1):
        in_list = False
        for list_index in NextList:
            if list_index and hamil_edges[list_index] == c:
                NextOcc[LastOcc[list_index]] = str_index
                LastOcc[list_index] = str_index
                in_list = True

        if not in_list:
            NextList[new_list_pos] = str_index
            LastOcc[str_index] = str_index
            new_list_pos = str_index

    # Step 2: Loop until there are no more lists left
    while any(x != None for x in NextList):
        # Step 3: Remove lists with only one substring
        prev_index = 0
        while prev_index != None and NextList[prev_index] != None:
            current_index = NextList[prev_index]
            if NextOcc[current_index] == None:
                NextList[prev_index] = NextList[current_index]
                NextList[current_index] = None
            else:
                prev_index = current_index

        # Step 4: Expand substrings:
        prev_index = 0
        NextList_items = []
        while prev_index != None:
            LastOcc = ['-'] + [None]*N
            current_index = NextList[prev_index]
            b = current_index
            prev_b = b
            if b:
                NextList_items.append(b)

            while b:
                p = b + k
                labels[b-1, k-1] = current_index
                if p >= N:
                    if b not in NextList_items:
                        NextList_items.append(b)
                    NextOcc[prev_b] = None
                else:
                    p = hamil_edges.index(hamil_edges[p])
                    if b == current_index:
                        LastOcc[p] = b
                    elif LastOcc[p]:
                        NextOcc[prev_b] = None
                        NextOcc[LastOcc[p]] = b
                        LastOcc[p] = b
                    else:
                        NextList_items.append(b)
                        NextOcc[prev_b] = None
                        LastOcc[p] = b

                prev_b = b
                b = NextOcc[b]

            prev_index = current_index

        NextList_items = sorted(NextList_items)
        NextList = [None]*N
        next_index = 0
        for n in NextList_items:
            NextList[next_index] = n
            next_index = n
        k += 1
    return labels

def create_labels(g):
    N = g.len()
    r = np.arange(1,N+1)
    labels = np.repeat([r], N, axis = 0)
    labels = np.transpose(labels)
    for i in range(N):
        labels[N-i:, i] = 0
    return labels

if __name__ == '__main__':
    # string = ''.join([choice(['A','B','C', 'D']) for _ in range(6)])
    # string = 'abcabc'
    # g = Graph(string)
    # labels = create_labels(g)
    # m = QUIS(g, labels)

    g = Graph()
    g.nodes = [3,5,8,10,13,15,17]
    g.edges = {k:{} for k in g.nodes}
    g.add_edge(3,5,'ac')
    g.add_edge(5,8,'ab')
    g.add_edge(8,10,'ae')
    g.add_edge(10,13,'ac')
    g.add_edge(13,15,'ab')
    g.add_edge(15,17,'ab')

    labels = create_labels(g)
    m = QUIS(g, labels)

    print(m)

    hp, he = g.get_hamil_path()
    he = [code for code, _ in he]

    for k, col in enumerate(m.T, start = 1):
        d = {}
        for b, i in enumerate(col):
            if i == 0:
                continue
            if i in d:
                d[i].append(he[b:b+k])
            else:
                d[i] = [he[b:b+k]]

        all_items = []
        print(d)
        for k in d:
            all_items += d[k]
            x = dict((x[0], x) for x in d[k]).values()
            if len(x) != 1:
                print('ERROR')

        a, counts = np.unique(all_items, return_counts=True)
        n_unique = 0
        passed = []
        for it in all_items:
            if not it in passed:
                passed.append(it)
                n_unique += 1
        if n_unique != len(d.keys()):
            print('ERROR 2')
