import sys

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('USAGE: compressor_PISA.py <code>')
    elif not sys.argv[1].isalpha():
        print('Code must contain only letters!')
    else:
        from PISA.encode import encode
        from PISA.graphs import Graph
        s = sys.argv[1]
        g = Graph(s)
        encode(g)
        code, load = g.edges[g.nodes[0]][g.nodes[-1]]
        print('Best code with load', load, 'is:')
        print(code)
