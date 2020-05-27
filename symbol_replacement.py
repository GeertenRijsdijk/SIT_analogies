from tools import is_symbol
from copy import copy
from distances import add_distances_chunk, add_distances_symbols, \
    add_distances_positional, remove_distances
from PISA.encode import encode, get_PISA_codes
from PISA.graphs import Graph
from complexity_metrics import analogy_load

'''
Finds all the ways the elements in l1 occur in a given string, with indices
They may be separated by operators, spread accross arguments...

Ex: get_chunks('S[(ab)(c),(d)]', 'abc')
returns: [ ( [(ab), (c)], [2, 6] ) ]

indicating that the string 'abc' occurs in the string as the elements
(ab) and (c) at positions 2 and 6, respectively.
'''
def get_chunks(string, l1):
    par_stack = []
    elements = []
    elem_indices = []
    # For each character in the string:
    for i, c in enumerate(string):
        # If it is an opening parenthesis, add it to the stack.
        if c == '(':
            par_stack.append(i)
        # If it is a closing parenthesis ...
        if c == ')':
            # ... get the corresponding parenthesis from the stack ...
            start = par_stack.pop(-1)
            # ... and find the substring the parentheses enclose (elem).
            elem = string[start:i+1]
            elem_len = len(elem.strip('()'))
            # if elem is already in the elements list ...
            if elements != [] and '('+''.join(elements[-elem_len:])+')' == elem:
                # ... remove those elements from the elements list.
                elements = elements[:-elem_len]
                elem_indices = elem_indices[:-elem_len]
            # if elem contains only symbols ...
            if elem.strip('()').isalnum():
                # ... add it to the elements list.
                elements.append(elem)
                elem_indices.append(start)

        # If it is a symbol, add it to the elements list.
        if is_symbol(string, i):
            elements.append(c)
            elem_indices.append(i)

    chunks = []
    symb_string = ''
    # For each sequential combination of elements ...
    for i in range(len(elements)):
        for j in range(i, len(elements)):
            # ... create a string of all symbols in those elements.
            symb_string = ''
            for e in elements[i:j+1]:
                symb = e.strip('()')
                for s in symb:
                    if s not in '+-':
                        symb_string += s
                    else:
                        break
            # If this string corresponds to l1 ...
            if symb_string == l1:
                # ... we have found a chunk.
                chunks.append((elements[i:j+1], elem_indices[i:j+1]))

    return chunks

'''
Splits a code on its highest level operations and symbols.

Ex: split_code('<(a)>/<2*((b)>dS[(a)(b)]')
Returns: ['<(a)>/<2*((b)>', 'd', 'S[(a)(b)]']
'''
def split_code(code):
    stack = []
    alternations = []
    elements = []
    # For each character in the code:
    for i in range(len(code)):
        # If it is a symbol not in an operator, add it to the elements.
        if is_symbol(code, i) and len(stack) == 0:
            elements.append(code[i])
        # If it is an opening bracket, add it to the stack
        elif code[i] in '<([':
            stack.append(i)
        # If it is a closing bracket ...
        elif code[i] in '>])':
            start = stack.pop(-1)
            # ... and the stack is not empty, it is a lower level operator.
            if len(stack) != 0:
                continue
            # Iteration, Symmetry and Alternation have different cases.
            if start > 1 and code[start-1] == '*':
                elements.append(code[start-2:i+1])
            if code[i] == ']' and start > 0 and code[start-1] == 'S':
                elements.append(code[start-1:i+1])
            elif code[i] == '>':
                if start > 0 and code[start-1] == '/':
                    lhs = alternations.pop(-1)
                    elements.append(lhs + code[start-1:i+1])
                else:
                    alternations.append(code[start:i+1])

    return elements

