from tools import alphabet
from decompressor import decompress
from PISA.encode import get_PISA_codes
from distances import add_distances_symbols, remove_distances

'''
Finds all iterations in a string.
input:
    - a string
returns:
    - a list of iteration operators representing the string
    - a list of only the parameters of these operators
    - a list of only the symbols in these operators
Example: find_iterations('AABBBCBBB')
Returns:
    - ['2*(A)', '3*(B)', '1*(C)', '3*(B)']
    - [2,3,1,3]
    - ['A', 'B', 'C', 'B']
'''
def find_iterations(string):
    count = 0
    last_symb = ''
    iters = []
    pars = []
    symbols = []
    for i, c in enumerate(string):
        if last_symb != c and count > 0:
            if count == 1:
                iter = last_symb
            else:
                iter = str(count) + '*(' + last_symb + ')'
            iters.append(iter)
            pars.append(count)
            symbols.append(last_symb)
            count = 1
        else:
            count += 1
        last_symb = c

    if count == 1:
        iter = last_symb
    else:
        iter = str(count) + '*(' + last_symb + ')'
    iters.append(iter)
    pars.append(count)
    symbols.append(last_symb)
    return iters, pars, symbols

'''
Finds the code best representing the structure of the iteration parameters in
a string.
input:
    - a string
returns, in addition to the lists of the previous function:
    - a simplest code for the parameters of the operators
Example: find_it_structure('AABBBCBBB')
Returns:
    - ['2*(A)', '3*(B)', '1*(C)', '3*(B)']
    - [2,3,1,3]
    - ['A', 'B', 'C', 'B']
    - '{2} S[ ({3}), ({1}) ]'
'''
def find_it_structure(string):
    iters, pars, symbols = find_iterations(string)
    str_pars = ['{' + str(p) + '}' for p in pars]
    codes = get_PISA_codes(str_pars, True)
    lowest = min(codes, key = lambda x: x[1])
    lowest_code = lowest[0]
    return iters, pars, symbols, lowest_code

'''
Given a code, finds all parameters in the code
Ex. get_pars( {2} S[ ({3}), ({1}) )
Returns:
    - [2, 3, 1]
'''
def get_pars(string):
    pars = []
    last_bracket = -1
    for i, c in enumerate(string):
        if c == '{':
            last_bracket = i
        elif c == '}':
            pars.append(string[last_bracket + 1:i])
    return pars

'''
Given a code, replaces all parameters in l1 with ones in r1
Ex. replace_it_structure( '{2} S[ ({3}), ({1})', [2,3,1], [4,5,6] )
Returns:
    - '{4} S[ ({5}), ({6})'
'''
def replace_it_structure(string, l1, r1):
    for i, l in enumerate(l1):
        string = string.replace('{' + l, '{|' + str(i) + '|')
        string = string.replace('(' + l, '(|' + str(i) + '|')
    for i, r in enumerate(r1):
        string = string.replace('{|' + str(i) + '|', '{' + r)
        string = string.replace('(|' + str(i) + '|', '(' + r)
    return string
'''
Adds new iterations to list it_r1 to give it the same number of iterations as
the full code. New iterations have their symbols defined as distances from the
previous symbol.

Ex:
Input:
    - sym_l: ['A', 'B', 'A', 'B']
    - sym_r1: ['E', 'F']
    - it_r1: ['4*(E)', 'F']
    - rep_pars: ['4', '1', '1', '4']
Returns:
    - it_r1: ['4*(E)', 'F', '1*(($-1))', '4*(($+1))']
'''
def add_new_iterations(sym_l, sym_r1, it_r1, rep_pars):
    for i in range(len(sym_r1), len(sym_l)):
        dist = alphabet.index(sym_l[i]) - alphabet.index(sym_l[i-1])

        ind = None
        if sym_l[i] in sym_l[:i]:
            ind = sym_l[:i].index(sym_l[i])

        new_it = str(rep_pars[i]) + '*('
        if ind != None and ind < len(sym_r1):
            new_it += sym_r1[ind] + ')'
        else:
            new_it += '($'
            if dist >= 0:
                new_it += '+' + str(dist) + '))'
            else:
                new_it += '-' + str(abs(dist)) + '))'

        it_r1.append(new_it)

    print(it_r1)
    return it_r1

'''
Attempts to solve an analogy by finding structure in the iterations that can
represent the analogy.

Example: solve_with_iterations('AAAB', 'ABBB', 'EEEEF')
Returns:
    - ('3*(A)BA3*(B)', '4*(E)FE4*(F)')
The latter of which is the result code, which can be decompressed to
EEEEFEFFFF. Subtracting EEEEF leads to the answer EFFFF.
'''
def solve_with_iterations(l1, l2, r1):
    _, _, sym_l1, struct_l1 = find_it_structure(l1)
    iters_orig, _, sym_l, struct_l = find_it_structure(l1 + l2)
    it_r1, pars_r1, sym_r1, struct_r1 = find_it_structure(r1)

    pars_l1 = get_pars(struct_l1)
    pars_r1 = get_pars(struct_r1)

    if len(pars_l1) != len(pars_r1):
        return None, None

    struct_l = add_distances_symbols(struct_l, pars_l1, False)

    pars_l = get_pars(struct_l)
    full_code = replace_it_structure(struct_l, pars_l1, pars_r1)
    full_code = remove_distances(full_code)

    full_code = decompress(full_code)
    rep_pars = get_pars(full_code)

    it_r1 = add_new_iterations(sym_l, sym_r1, it_r1, rep_pars)

    for n in rep_pars:
        replaced = False
        for it in it_r1:
            if it.startswith(n):
                if n == '1':
                    rep = it[3:-1]
                else:
                    rep = it
                full_code = full_code.replace('{' + n + '}', rep, 1)
                replaced = True
            elif n == '1' and it[0].isalpha():
                full_code = full_code.replace('{' + n + '}', it, 1)
                replaced = True

    full_code = remove_distances(full_code)
    return ''.join(iters_orig), full_code

if __name__ == '__main__':
    a = solve_with_iterations('ABBA', 'BBABB', 'CCCDCCC')
    print(a)

# def add_new_iterations(sym_l, sym_r1, it_r1, rep_pars):
#     for i in range(len(sym_r1), len(sym_l)):
#         dist = alphabet.index(sym_l[i]) - alphabet.index(sym_l[i-1])
#
#         ind = None
#         if sym_l[i] in sym_l[:i]:
#             ind = sym_l[:i].index(sym_l[i])
#
#         if ind != None and ind < len(sym_r1):
#             it_r1.append(sym_r1[ind])
#         else:
#             new_it = str(rep_pars[i]) + '*(($'
#             if dist >= 0:
#                 new_it += '+' + str(dist) + '))'
#             else:
#                 new_it += '-' + str(abs(dist)) + '))'
#
#             it_r1.append(new_it)
#     print(it_r1)
#     return it_r1
