from compressor_bruteforce import compress
from decompressor import decompress
from complexity_metrics import I_new_load
from tools import alphabet

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

def add_distances(code, symbols_orig):
    new_code = ''
    symbols = []
    for i, c in enumerate(code):
        # Check whether something is is a symbol
        symbol = False
        if c.isalpha() and c != 'S':
            symbol = True
        elif c == 'S' and (i == len(code) - 1 or code[i+1] != '['):
            symbol = True
        if symbol:
            if c not in symbols_orig and len(symbols) > 0:
                dist = alphabet.index(c) - alphabet.index(symbols[-1][0])
                if dist >= 0:
                    new_code += symbols[-1][0] + '+' + str(dist)
                else:
                    new_code += symbols[-1][0] + '-' + str(abs(dist))
            else:
                symbols.append(c)
                new_code += c
        else:
            new_code += c
    return new_code

def replace_symbols(code, l1, r1):
    correspondences = {}
    for i, symbol in enumerate(l1):
        if i < len(r1):
            correspondences[i] = (symbol, r1[i])

    for n, (orig, _) in correspondences.items():
        code = code.replace(orig, '{'+str(n)+'}')
    for n, (_, rep) in correspondences.items():
        code = code.replace('{'+str(n)+'}', rep)
    return code

def remove_distances(code):
    replacements = {}
    for i in range(1, len(code)-1):
        if code[i] in ['+', '-']:
            snippet = code[i-1:i+2]
            if code[i] == '+':
                rep = alphabet[alphabet.index(snippet[0]) + int(snippet[2])]
            else:
                rep = alphabet[alphabet.index(snippet[0]) - int(snippet[2])]
            replacements[snippet] = rep
    for orig, rep in replacements.items():
        code = code.replace(orig, rep)
    return code

def predict_analogy(string):
    l, r = string.split('::')
    l1, l2 = l.split(':')
    r1, r2 = r.split(':')

    c, _ = compress(l1+l2)
    codes, load = lowest_complexity(c)

    code = codes[0]
    code = add_distances(code, l1)
    code = replace_symbols(code, l1, r1)
    code = remove_distances(code)
    d = decompress(code)

    print(string)
    print(l1 + ':' + l2 + '::' + r1 + ':' + d[len(r1):])

if __name__ == '__main__':
    predict_analogy('ACAD:BCBD::DFDG:?')

    # for n, (orig, _) in correspondences.items():
    #     code = code.replace(orig, '{'+str(n)+'}')
    # for n, (_, rep) in correspondences.items():
    #     code = code.replace('{'+str(n)+'}', rep)

    # correspondences = {}
    # for i, symbol in enumerate(l1):
    #     if i < len(r1):
    #         correspondences[i] = (symbol, r1[i])
