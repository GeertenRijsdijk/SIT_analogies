'''
tools.py
Geerten Rijsdijk (11296720)

A variety of helper functions used in multiple algorithms
'''

# Alphabet class for dealing with multiple alphabets
class Alphabet():
    def __init__(self):
        self.lower = 'abcdefghijklmnopqrstuvwxyz'
        self.upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.numbers = '1234567890'
        self.alphabets = [self.lower, self.upper, self.numbers]
        self.last_accessed = 0

    def index(self, c):
        for i, a in enumerate(self.alphabets):
            if c in a:
                self.last_accessed = i
                return a.index(c)

    def add(self, c, n):
        for i, a in enumerate(self.alphabets):
            if c in a:
                self.last_accessed = i
                return a[(a.index(c) + n)%len(a)]

    def __getitem__(self, i):
        l = len(self)
        return self.alphabets[self.last_accessed][i%l]

    def __len__(self):
        return len(self.alphabets[self.last_accessed])

    def __iter__(self):
        return iter(self.alphabets[self.last_accessed])

alphabet = Alphabet()


# Check whether the ith character of a string is a symbol
# (and not part of an operator)
def is_symbol(code, i):
    c = code[i]
    # Not alphanumeric
    if not c.isalnum():
        return False
    if i > 0 and code[i-1] == '!':
        return False

    # Iteration
    if i != len(code)-1 and code[i+1] == '*':
        return False
    # Symmetry
    if c == 'S' and not (i == len(code) - 1 or code[i+1] != '['):
        return False
    # Distance
    for j in range(0, i):
        if code[i-j] in '+-':
            return False
        elif not code[i-j].isdigit():
            break
    return True

'''
Returns every way a string can be split into substrings,
or every way a list of strings can be combined into substrings.

EX: 'abc'           =>  [['a', 'b', 'c'], ['a', 'bc'], ['ab, 'c'], ['abc']]
EX: ['a', 'b', 'c'] =>  [['a', 'b', 'c'], ['a', 'bc'], ['ab, 'c'], ['abc']]
'''

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

def create_splits(chars):
    all_splits = []

    # Represent all possible splits as the binary numbers 1 - 2^(n-1)
    n = 2**(len(chars)-1)
    for i in range(0, n):
        # Create the binary number corresponding to i, add leading zeros
        config = format(i, 'b')
        config = '0'* (len(chars) - len(config) - 1) + config

        # Create split from the binary number, split on 1's
        last_i = 0
        split = []
        for i, n in enumerate(config):
            if n == '1':
                if isinstance(chars, str):
                    split.append(chars[last_i:i+1])
                else:
                    split.append(''.join(chars[last_i:i+1]))
                last_i = i+1
        if isinstance(chars, str):
            split.append(chars[last_i:])
        else:
            split.append(''.join(chars[last_i:]))

        # Add to all splits
        all_splits.append(split)
    return all_splits

# Turns a part of a list of substrings into an iteration
def build_iteration(split, i, j):
    new_elem = str(j - i) + '*(' + split[i] + ')'
    return split[:i] + [new_elem] + split[j:]

# Turns a part of a list of substrings into an symmetry
def build_symmetry(split, i, j, pivot, elems):
    new_elem = 'S['
    for arg in elems:
        new_elem += arg
    if (j-i)%2 == 1:
        new_elem += ','
        new_elem += '(' + split[i+pivot] + ')'
    new_elem += ']'
    return split[:i] + [new_elem] + split[j:]

# Turns a part of a list of substrings into an alternation
def build_alternation(split, i, j, offset, elems):
    repeat = '<(' + split[i+offset] + ')>'
    A_chunk = '<' + ''.join(elems) + '>'
    if offset == 0:
        new_elem = repeat + '/' + A_chunk
    else:
        new_elem = A_chunk + '/' + repeat
    return split[:i] + [new_elem] + split[j:]

def build_sequence(split, i, j, dist):
    new_elem = '{(' + split[i] + '),' + str(j-i) +',' + str(dist) + '}'
    return split[:i] + [new_elem] + split[j:]
