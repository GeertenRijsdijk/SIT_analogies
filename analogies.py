from compressor_bruteforce import compress
from decompressor import decompress
from complexity_metrics import I_new_load, analogy_load
from tools import alphabet, is_symbol
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

def rank_answers(l1, l2, r1, answers):
    pass

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

# Find and replace one chunk in a code with another one
def replace_chunks(code, l1, r1):
    if l1 in code:
        return code.replace(l1, r1)

    par_stack = []
    args = []
    indices = []
    # Create a list of all operator arguments and single symbols
    # And a separate list for their indices
    for i, c in enumerate(code):
        if c == '(':
            par_stack.append(i)
        elif c == ')':
            start = par_stack.pop(-1)
            arg = code[start:i+1]
            if len(args) > 0 and '(' + args[-1] + ')' == arg:
                args.pop(-1)
                indices.pop(-1)
            if arg.strip('()').isalnum() and len(arg.strip('()')) == 1:
                args.append(code[start:i+1])
                indices.append(start)
        elif c in '*[]{}<>/+-':
            args.append('-')
            indices.append(i)

    # Create a string of all symbols in the code
    symb_string = ''.join(args)
    symb_string = symb_string.replace('(', '').replace(')', '')

    # Search for the chunk in the symbols
    new_code = code
    for i in range(len(symb_string) - len(l1)+1):
        substring = symb_string[i:i+len(l1)]
        if l1 != substring:
            continue
        lengths = [len(args[j]) for j in range(i,i+len(l1))]
        if len(set(lengths)) != 1:
            continue
        # When the chunk is found ...
        # ... find the start/end points of the chunk in the original code.
        s, e = indices[i], indices[i+len(l1)-1]+len(args[i+len(l1)-1])
        n_pars = args[i].count('(')
        # Create a new code with the specified new chunk ...
        rep_list = [n_pars*'(' + r + n_pars * ')' for r in r1]
        if ',' in code[s:e]:
            rep_list = rep_list[:-1] + [','] + rep_list[-1:]
        rep_code = ''.join(rep_list)
        # ... and replace the old chunk with the new chunk.
        new_code = new_code.replace(code[s:e], rep_code)
    return new_code

# Replaces all symbols in a code with different symbols symbols.
def replace_symbols(code, l1, r1):

    # Replace full chunks
    chunk_code = replace_chunks(code, l1, r1)
    if chunk_code != code:
        return chunk_code

    # Create a dictionary of corresponding symbols
    correspondences = {}
    for i, symbol in enumerate(l1):
        if i < len(r1):
            correspondences[i] = (symbol, r1[i])

    # Replace the symbols with their replacements
    for n, (orig, _) in correspondences.items():
        code = code.replace(orig, '{'+str(n)+'}')
    for n, (_, rep) in correspondences.items():
        code = code.replace('{'+str(n)+'}', rep)
    return code

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
        new_code = replace_symbols(new_code, l1, r1)
        #print('3:', new_code)
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
def predict_analogy(string):
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
    return solves[:10]

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('USAGE: analogies.py <analogy>')
        print('Analogy should be of form A:B::C:?')
    else:
        solves = predict_analogy(sys.argv[1])
        for solve in solves:
            print(solve)
