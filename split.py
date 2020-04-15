'''
split.py
Geerten Rijsdijk (11296720)

Returns every way a string can be split into substrings,
or every way a list of strings can be combined into substrings.

EX: 'abc'           =>  [['a', 'b', 'c'], ['a', 'bc'], ['ab, 'c'], ['abc']]
EX: ['a', 'b', 'c'] =>  [['a', 'b', 'c'], ['a', 'bc'], ['ab, 'c'], ['abc']]
'''

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
