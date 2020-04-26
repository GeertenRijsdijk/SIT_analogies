# SIT_analogies
Using a Structural Information Theory approach on Hofstadter`s analogies

Files:

- analogies.py: An implementation of the theoretical idea of using SIT to complete Hofstadter's analogies.
- complexity_metrics.py: A collection of complexity metrics used to calculate the complexity of SIT codes.
- compressor_bruteforce.py: Implementation of a compressor that creates every possible encoding of a given string.
- compressor_concurrent.py: Implementation of implements an attempt to increase the speed of the brute-force compressor using an actor library. As of now, the long initialization time needed for actors means this file is not faster.
- compressor_optimized.py: File used for attempts at optimizations, currently not faster.
- decompressor.py: Implementation of a decompressor that writes a given code back to a string.
- tests.py: A unittests class with tests for the bruteforce compressor and decompressor.
- tools.py: A collection of smaller functions that are used by multiple other files.
