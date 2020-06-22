import unittest
from decompressor import decompress
from compressor_bruteforce import compress_bf
from random import choice, randint
from analogies import predict_analogy
from PISA.encode import encode
from PISA.graphs import Graph
from iterations import solve_with_iterations

class Test_Decompressor(unittest.TestCase):

    def test_iteration(self):
        self.assertEqual(decompress('2*(a)'), 'aa')
        self.assertEqual(decompress('2*((a))'), '(a)(a)')
        self.assertEqual(decompress('2*(3*(a))'), 'aaaaaa')
        self.assertEqual(decompress('11*(a)'), 'aaaaaaaaaaa')

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
        self.assertEqual(decompress('3*(S[(A),(B)])'), 'ABAABAABA')
        self.assertEqual(decompress('<(A)>/<S[((B)),((C))]>'), 'ABACAB')

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
            answers, _ = compress_bf(string)
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
            ('ABAC:ADAE::FBFC:?', 'FDFE', 1),
            ('ABC:CBA::DEF:?', 'FED', 1),
            ('ABC:CBA::DEFG:?', 'GFED', 3),
            ('ABC:CBA::LKJI:?', 'IJKL', 3),
            ('ABCB:ABCB::Q:?', 'Q', 1),
            ('ABCB:Q::ABCB:?', 'Q', 1),
            ('ABCB:Q::BCDC:?', 'R', 3),
            ('IFP:JGQ::UEC:?', 'VFD', 3),
            ('ABAC:ACAB::DEFG:?', 'DGFE', 3),
            ('ABAC:ACAB::DEFG:?', 'FGDE', 10),
            ('AXCR:CRAX::DEFG:?', 'FGDE', 3),
            ('ABC:ABD::IJJKKK:?', 'IJJLLL', 3),
            ('ABC:ABBACCC::DEF:?', 'DEEDFFF', 3),
            ('ABC:ABCD::ABCDE:?', 'ABCDEF', 3),
            ('AE:BD::CC:?', 'DB', 6),
            ('AAE:BBD::CCC:?', 'DDB', 7),
            ('ABC:ABD::IJKLM:?', 'IJKLN', 3),
            ('CAB:DAB::MIJKL:?', 'NIJKL', 3),
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
                part = ''.join([choice(['A','B','C', 'a', 'b', 'c']) \
                    for _ in range(r)])
                parts.append(part)
            analogy = parts[0] + ':' + parts[1] + '::' + parts[2] + ':?'
            predict_analogy(analogy)

class Test_Analogy_Solver_it(unittest.TestCase):
    def test_analogies(self):
        tests = {
            ('AAAB', 'CBBB', 'EEEEEF'): 'GFFFFF',
            ('ABA', 'AABBAA', 'AABBAA'): 'AAABBBAAA',
            ('ABBACCC', 'ADDDD', 'IJJJIKKKK'): 'ILLLLL',
        }

        for test, answer in tests.items():
            l1, l2, r1 = test
            code, new_code = solve_with_iterations(l1, l2, r1)
            self.assertEqual(decompress(code), l1+l2)
            self.assertEqual(decompress(new_code), r1+answer)


class Test_PISA(unittest.TestCase):
    def test_pisa(self):
        for i in range(50):
            N = randint(2,20)
            s = ''.join([choice(['A','B','C', 'D']) for _ in range(N)])
            g = Graph(s)
            encode(g)
            code, _ = g.edges[g.nodes[0]][g.nodes[-1]]
            self.assertEqual(s, decompress(code))

if __name__ == '__main__':
    unittest.main()
