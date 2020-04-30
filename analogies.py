from compressor_bruteforce import compress
from decompressor import decompress
from complexity_metrics import I_new_load, analogy_load
from tools import alphabet, is_symbol
from symbol_replacement import replace_left_right
import sys

# Given a list of codes, returns the codes with the lowest information load.
def lowest_complexity(codes, metric = 'I_new'):
    lowest_codes = []
    lowest_load = float('inf')
    for code in codes:
        if metric == 'analogy':
            load = analogy_load(code)
        elif metric == 'I_new':
            load = I_new_load(code)
        else:
            print('unknown metric, using I_new')
        if load < lowest_load:
            lowest_codes = [code]
            lowest_load = load
        elif load == lowest_load:
            lowest_codes.append(code)
    return lowest_codes, lowest_load

# Rewrites a code so it only uses symbols from a specified set, using distances.
def add_distances(code, lhs):
    new_code = ''
    symbols = []
    # For each character in the string ...
    for i, c in enumerate(code):
        is_symb = is_symbol(code, i)
        # If c is a symbol and not already in the lefthandside ...
        if is_symb and c not in lhs:
            # ... calculate the distance from the last symbol
            dist = alphabet.index(c) - alphabet.index(symbols[-1])
            # ... and add c to the code as that distance
            if dist >= 0:
                new_code += '($+' + str(dist) + ')'
            else:
                new_code += '($-' + str(abs(dist)) + ')'

        # Otherwise, just add c to the new code
        else:
            new_code += c

        if is_symb and c not in symbols:
            symbols.append(c)

    return new_code

# Removes the distance operators to find the correct symbols.
def remove_distances(code):
    symbols = []
    par_stack = []
    new_code = ''
    # For each character in the code...
    for i, c in enumerate(code):
        # ... add the character to the new code.
        new_code += c
        if is_symbol(code, i) and c not in symbols:
            symbols.append(c)
        if c == '(':
            par_stack.append(i)
        # If we find a part of the code enclosed in parentheses ...
        elif c == ')':
            start = par_stack.pop(-1)
            part = code[start:i+1].strip('()')
            # ... check whether this part contains a +/- operator.
            if ('+' in part or '-' in part) and '(' not in code[start+1:i]:
                # If yes, remove the operation from the code ...
                new_code = new_code[:-(i-start+1)]
                # ... calculate the new symbol ...
                symb, op, dist = part[0], part[1], int(''.join(part[2:]))
                if symb == '$':
                    symb = symbols[-1]
                if op == '+':
                    new_symb = alphabet[alphabet.index(symb) + dist]
                else:
                    new_symb = alphabet[alphabet.index(symb) - dist]
                # ... and add that to the code instead.
                new_code += new_symb
                symbols.append(new_symb)
    return new_code

def find_solves_of_codes(codes, l1, r1):
    solves = []
    for code in codes:
        #print('1:', code)
        new_code = add_distances(code, l1)
        #print('2:', new_code)
        new_codes = replace_left_right(new_code, l1, r1)
        #print('3:', new_code)
        for new_code in new_codes:
            #print(new_code)
            new_code = remove_distances(new_code)
            #print('4:', new_code)
            d = decompress(new_code)

            if d[:len(r1)] == r1:
                complexity = analogy_load(code) + analogy_load(new_code)
                solves.append((d[len(r1):], round(complexity,2), code, new_code))
            #print('>', solves[-1])

    return solves

# Predicts an analogy by finding a structure in the lefthandside of an analogy
# and applying that same structure to the righthandside.
def predict_analogy(string, n_answers = 'all'):
    try:
        l, r = string.split('::')
        l1, l2 = l.split(':')
        r1, r2 = r.split(':')
    except:
        print('Analogy should be of form A:B::C:?')
        quit()

    codes_1, _ = compress(l1+l2)
    solves_1 = find_solves_of_codes(codes_1, l1, r1)
    codes_2, _ = compress(l1+r1)
    solves_2 = find_solves_of_codes(codes_2, l1, l2)
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