'''
Given a string, elements in the string and new elements, replaces the elements
in the string with the new ones.

Also returns the starting indices of the new elements.

Ex: reconstruct_string('S[(a),(b)]', ([(a), (b)],[2, 6]), [(cd), (e)])
Returns: 'S[(cd),(e)]' , [2,7]
'''
def reconstruct_string(string, chunk, new_elems):
    elems, indices = chunk
    r_indices = []
    new_string = ''
    elem_end = 0
    # For each index in the chunk:
    for i, ind in enumerate(indices):
        # Add the parts not in the chunks
        new_string += string[elem_end:ind]
        elem_end = ind+len(elems[i])

        # Find the number of opening parentheses, for the return index
        n_pars = 0
        for c in new_elems[i]:
            if c == '(':
                n_pars += 1
            else:
                break
        # Find the return index and add it to the list
        r_indices.append(len(new_string)+n_pars)

        # Add the replacing element to the new string
        new_string += new_elems[i]

    # Add everything after the last element to the new string
    new_string += string[elem_end:]
    return new_string, r_indices

'''
Replaces symbols in a string that occur in l1 with symbols that occur in r1.
Also returns a list of all new symbols and their indices in the new string.

Ex: replace_symbols(<(a)>/<(b)(c)(a)>, 'abc', 'ijk')
Returns <(i)>/<(j)(k)(i)>, ['i', 'j', 'k', 'i'], [2, 8, 11, 14]
'''
def replace_symbols(string, l1, r1):
    new_string = ''
    symbols = []
    r_indices = []
    r_elems = []
    # For each element in the string:
    for i, c in enumerate(string):
        # If it is a symbol and occurs in l1 ...
        if is_symbol(string, i) and c in l1:
            n = symbols.count(c)%l1.count(c)
            # ... find the corresponding symbol in r1 ...
            new_symbol = r1[l1.index(c, n)%len(r1)]

            r_indices.append(len(new_string))
            r_elems.append(new_symbol)
            # ... and add it to the new string.
            new_string += new_symbol
            symbols.append(c)
        # Otherwise, just add it to the string.
        else:
            new_string += c
    return new_string, r_elems, r_indices

'''
In a string, replaces the symbols in the chunk with symbols in r1, and places
the chunk back in the string.

Also returns the starting indices of the new elements.

Ex: replace_chunks('S[(a)(bc)]($+1)', (['(a)', '(bc)'],[2, 5]), ['i', '2*(j)']):
Returns: 'S[(i)(2*(j))]($+1)', [4, 7]
'''
def replace_chunks(string, chunk, r1):
    elems, _ = chunk
    elems2 = copy(elems)
    # For each element:
    for i, elem in enumerate(elems):
        # Remove all outer parentheses, ....
        elem_stripped = elem.strip('()')
        dist = ''
        # ... find the part of the string before any + or - ...
        if '+' in elem_stripped:
            dist_ind = elem_stripped.index('+')
            dist += elem_stripped[dist_ind:]
        if '-' in elem_stripped:
            dist_ind = elem_stripped.index('-')
            dist += elem_stripped[dist_ind:]
        # ... and replace that part with a new part, given in r1 ...
        new_r = ''
        for j, c in enumerate(r1[i]):
            # ... while carrying over any distance operator.
            if is_symbol(r1[i], j) and dist != '':
                new_r += '(' + c + dist + ')'
            else:
                new_r += c
        elems2[i] = elems2[i].replace(elem_stripped, new_r)

    # Now reconstruct the string and return it.
    return reconstruct_string(string, chunk, elems2)

