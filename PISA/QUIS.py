import numpy as np
from random import choice
import time

def QUIS(string, labels):
    # Step 0: Initialize arrays/variables
    # String + 2 lists get extra element to create 1 based indexing
    string = '-' + string
    NextList = [None for _ in string]
    NextOcc = ['-'] + [None for _ in string]
    LastOcc = ['-'] + [None for _ in string]
    new_list_pos = 0
    k = 1

    # Step 1: Create lists for 1-element substrings
    for str_index, c in enumerate(string[1:], start = 1):
        in_list = False
        for list_index in NextList:
            if list_index and string[list_index] == c:
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
            LastOcc = ['-'] + [None for _ in string]
            current_index = NextList[prev_index]
            b = current_index
            prev_b = b
            if b:
                NextList_items.append(b)

            while b:
                p = b + k
                labels[b-1, k-1] = current_index
                if p >= len(string):
                    if b not in NextList_items:
                        NextList_items.append(b)
                    NextOcc[prev_b] = None
                else:
                    p = string.index(string[p])
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
        NextList = [None for _ in string]
        next_index = 0
        for n in NextList_items:
            NextList[next_index] = n
            next_index = n
        k += 1
    return labels


if __name__ == '__main__':
    string = ''.join([choice(['A','B','C', 'D']) for _ in range(10)])
    r = np.arange(1,len(string)+1)
    labels = np.repeat([r], len(string), axis = 0)
    labels = np.transpose(labels)
    for i in range(len(string)):
        labels[len(string)-i:, i] = 0

    # start = time.time()
    # for i in range(50):
    m = QUIS(string, labels)
    # t = time.time() - start
    # print(t/50)

    #print(m)

    for k, col in enumerate(m.T, start = 1):
        d = {}
        for b, i in enumerate(col):
            if i == 0:
                continue
            if i in d:
                d[i].append(string[b:b+k])
            else:
                d[i] = [string[b:b+k]]

        #print(d)
        all_items = []
        for k in d:
            all_items += d[k]
            if len(set(d[k])) != 1:
                print('ERROR')
        if len(set(all_items)) != len(d.keys()):
            print('ERROR 2')
