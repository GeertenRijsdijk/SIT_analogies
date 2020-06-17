from compressor_bruteforce import compress_bf
from decompressor import decompress
from complexity_metrics import I_new_load, analogy_load
from symbol_replacement import replace_left_right
from PISA.encode import encode, get_PISA_codes
from PISA.graphs import Graph
from iterations import solve_with_iterations
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
def find_solves_of_codes(l1, l2, r1, penalty = 0, it = False):
    solves = []
    # Find all codes
    # codes, _ = compress_bf(l1+l2)
    codes = get_PISA_codes(l1+l2, return_loads = True)
    if it:
        code, new_code = solve_with_iterations(l1, l2, r1)
    else:
        code = None

    if code:
        # Decompress the code
        d = decompress(new_code)

        # Add them to the answers, only if the found string starts with r1
        if d[:len(r1)] == r1:
            complexity = analogy_load(code) + analogy_load(new_code) \
                + penalty
            solves.append((d[len(r1):], round(complexity,2), code,new_code))

    for code, load in codes:
        # Replace the symbols in the codes
        new_codes = replace_left_right(code, l1, l2, r1)
        for new_code in new_codes:
            # Decompress the codes
            d = decompress(new_code)

            # Add them to the answers, only if the found string starts with r1
            if d[:len(r1)] == r1:
                complexity = analogy_load(code) + analogy_load(new_code) \
                    + penalty
                solves.append((d[len(r1):], round(complexity,2), code,new_code))

    return solves

'''
Given an analogy, runs the previous function twice to find all possible answers:
An analogy of form A:B::C:? is also run as A:C::B:?

Answers are returned in the same format as the previous function.
'''
def predict_analogy(string, n_answers = 'all', it = False):
    try:
        l, r = string.split('::')
        l1, l2 = l.split(':')
        r1, r2 = r.split(':')
    except:
        print('Analogy should be of form A:B::C:?')
        quit()

    solves_1 = find_solves_of_codes(l1, l2, r1, it = it)
    solves_2 = find_solves_of_codes(l1, r1, l2, penalty = 0, it = it)
    solves = sorted(solves_1 + solves_2, key = lambda x:x[1])
    if n_answers == 'all':
        return solves
    else:
        return solves[:n_answers]

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('USAGE: analogies.py <analogy> <n answers> <use iteration>')
        print('Analogy should be of form A:B::C:?')
        print('Set <n answers> to 0 for all answers.')
        print('<use iteration>: 0 for no (default), 1 for yes')
        quit()
    n_answers = 'all'
    use_iteration = False
    if len(sys.argv) >= 3:
        if (not sys.argv[2].isdigit() or int(sys.argv[2]) < 0):
            print('USAGE: analogies.py <analogy> <n answers> <use iteration>')
            print('<n answers> should be a positive, nonzero integer.')
            quit()
        elif sys.argv[2] != '0':
            n_answers = int(sys.argv[2])
    if len(sys.argv) == 4:
        use_iteration = int(sys.argv[3])
    check_analogy = sys.argv[1].replace(':', '').replace('?', '')
    if not check_analogy.isalpha():
        print('Analogy should contain only letters.')
        quit()
    solves = predict_analogy(sys.argv[1], n_answers, it = use_iteration)
    for solve in solves:
        print(solve)
