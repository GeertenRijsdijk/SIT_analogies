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
    if len(sys.argv) < 3:
        error = True
    if len(sys.argv) >= 4 and sys.argv[3] == 'F':
        bf = False
    if len(sys.argv) == 5 and sys.argv[4] == 'F':
        pisa = False
    try:
        k = int(sys.argv[1])
        N = int(sys.argv[2])
        if k < 0 or N < 0:
            error = True
    except:
        error = True
    if error:
        print('USAGE: time_comparison.py <k> <N> <bf> <PISA>')
        print('k (positive int) = maximum length of string (required)')
        print('N (positive int) = \
number of iterations average is taken over (required)')
        print('bf (T or F) = run brute-force compressor? (default T)')
        print('PISA (T or F) = run PISA compressor? (default T)')
        quit()


    x_axis = [i for i in range(k+1)]

    bf_times = [0]
    pisa_times = [0]
    for l in range(1, k+1):

        strings = []
        for n in range(N):
            s = ''.join([choice(['A','B','C', 'D']) for _ in range(l)])
            strings.append(s)

        if bf:
            print(l, 'BF   :', end = ' ', flush = True)
            start = time.time()
            for i, s in enumerate(strings):
                print(i, end = ' ', flush = True)
                compress_bf(s)
            t = (time.time() - start)/N
            bf_times.append(t)
            print('')

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
    plt.ylabel('time needed for compression')
    plt.legend()

    plt.show()
