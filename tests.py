import unittest
from decompressor import decompress

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

    def test_combined(self):
        self.assertEqual(decompress('S[(2*(ab))(c)]'), 'ababccabab')
        self.assertEqual(decompress('S[2*((a)(b))(c)]'), 'ababccbaba')
        self.assertEqual(decompress('<2*((a)(b))>/<(f)>'), 'afbfafbf')
        self.assertEqual(decompress('3*(S[(a),(b)])'), 'abaabaaba')
        self.assertEqual(decompress('<(a)>/<S[((b)),((c))]>'), 'abacab')

if __name__ == '__main__':
    unittest.main()