# SIT_analogies
Using a Structural Information Theory approach on Hofstadter`s analogies

Files:

- README.md: The file you are currently reading.
- analogies.py: An implementation of the theoretical idea of using SIT to complete Hofstadter's analogies.
- complexity_metrics.py: A collection of complexity metrics used to calculate the complexity of SIT codes.
- compressor_bruteforce.py: Implementation of a compressor that creates every possible encoding of a given string.
- compressor_concurrent.py: Implementation of implements an attempt to increase the speed of the brute-force compressor using an actor library. As of now, the long initialization time needed for actors means this file is not faster.
- compressor_PISA.py: A file that allows you to try the PISA-based compressor implemented in the PISA folder from the command line.
- compressor_optimized.py: File used for attempts at optimizations, currently not faster.
- decompressor.py: Implementation of a decompressor that writes a given code back to a string.
- tests.py: A unittests class with tests for the bruteforce compressor and decompressor.
- tools.py: A collection of smaller functions that are used by multiple other files.

In the PISA folder:
- QUIS.py: Implementation of the QUick Identification of all Substrings (QUIS) algorithm.
- graphs.py: Classes for Graphs, Sgraphs, Left/Right Agraphs. 
- encode.py: The encoding algorithm, based on PISA.
