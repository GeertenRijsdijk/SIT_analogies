# Complexity metric using number of symbols + iterations + symmetries
def I_old_load(string):
    load = 0
    for i, c in enumerate(string):
        if c.isalpha() or c == '*':
            load += 1
    return load

# Complexity metric using number of symbols
def P_load(string):
    load = 0
    for i, c in enumerate(string):
        if c.isalpha() and c != 'S':
            load += 1
        elif c == 'S' and (i == len(string)-1 or not string[i+1] == '['):
            load += 1
    return load

# Complexity metric using number of symbols + operators
def I_a_load(string):
    load = 0
    for i, c in enumerate(string):
        if c.isalpha() or c == '*' or c == '/':
            load += 1
    return load

# Complexity metric using number of symbols + non-S-chunks
def I_new_load(string):
    return P_load(string) + len(get_chunks(string))

def I_seq_load(string):
    load = 0
    for c in string:
        if c.isalpha() or c in ['*', '/', '{']:
            load += 1
    return load
    #return I_new_load(string) + string.count('{')*2

# Find the number of chunks in a string that have more than one symbol and
# are not S-chunks
def get_chunks(s):
    par_stack = []
    symm_depth = 0
    chunks = []
    for i, c in enumerate(s):
        if c == '[':
            symm_depth += 1
        if c == ']':
            symm_depth -= 1

        if c == '(':
            par_stack.append(i)
        if c == ')':
            i_start = par_stack.pop(-1)
            if i - i_start < 3 or (symm_depth > 1 and s[i_start + 1] == '('):
                continue
            chunks.append(s[i_start:i+1])
    return chunks


if __name__ == '__main__':
    # Some quick tests from literature + PISA algorithm
    d = {
        'ABCDEF':6,
        '<(aba)>/<(cdacd)(bacdacdab)>':20,
        '<(S[(a), (b)])>/<(S[(cd), (a)])(S[(b)(a)(cd), (a)])>':15,
        'S[(ab)(acd)(acd)(ab)]':14,
        'S[S[((ab))((acd))]]':7,
        '2 * (<(a)>/<S[((b))((cd))]>)':8,

        'S[(a),(b)]':2,
        'S[(a)(b),(c)]':3,
        '3*(a)':1,
        '3*(ab)':3,
        '<(a)>/<(b)(c)(d)>':4,
        '<(a)>/<(b)(c)(d)(e)>':5,

        'S[(A) (B A C)] S[(C B) (A)] 2*(C) 4*(B)':11,
        'S[(A), (B)] 3*(B) 6*(B A) 2*(A)':7,

        'ab2 * (acd) S[(a) (b), (a)] 2 * (cda) b':14,
        'S[S[S[(((A R))), (((B)))] ((C)), ((D))], (Q)]':7,

    }

    for s, sip in d.items():
        if I_new_load(s) != sip:
            print(s, 'FAILED!')
            print('RETURNED:', I_new_load(s))
            print('EXPECTED:', sip)
    print('Done')
