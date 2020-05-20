import numpy as np

'''
The QUick Identification of all Substrings (QUIS) algorithm, based on the
version as defined in 'simplicity in vision', by Peter A. van der Helm.

Input:
    - a hyperstring (Graph object) with a hamilton path of N edges
    - a NxN triangular matrix, initialized with labels[b, k] = b
Output:
    - a NxN matrix indicating identity relationships between subpaths of the
    hamilton path.
Example:
    Input:
        - A hyperstring of the string 'ababac'
        - The 6x6 triangular matrix, initialized with labels[b, k] = b
    Output: A numpy matrix of form:

        [   [ 1  1  1  1  1  1 ]
            [ 2  2  2  2  2  0 ]
            [ 1  1  1  3  0  0 ]
            [ 2  2  4  0  0  0 ]
            [ 1  5  0  0  0  0 ]
            [ 6  0  0  0  0  0 ]
        ]
'''
def QUIS(g, labels):
    # Step 0: Initialize arrays/variables
    N = g.len()+1
    _, hamil_edges = g.get_hamil_path()
    # Add extra character at start of list to simulate 1-indexing
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
            # Reset the LastOcc list
            LastOcc = ['-'] + [None]*N
            current_index = NextList[prev_index]
            b = current_index
            prev_b = b
            if b:
                NextList_items.append(b)

            # Loop over the linked list
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

        # Recreate the Nextlist
        NextList_items = sorted(NextList_items)
        NextList = [None]*N
        next_index = 0
        for n in NextList_items:
            NextList[next_index] = n
            next_index = n
        k += 1
    return labels

'''
Given a graph, creates a triangular matrix of labels used in QUIS

Input:
    - a hyperstring (Graph object) with a hamilton path of N edges
Output:
    - a NxN triangular matrix, initialized with labels[b, k] = b
Example:
    Input:
        - A hyperstring of the string 'ababac'
    Output: A numpy matrix of form:

        [   [ 1  1  1  1  1  1 ]
            [ 2  2  2  2  2  0 ]
            [ 3  3  3  3  0  0 ]
            [ 4  4  4  0  0  0 ]
            [ 5  5  0  0  0  0 ]
            [ 6  0  0  0  0  0 ]
        ]
'''
def create_labels(g):
    N = g.len()
    r = np.arange(1,N+1)
    labels = np.repeat([r], N, axis = 0)
    labels = np.transpose(labels)
    for i in range(N):
        labels[N-i:, i] = 0
    return labels
