import unittest
from decompressor import decompress
from compressor_bruteforce import compress
from random import choice

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

    def test_sequence(self):
        self.assertEqual(decompress('{(a),4,1}'), 'abcd')
        self.assertEqual(decompress('{((a)),4,1}'), '(a)(b)(c)(d)')
        self.assertEqual(decompress('{((a)),4,1}'), '(a)(b)(c)(d)')
        self.assertEqual(decompress('{(d),4,-1}'), 'dcba')
        self.assertEqual(decompress('{(A),4,4}'), 'AEIM')

    def test_combined(self):
        self.assertEqual(decompress('S[(2*(ab))(c)]'), 'ababccabab')
        self.assertEqual(decompress('S[2*((a)(b))(c)]'), 'ababccbaba')
        self.assertEqual(decompress('<2*((a)(b))>/<(f)>'), 'afbfafbf')
        self.assertEqual(decompress('3*(S[(1),(2)])'), '121121121')
        self.assertEqual(decompress('<(1)>/<S[((2)),((3))]>'), '121312')
        self.assertEqual(decompress('<(A)>/<{((A)),4,2}>'), 'AAACAEAG')
        self.assertEqual(decompress('S[{((A)),3,1},(D)]'), 'ABCDCBA')

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

if __name__ == '__main__':
    unittest.main()
