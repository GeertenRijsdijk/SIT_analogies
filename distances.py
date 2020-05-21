from tools import alphabet, is_symbol

def add_distances_positional(code, lhs, rhs):
    new_code = ''
    counts = {c:0 for c in rhs}
    # For each character in the string ...
    for i, c in enumerate(code):
        is_symb = is_symbol(code, i)
        # If c is a symbol and not already in the lefthandside ...
        if is_symb and c not in lhs:
            # ... find the symbol in lhs at the same position as c in rhs ...
            pos_symbol = lhs[rhs.index(c, counts[c])]
            counts[c] += 1
            # ... calculate the distance from the last symbol
            dist = alphabet.index(c) - alphabet.index(pos_symbol)
            # ... and add c to the code as that distance
            if dist >= 0:
                new_code += '(' + pos_symbol + '+' + str(dist) + ')'
            else:
                new_code += '(' + pos_symbol + '-' + str(abs(dist)) + ')'

        # Otherwise, just add c to the new code
        else:
            new_code += c

    return new_code

'''
Rewrites a code, keeping only symbols in a specified set. Symbols not in the set
are rewritten as distances from the previous new symbol.

Ex: add_distances_symbols('S[(A),(B)]CA', 'AB')
returns: 'S[(A),(B)]($+1)A'
'''
def add_distances_symbols(code, lhs):
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

'''
Rewrites a code, keeping only elements in a specified set (with indices).
These elements can contain multiple symbols.
Symbols that occur in the elements, but are not actually in an element are
replaced as well.

Ex: add_distances_chunks('S[(AB),(C)]A', (['(AB)', '(C)'],[2, 7]))
returns: 'S[(AB),(C)]($-2)'
'''
def add_distances_chunk(code, chunk):
    elems, indices = chunk
    new_string = ''
    symbols = []
    # For each character in the string:
    for i, c in enumerate(code):
        # If it is not a symbol, skip it.
        if not is_symbol(code, i):
            new_string += c
            continue
        # If it is one of the elements in the chunk ...
        in_element = False
        for j in range(len(elems)):
            if indices[j] <= i < indices[j]+len(elems[j]):
                new_string += c
                in_element = True
                # ... add it to the symbols, if it is not in already.
                if c not in symbols:
                    symbols.append(c)

        # If it was added, we don't need to do anything with it anymore.
        if in_element:
            continue

        # At this point, we have encountered a symbol not in the given elements.
        # If there are no previous symbols, we cannot find a distance.
        if symbols == []:
            return False

        # Calculate the distance from the last new symbol ...
        dist = alphabet.index(c) - alphabet.index(symbols[-1])
        new_symb = alphabet[alphabet.index(symbols[-1]) + dist]
        # ... and write the symbol as a distance from this symbol.
        if dist >= 0:
            new_string += '($+' + str(dist) + ')'
        else:
            new_string += '($-' + str(abs(dist)) + ')'
        if new_symb not in symbols:
            symbols.append(new_symb)

    return new_string

'''
Rewrites a code, turning distance operators into new symbols.
r_codes and r_indices can be given to the function to allow it to carry over
structure to places where new symbols are calculated.

Ex: remove_distances('S[(IJ),(K)]($+1)')
Returns: 'S[(IJ),(K)]L'

Ex: remove_distances('S[(I),(3*(K))]($+1)', ['I', '3*(K)'], [3, 7])
Returns: S[(I), (3*(K))] 3*(L)

As 3*(K) is specified in the second argument, indicating that the structure
should be carried over as well, resulting in 3*(L).
'''
def remove_distances(code, r_codes = [], r_indices = []):
    symbols = []
    par_stack = []
    new_code = ''
    # For each character in the code...
    for i, c in enumerate(code):
        # ... add the character to the new code.
        new_code += c
        in_element = -1

        if is_symbol(code, i):
            # Check if symbol c is part of one of the r_codes
            for j in range(len(r_codes)):
                if r_indices[j] <= i < r_indices[j]+len(r_codes[j]):
                    in_element = j
                    if r_codes[j] not in symbols:
                        symbols.append(r_codes[j])

            if in_element < 0 and c not in symbols:
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
                symb, op, dist = part[0], part[1], int(''.join(part[2:]))
                # ... find the code to calculate from ...
                if symb == '$':
                    symb = symbols[-1]
                # ... and get the correct distance.
                if op == '-':
                    dist *= -1
                # If it concerns a single symbol, calculate the distance from it
                if symb.isalnum() and len(symb) == 1:
                    new_symb = alphabet[alphabet.index(symb) + dist]
                # If it concerns a code ...
                else:
                    new_symb = ''
                    # ... add the distance to each symbol in the code.
                    for i, s in enumerate(symb):
                        if is_symbol(symb, i):
                            new_symb += alphabet[alphabet.index(s) + dist]
                        else:
                            new_symb += s

                #  Add the result to the new code.
                new_code += new_symb
                #if new_symb not in symbols:
                symbols.append(new_symb)

    #print('>', code)
    #print('>>', new_code)
    return new_code

if __name__ == '__main__':
    a = add_distances_positional('AAEECCCC', 'AAEE', 'CCCC')
    print(a)
