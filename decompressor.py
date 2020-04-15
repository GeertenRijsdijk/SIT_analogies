'''
decompressor.py
Geerten Rijsdijk (11296720)

In this file, a SIT decompressor is implemented.

USAGE: decompressor.py <code>
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

# 'quick and dirty' way of getting arguments. Not proud of this one.
def get_arguments(code):
    code = re.sub("[^a-zA-Z()]", '', code)
    stack = []
    arguments = []
    for i, c in enumerate(code):
        if c == '(':
            stack.append(i)
        elif c == ')':
            i_start = stack.pop(-1)
            if stack == []:
                arguments.append(code[i_start+1:i])
    return arguments

# Decompresses a code with at most one operator
def solve_basic_operation(code):
    # Case: Iteration
    if code[1] == '*':
        n = int(code[0])
        new_code = code[3:-1]
        return new_code * n

    # Case: Symmetry
    elif code[0] == 'S':
        arguments = get_arguments(code[1:])
        new_code = ''.join(arguments)
        if ',' in code:
            arguments.pop(-1)
        arguments.reverse()
        new_code += ''.join(arguments)
        return new_code

    # Case: Alternation
    elif code[0] == '<':
        l,r = code.split('/')
        l = get_arguments(l)
        r = get_arguments(r)
        new_code = ''
        max_len = max(len(l), len(r))
        for i in range(max_len):
            new_code += l[i%len(l)]
            new_code += r[i%len(r)]
        return new_code
    return code

# Returns a list of all operators in a given code
def find_operators(code):
    # Stack of the locations of the <, (, [
    bracket_stack = []
    # List of operators.
    operators = []
    # Alternations are separate because they consist of 2 parts
    alternation_stack = []

    for i, c in enumerate(code):
        # (possible) start of operator, add to stack
        if c in ['(', '[', '<']:
            bracket_stack.append((c, i))
        # Add iterations to the operators list
        elif c == ')':
            start = bracket_stack.pop(-1)
            if start[1] != 0 and code[start[1]-1] == '*':
                operators.append(code[start[1]-2:i+1])
        # Add symmetries to the operators list
        elif c == ']':
            start = bracket_stack.pop(-1)
            operators.append(code[start[1]-1:i+1])
        # Add parts of alternations to the alternations list
        elif c == '>':
            start = bracket_stack.pop(-1)
            if i == len(code) - 1 or code[i+1] != '/':
                left = alternation_stack.pop(-1)
                right = code[start[1]:i+1]
                operators.append(left+'/'+right)
            else:
                alternation_stack.append(code[start[1]:i+1])

    return operators

# Decompresses all lowest level operators (i.e. without nested operators)
def decompress_base_layer(code):
    operators = find_operators(code)
    # Build a dictionary of all the operators and their decompression
    decomp_dict = {}
    for op in operators:
        if is_basic(op):
            decomp_dict[op] = solve_basic_operation(op)

    # Replace the operators by their decompression
    for k, v in decomp_dict.items():
        code = code.replace(k, v)
    return code

# rewrites a code to a version without operators by constantly decompressing
# the hierarchically lowest operators.
def decompress(code):
    code = code.replace(' ', '')
    while ('*' in code or '[' in code or"/" in code):
        code = decompress_base_layer(code)
    return code

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('USAGE: decompressor.py <code>')
        print('Code with spaces must be put in double quotes.')
    elif sys.argv[1]:
        print(decompress(sys.argv[1]))
