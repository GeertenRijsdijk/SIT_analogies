from compressor_bruteforce import compress
from decompressor import decompress
from complexity_metrics import I_new_load
from tools import alphabet
import sys

# Given a list of codes, returns the codes with the lowest information load.
def lowest_complexity(codes):
    lowest_codes = []
    lowest_load = float('inf')
    for c in codes:
        load = I_new_load(c)
        if load < lowest_load:
            lowest_codes = [c]
            lowest_load = load
        elif load == lowest_load:
            lowest_codes.append(c)
    return lowest_codes, lowest_load

# Rewrites a code so it only uses symbols from a specified set, using distances.
def add_distances(code, lhs):
    new_code = ''
    # For each character in the string ...
    for i, c in enumerate(code):
        # ... check whether the character c is a symbol.
        symbol = False
        if c.isalpha() and c != 'S':
            symbol = True
        elif c == 'S' and (i == len(code) - 1 or code[i+1] != '['):
            symbol = True

        # If c is a symbol and not already in the lefthandside ...
        if symbol and c not in lhs:
            # ... find the symbol in the lhs that is closest to c ...
            min_symb, min_dist = ('', float('inf'))
            for s in lhs:
                dist = alphabet.index(c) - alphabet.index(s)
                if abs(dist) < min_dist:
                    min_dist = dist
                    min_symb = s
            # ... and add c to the code as a distance from that symbol.
            if dist >= 0:
                new_code += min_symb + '+' + str(min_dist)
            else:
                new_code += min_symb + '-' + str(abs(min_dist))

        # Otherwise, just add c to the new code
        else:
            new_code += c

    return new_code

# Replaces all symbols in a code with different symbols symbols.
def replace_symbols(code, l1, r1):
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
    # Create a dictionary of replacements, eg a+1:b
    replacements = {}
    for i in range(1, len(code)-1):
        if code[i] in ['+', '-']:
            snippet = code[i-1:i+2]
            if code[i] == '+':
                rep = alphabet[alphabet.index(snippet[0]) + int(snippet[2])]
            else:
                rep = alphabet[alphabet.index(snippet[0]) - int(snippet[2])]
            replacements[snippet] = rep
    # Replace the operators with the calculated symbols
    for orig, rep in replacements.items():
        code = code.replace(orig, rep)
    return code

# Predicts an analogy by finding a structure in the lefthandside of an analogy
# and applying that same structure to the righthandside.
def predict_analogy(string):
    l, r = string.split('::')
    l1, l2 = l.split(':')
    r1, r2 = r.split(':')

    c, _ = compress(l1+l2)
    codes, load = lowest_complexity(c)

    print(string)
    code = codes[0]
    print(code)
    code = add_distances(code, l1)
    print(code)
    code = replace_symbols(code, l1, r1)
    print(code)
    code = remove_distances(code)
    print(code)
    d = decompress(code)

    print(l1 + ':' + l2 + '::' + r1 + ':' + d[len(r1):])

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('USAGE: analogies.py <analogy>')
        print('Analogy should be of form A:B::C:?')
    else:
        predict_analogy(sys.argv[1])
