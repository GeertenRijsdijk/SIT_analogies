import sys
from complexity_metrics import I_new_load
from tools import build_iteration, build_symmetry, build_alternation, create_splits

# Finds all possible operations in a given list of substrings
def compress_split(split):
    new_codes = []

    # Create iterations
    for i in range(len(split)-1):
        for j in range(i+2, len(split)+1):
            if len(set(split[i:j])) == 1:
              new_codes.append(build_iteration(split, i, j))

    # Create symmetries
    for i in range(len(split)-2):
        for j in range(i+3, len(split)+1):
            pivot = int((j-i)/2)
            if split[i:i+pivot] == split[j-pivot:j][:: -1] and \
                split[i+pivot] == split[j-pivot-1]:

                # Create all possible codes for the S-argument
                argument_split = \
                     ['('+ a +')' for a in split[i:i+pivot]]
                _, splits = compress_bf(argument_split)
                for s in splits:
                    new_codes.append(build_symmetry(\
                        split, i, j, pivot, elems = s))

    # Create alternations
    for i in range(len(split)-3):
        for j in range(i+4, len(split)+1):
            # Alternations result in an even number of elements
            if len(split[i:j])%2 != 0:
                continue

            # Check whether the even/odd elements of the list are the same
            offsets = []
            if len(set(split[i:j][::2])) == 1:
                offsets.append(0)
            if len(set(split[i:j][1::2])) == 1:
                offsets.append(1)

            for offset in offsets:
                # Create all possible codes for the A-argument
                argument_split = \
                    ['('+ a +')' for a in split[i:j][1-offset::2]]
                _, splits = compress_bf(argument_split)
                for s in splits:
                    new_codes.append(build_alternation(\
                        split, i, j, offset, elems = s))

    return new_codes

# Create a compression of a string
def compress_bf(characters):
    # Get all possible ways to split a string into substrings
    splits = create_splits(characters)

    # Keep track of the processed splits and resulting codes
    all_splits = []
    all_codes = []

    while splits != []:
        s = splits.pop(0)
        if s in all_splits:
            continue
        all_splits.append(s)
        if ''.join(s) not in all_codes:
            all_codes.append(''.join(s))

        # Create new code with compressed elements, add to splits
        new_codes = compress_split(s)
        splits += new_codes
    return all_codes, all_splits

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('USAGE: compressor_bruteforce.py <code>')
    elif not sys.argv[1].isalpha():
        print('Code must contain only letters!')
    else:
        lowest_codes = []
        lowest_load = float('inf')
        for c in compress_bf(sys.argv[1])[0]:
            load = I_new_load(c)
            if load < lowest_load:
                lowest_codes = [c]
                lowest_load = load
            elif load == lowest_load:
                lowest_codes.append(c)

        print('CODES WITH LOWEST LOAD OF ' + str(lowest_load) + ' sip :')
        for c in lowest_codes:
            print(c)
