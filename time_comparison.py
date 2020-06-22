from matplotlib import pyplot as plt
from random import choice
import sys
import time

from compressor_bruteforce import compress_bf
from PISA.encode import encode
from PISA.graphs import Graph

if __name__ == '__main__':
    error = False
    bf = True
    pisa = True
    pisa_c = False
    if len(sys.argv) < 3:
        error = True
    if len(sys.argv) >= 4 and sys.argv[3] == 'F':
        bf = False
    if len(sys.argv) >= 5 and sys.argv[4] == 'F':
        pisa = False
    if len(sys.argv) >= 6 and sys.argv[5] == 'T':
        pisa_c = True
    try:
        k = int(sys.argv[1])
        N = int(sys.argv[2])
        if k < 0 or N < 0:
            error = True
    except:
        error = True
    if error:
        print('USAGE: time_comparison.py <k> <N> <bf> <PISA> <PISA_C>')
        print('k (positive int) = maximum length of string (required)')
        print('N (positive int) = \
number of iterations average is taken over (required)')
        print('bf (T or F) = run brute-force compressor? (default T)')
        print('PISA (T or F) = run PISA compressor? (default T)')
        print('PISA_C (T or F) = create testfiles for original PISA? \
(default F)')
        quit()


    x_axis = [i for i in range(k+1)]

    bf_times = [0]
    pisa_times = [0]

    strings = []
    for n in range(N):
        strings.append('')

    for l in range(1, k+1):
        for i, s in enumerate(strings):
            s += choice(['A','B','C', 'D'])
            strings[i] = s
        # Create test files for original PISA speed comparison
        if pisa_c:
            with open('PISA_TESTS/test_' + str(l) + '.txt', 'w') as f:
                for s in strings:
                    f.write(s + '\n\n')
        # Test brute-force compressor
        if bf:
            print(l, 'BF   :', end = ' ', flush = True)
            start = time.time()
            for i, s in enumerate(strings):
                print(i, end = ' ', flush = True)
                compress_bf(s)
            t = (time.time() - start)/N
            bf_times.append(t)
            print('')
        # Test PISA-based compressor
        if pisa:
            print(l, 'PISA :', end = ' ', flush = True)
            start = time.time()
            for i, s in enumerate(strings):
                print(i, end = ' ', flush = True)
                g = Graph(s)
                encode(g)
            print('\n')
            t = (time.time() - start)/N
            pisa_times.append(t)

    if bf:
        plt.plot(x_axis, bf_times, label = 'brute-force')
    if pisa:
        plt.plot(x_axis, pisa_times, label = 'PISA-based')

    plt.xlabel('string length')
    plt.ylabel('time needed for compression (seconds)')
    plt.legend()

    plt.show()
