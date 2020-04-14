def create_splits(string):
    all_splits = []
    n = 2**(len(string)-1)
    for i in range(1, n):
        config = format(i, 'b')
        # Add leading zeros
        config = '0'* (len(string) - len(config) - 1) + config
        last_i = 0
        split = []
        for i, n in enumerate(config):
            if n == '1':
                split.append(string[last_i:i+1])
                last_i = i+1
        split.append(string[last_i:])
        all_splits.append(split)
    return all_splits

def build_iteration(split, i, j):
    new_elem = str(j - i) + '*(' + split[i] + ')'
    return split[:i] + [new_elem] + split[j:]

def build_symmetry(split, i, j, pivot):
    new_elem = 'S['
    for arg in split[i:i+pivot]:
        new_elem += '(' + arg +')'
    if (j-i)%2 == 1:
        new_elem += ','
    new_elem += '(' + split[i+pivot] + ')]'
    return split[:i] + [new_elem] + split[j:]

def build_alternation(split, i, j, offset):
    alt_half = '<(' + split[i+offset] + ')>'
    other_elems= split[i:j][1 - offset::2]
    other_half = '<' + ''.join(['(' + e + ')' for e in other_elems]) + '>'
    if offset == 0:
        new_elem = alt_half + '/' + other_half
    else:
        new_elem = other_half + '/' + alt_half
    return split[:i] + [new_elem] + split[j:]

def compress_split(split):
    new_codes = []

    # Iterations
    for i in range(len(split)-1):
        for j in range(i+2, len(split)+1):
            if len(set(split[i:j])) == 1:
              new_codes.append(build_iteration(split, i, j))

    # Symmetries
    for i in range(len(split)-2):
        for j in range(i+3, len(split)+1):
            pivot = int((j-i-1)/2)
            if split[i:i+pivot] == split[j-pivot:j][:: -1] and \
            split[i+pivot] == split[j-pivot-1]:
                new_codes.append(build_symmetry(split, i, j, pivot))

    # Alternations
    for i in range(len(split)-3):
        for j in range(i+4, len(split)+1):
            # Alternations result in an even number of elements
            if len(split[i:j])%2 != 0:
                continue

            if len(set(split[i:j][::2])) == 1:
                 new_codes.append(build_alternation(split, i, j, 0))
            if len(set(split[i:j][1::2])) == 1:
                 new_codes.append(build_alternation(split, i, j, 1))

    return new_codes

def compress(string):
    splits = [[string]] + create_splits(string)
    all_splits = []
    all_codes = []
    while splits != []:
        s = splits.pop(0)
        if s in all_splits:
            continue
        all_splits.append(s)
        if ''.join(s) not in all_codes:
            all_codes.append(''.join(s))
        new_codes = compress_split(s)
        splits += new_codes
    return all_codes

if __name__ == '__main__':
    s = 'aaaa'
    aa = compress(s)
    for a in aa:
        print(a)