'''
Given a string, a chunk and the symbols in that chunk (l1), finds whether
the elements of that chunk occur in such a way that more elements can be added
while preserving the structure. (This is what is referred to as a sequential
chunk, name pending). If so, it replaces the elements with elementsin r1.

Ex: replace_sequential_chunk('S[(a)(b)(c)]($+1)', \
    (['(a)', '(b)', '(c)'],[2, 5, 8]), 'abc', 'ijkl'):
Returns: 'S[(i)(j)(k)(l)]($+1)'

Where (a)(b)(c) becomes (i)(j)(k)(l). This is possible because these all
occur within one symmetry.
'''
def replace_sequential_chunk(string, chunk, l1, r1):
    elems, indices = chunk
    # First, test whether the chunk is a sequential chunk. If so, it should ...
    # ... have the same number of elements as l1 ...
    if len(elems) != len(l1):
        return []
    # ... one length for all of its elements ...
    if len(set([len(e) for e in elems])) != 1:
        return[]

    # ... become l1 when stripped of the paretheses and pasted together ...
    stripped_string = ''.join(elems).replace('(', '').replace(')', '')
    if stripped_string != l1:
        return []

    # ... occur in the string without any brackets/operators between the
    # elements. A Comma is allowed.
    start = indices[0]
    end = indices[-1] + len(elems[-1])
    if string[start:end].replace(',' , '') != ''.join(elems):
        return []

    # At this point, a sequential chunk has been found.
    n_pars = elems[0].count('(')
    new_elems = [n_pars * '(' + r + n_pars*')' for r in r1]
    # Construct the new elements from r1
    if ',' in string[start:end]:
        new_elems = new_elems[:-1] + [','] + new_elems[-1:]
    return string[:start] + ''.join(new_elems) + string[end:]

'''
Replaces a part in a string with different symbols. This can be done in
different ways, depending on how l1 and r1 correspond, and how l1 is found
in the given string.

Ex: replace_left_right(S[(a)(b)(c)], 'abc', 'defg')
returns ['S[(d)(e)(f)(g)]'']
'''
def replace_left_right(string, l1, l2, r1):
    replacements = []
    rep_chunks = get_chunks(string, l1)
    rcodes = get_PISA_codes(r1)
    rsplits = [split_code(c) for c in rcodes]

    # If l1 and l2 have the same length, positional distances are possible
    if len(l1) == len(l2) and len(l1) == len(r1):
        dist_string = add_distances_positional(string, l1, l2)
        code, _, _ = replace_symbols(dist_string, l1, list(r1))
        replacements.append(remove_distances(code))

    dist_string = add_distances_symbols(string, l1)

    # If l1 and r1 have the same length
    if len(l1) == len(r1):
        code, _, _ = replace_symbols(dist_string, l1, list(r1))
        replacements.append(remove_distances(code))

    # If r1 is larger than l1 ...
    if len(l1) < len(r1):
        # ... try replacing l1 with compressed codes of r1.
        for rs in rsplits:
            if len(rs) == len(l1):
                code, r_elems, r_inds = replace_symbols(dist_string, l1, rs)
                replacements.append(remove_distances(code, r_elems, r_inds))

    # For every way l1 occurs in string:
    for chunk in rep_chunks:
        new_string = add_distances_chunk(string, chunk)
        if not new_string:
            continue
        rep_seq = replace_sequential_chunk(new_string, chunk, l1, r1)
        replacements.append(remove_distances(rep_seq))

        # Try to match r1 to the chunk, and replace
        matched_r1 = match_elements(chunk, r1)
        if matched_r1 and len(matched_r1) == len(chunk[0]):
            rep, r_inds = replace_chunks(new_string, chunk, matched_r1)
            replacements.append(remove_distances(rep))

        # If the chunk is smaller than r1
        if len(chunk[0]) < len(r1):
            for rs in rsplits:
                if len(rs) == len(chunk[0]):
                    rep, r_inds = replace_chunks(new_string, chunk, rs)
                    replacements.append(remove_distances(rep, rs, r_inds))

    return list(set(replacements))

def match_elements(chunk, r1):
    elems, _ = chunk
    lengths = [len(e.strip('()')) for e in elems]
    max_len = max(lengths)
    ind = lengths.index(max_len)
    lengths[ind] = max_len - sum(lengths) + len(r1)
    for l in lengths:
        if l <= 0:
            return None

    splits = []
    start = 0
    for length in lengths:
        splits.append(r1[start:start + length])
        start += length
    return splits
