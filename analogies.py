from compressor_bruteforce import compress
from decompressor import decompress
from complexity_metrics import I_new_load, analogy_load
from symbol_replacement import replace_left_right
import sys

'''
an the 3 parts of an analogy, finds possible answers to the analogy.

A penalty can be given, increasing the complexity of all codes generated
by this amount.

EX: For the analogy ABA:ACA::ADA:?
find_solves_of_codes(codes, 'ABA', 'ACA', 'ADA')
Returns a list of sets, which contain:
    1: The found solution
    2: The complexity of this solution
    3: The code the solution was based on
    4: The code when applied to the right-hand side of the analogy.
'''
def find_solves_of_codes(l1, l2, r1, penalty = 0):
    solves = []
    # Find all codes
    codes, _ = compress(l1+l2)
    for code in codes:
        # Replace the symbols in the codes
        new_codes = replace_left_right(code, l1, r1)
        for new_code in new_codes:
            # Decompress the codes
            d = decompress(new_code)

            # Add them to the answers, only if the found string starts with r1
            if d[:len(r1)] == r1:
                complexity = analogy_load(code) + analogy_load(new_code) \
                    + penalty
                solves.append((d[len(r1):], round(complexity,2), code, new_code))

    return solves

'''
Given an analogy, runs the previous function twice to find all possible answers:
An analogy of form A:B::C:? is also run as A:C::B:?

Answers are returned in the same format as the previous function.
'''
def predict_analogy(string, n_answers = 'all'):
    try:
        l, r = string.split('::')
        l1, l2 = l.split(':')
        r1, r2 = r.split(':')
    except:
        print('Analogy should be of form A:B::C:?')
        quit()

    solves_1 = find_solves_of_codes(l1, l2, r1)
    solves_2 = find_solves_of_codes(l1, r1, l2, penalty = 1)
    solves = sorted(solves_1 + solves_2, key = lambda x:x[1])
    if n_answers == 'all':
        return solves
    else:
        return solves[:n_answers]

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('USAGE: analogies.py <analogy> <n answers>')
        print('Analogy should be of form A:B::C:?')
        print('Leave <n answers> empty for all answers.')
        quit()
    n_answers = 'all'
    if len(sys.argv) == 3:
        if (not sys.argv[2].isdigit() or int(sys.argv[2]) <= 0):
            print('USAGE: analogies.py <analogy> <n answers>')
            print('<n answers> should be a positive, nonzero integer.')
            quit()
        else:
            n_answers = int(sys.argv[2])

    solves = predict_analogy(sys.argv[1], n_answers)
    for solve in solves:
        print(solve)
