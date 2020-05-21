import unittest
from decompressor import decompress
from compressor_bruteforce import compress
from random import choice, randint
from analogies import predict_analogy
from PISA.encode import encode
from PISA.graphs import Graph

class Test_Decompressor(unittest.TestCase):

    def test_iteration(self):
        self.assertEqual(decompress('2*(a)'), 'aa')
        self.assertEqual(decompress('2*((a))'), '(a)(a)')
        self.assertEqual(decompress('2*(3*(a))'), 'aaaaaa')

    def test_symmetry(self):
        self.assertEqual(decompress('S[(a)(b)]'), 'abba')
        self.assertEqual(decompress('S[(a),(b)]'), 'aba')
        self.assertEqual(decompress('S[((a)),((b))]'), '(a)(b)(a)')
        self.assertEqual(decompress('S[(a)(b),(c)]'), 'abcba')
        self.assertEqual(decompress('S[(d)(S[(a),(b)]),(c)]'), 'dabacabad')
        self.assertEqual(decompress('S[S[((a)),((b))],(c)]'), 'abacaba')

    def test_alternation(self):
        self.assertEqual(decompress('<(a)>/<(b)(c)(d)>'), 'abacad')
        self.assertEqual(decompress('<(a)(b)(c)>/<(d)>'), 'adbdcd')
        self.assertEqual(decompress('<(<(a)(b)>/<(d)>)>/<(e)(f)>'), 'adbdeadbdf')
        self.assertEqual(decompress('<<((a))((b))>/<((d))>>/<(e)>'), 'aedebede')
        self.assertEqual(decompress('<(A)>/<(<(BB)(C)>/<(A)>)(B)>'), 'ABBACAAB')

    def test_combined(self):
        self.assertEqual(decompress('S[(2*(ab))(c)]'), 'ababccabab')
        self.assertEqual(decompress('S[2*((a)(b))(c)]'), 'ababccbaba')
        self.assertEqual(decompress('<2*((a)(b))>/<(f)>'), 'afbfafbf')
        self.assertEqual(decompress('3*(S[(1),(2)])'), '121121121')
        self.assertEqual(decompress('<(1)>/<S[((2)),((3))]>'), '121312')

class Test_Compressor(unittest.TestCase):
    def test_iteration(self):
        strings = ['AAAA', 'ABAB', 'AABB', 'AAAAAA', 'AAABBB', 'AAAAAAAA']
        self.compress_decompress_compare(strings)

    def test_symmetry(self):
        strings = ['ABA', 'ABCBA', 'BACABAC', 'BAAB', 'CAACBDB']
        self.compress_decompress_compare(strings)

    def test_alternation(self):
        strings = ['ABAD', 'ABACAD', 'CDACDBCDE', 'QAQBQCQD']
        self.compress_decompress_compare(strings)

    def test_combined(self):
        strings = ['ABACAB', 'AABCBAA', 'AABAACAAB', 'ABABCBABA']
        self.compress_decompress_compare(strings)

    def compress_decompress_compare(self, strings):
        for string in strings:
            answers, _ = compress(string)
            for ans in answers:
                self.assertEqual(decompress(ans), string)

    def test_randomized_strings(self):
        strings = []
        for i in range(5, 10):
            string = ''.join([choice(['A','B','C', 'D']) for _ in range(i)])
            strings.append(string)
        self.compress_decompress_compare(strings)

class Test_Analogy_Solver(unittest.TestCase):
    def test_analogies(self):
        tests = [
            ('A:B::C:?', 'D', 1),
            ('ABA:ACA::ADA:?', 'AEA', 1),
            ('ABC:ABD::DEF:?', 'DEG', 1),
            ('ABAC:ADAE::FBFC:?', 'FDFE', 3),
            ('ABC:CBA::DEF:?', 'FED', 3),
            ('ABC:CBA::DEFG:?', 'GFED', 3),
            ('ABCB:ABCB::Q:?', 'Q', 3),
            ('ABCB:Q::ABCB:?', 'Q', 3),
            ('ABCB:Q::BCDC:?', 'R', 3),
            ('IFP:JGQ::UEC:?', 'VFD', 3),
            ('ABAC:ACAB::DEFG:?', 'FGDE', 3),
            ('ABAC:ACAB::DEFG:?', 'DGFE', 3),
            ('ABC:ABD::IJJKKK:?', 'IJJLLL', 3),
            ('ABC:ABBACCC::DEF:?', 'DEEDFFF', 3),
            ('ABC:ABCD::ABCDE:?', 'ABCDEF', 3),
        ]
        for analogy, answer, top in tests:
            self.single_analogy_test(analogy, answer, top)

    def single_analogy_test(self, analogy, answer, top):
        answers = predict_analogy(analogy)
        codes = [a[0] for a in answers][:top]
        self.assertIn(answer, codes)

    # Run a bunch of random analogies to see whether it crashes
    def test_analogy_crashes(self):
        for i in range(5):
            parts = []
            for i in range(3):
                r = randint(1,6)
                part = ''.join([choice(['A','B','C', '1', '2', '3']) for _ in range(r)])
                parts.append(part)
            analogy = parts[0] + ':' + parts[1] + '::' + parts[2] + ':?'
            predict_analogy(analogy)

class Test_PISA(unittest.TestCase):
    def test_pisa(self):
        for i in range(1):
            N = randint(1,20)
            s = ''.join([choice(['A','B','C', 'D']) for _ in range(N)])
            g = Graph(s)
            encode(g)
            code, _ = g.edges[g.nodes[0]][g.nodes[-1]]
            self.assertEqual(s, decompress(code))

if __name__ == '__main__':
    unittest.main()
