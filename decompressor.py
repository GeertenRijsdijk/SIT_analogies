'''
decompressor.py
Geerten Rijsdijk (11296720)

In this file, a SIT decompressor is implemented.

USAGE: decompress.py <code>
Code with spaces must be put in double quotes.
'''

import re
import sys

# Check wether given code contains at most one operator
def is_basic(s):
    ite = sum(c == '*' for c in s)
    sym = sum(c == '[' for c in s)
    alt = sum(c == '/' for c in s)

    n_operators = ite + sym + alt
    if n_operators > 1:
        return False
    return True

# Decompresses a code with at most one operator
def solve_basic_operation(code):
    # Case: Iteration
    if code[1] == '*':
        n = int(code[0])
        new_code = re.sub('[\d*()]', '', code)
        return new_code * n

    # Case: Symmetry
    elif code[0] == 'S':
        arguments = re.findall("[\w']+", code[1:])
        new_code = ''.join(arguments)
        if ',' in code:
            arguments.pop(-1)
        arguments.reverse()
        new_code += ''.join(arguments)
        return new_code

    # Case: Alternation
    elif code[0] == '<':
        l,r = code.split('/')
        l = re.findall("[\w']+", l)
        r = re.findall("[\w']+", r)
        new_code = ''
        max_len = max(len(l), len(r))
        for i in range(max_len):
            new_code += l[i%len(l)]
            new_code += r[i%len(r)]
        return new_code
    return code

# Returns a list of all operators in a given code
def find_operators(code):
    bracket_stack = []
    alternations = []
    operators = []
    for i, c in enumerate(code):
        if c in ['(', '[', '<']:
            bracket_stack.append((c, i))
        elif c == ')':
            start = bracket_stack.pop(-1)
            if start[1] != 0 and code[start[1]-1] == '*':
                operators.append(code[start[1]-2:i+1])
        elif c == ']':
            start = bracket_stack.pop(-1)
            operators.append(code[start[1]-1:i+1])
        elif c == '>':
            start = bracket_stack.pop(-1)
            alternations.append(code[start[1]:i+1])

    for i in range(0, len(alternations), 2):
        operators.append(alternations[i]+'/'+alternations[i+1])
    return operators

# Decompresses all lowest level operators (i.e. without nested operators)
def decompress_base_layer(code):
    # construct
    operators = find_operators(code)
    decomp_dict = {}
    for op in operators:
        if is_basic(op):
            decomp_dict[op] = solve_basic_operation(op)

    for k, v in decomp_dict.items():
        code = code.replace(k, v)
    return code

# rewrites a code to a version without operators by constantly decompressing
# the hierarchically lowest operators.
def decompress(code):
    code = code.replace(' ', '')
    while not code.isalpha():
        code = decompress_base_layer(code)
    return code

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('USAGE: decompress.py <code>')
        print('Code with spaces must be put in double quotes.')
    elif sys.argv[1]:
        print(decompress(sys.argv[1]))

    # tests = [
    #     '2*(3*(2*(4*(A))))',
    #     'S[(a)(b),(c)]',
    #     'a 2*(S[(2*(b))(a),(c)]) b S[(d)(e)]',
    #     '<<(a)>/<(b) (2*(d))>>/<(b)(c)>',
    # ]
    #
    # for t in tests:
    #     print(t, '=>', decompress(t))
