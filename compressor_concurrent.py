import sys
from split import create_splits
from complexity_metrics import I_new_load
from thespian.actors import *
import compressor_bruteforce as cb
from split import create_splits
from compressor_bruteforce import build_iteration, build_symmetry, build_alternation, compress
import time

class Iteration_actor(Actor):
    def receiveMessage(self, split, sender):
        new_codes = []
        # Create iterations
        for i in range(len(split)-1):
            for j in range(i+2, len(split)+1):
                if len(set(split[i:j])) == 1:
                  new_codes.append(build_iteration(split, i, j))
        self.send(sender, new_codes)

class Symmetry_actor(Actor):
    def receiveMessage(self, split, sender):
        new_codes = []
        for i in range(len(split)-2):
            for j in range(i+3, len(split)+1):
                pivot = int((j-i)/2)
                if split[i:i+pivot] == split[j-pivot:j][:: -1] and \
                    split[i+pivot] == split[j-pivot-1]:

                    # Create all possible codes for the S-argument
                    argument_split = \
                         ['('+ a +')' for a in split[i:i+pivot]]
                    c = Compression(argument_split)
                    _, splits = c.run()
                    for s in splits:
                        new_codes.append(build_symmetry(\
                            split, i, j, pivot, elems = s))
        self.send(sender, new_codes)

class Alternation_actor(Actor):
    def receiveMessage(self, split, sender):
        new_codes = []
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
                    c = Compression(argument_split)
                    _, splits = c.run()
                    for s in splits:
                        new_codes.append(build_alternation(\
                            split, i, j, offset, elems = s))
        self.send(sender, new_codes)

class Compression():
    def __init__(self, characters):
        self.acsys = ActorSystem("multiprocQueueBase", transientUnique = True)
        self.all_splits = []
        self.all_codes = []

        self.splits = create_splits(characters)
        #self.n_actors = len(self.splits)
        self.n_actors = 20
        self.it_actors, self.sym_actors, self.alt_actors = [], [], []
        for i in range(self.n_actors):
            it = self.acsys.createActor(Iteration_actor)
            self.it_actors.append(it)
            sym = self.acsys.createActor(Symmetry_actor)
            self.sym_actors.append(sym)
            alt = self.acsys.createActor(Alternation_actor)
            self.alt_actors.append(alt)

        # distribution_counter, used to evenly distribute work among actors
        self.dc = 0
        # counter of number of active actors
        self.n_active_actors = 0

    def run(self):
        time0 = time.time()
        self.distribute_splits(self.splits)

        while self.n_active_actors > 0:
            new_codes = self.acsys.listen()
            self.n_active_actors -= 1
            self.distribute_splits(new_codes)
        self.acsys.shutdown()
        return self.all_codes, self.all_splits

    def distribute_splits(self, splits):
        for s in splits:

            if s in self.all_splits:
                continue
            self.all_splits.append(s)
            if ''.join(s) not in self.all_codes:
                self.all_codes.append(''.join(s))

            self.acsys.tell(self.it_actors[self.dc], s)
            self.acsys.tell(self.sym_actors[self.dc], s)
            self.acsys.tell(self.alt_actors[self.dc], s)
            self.dc = (self.dc + 1)%self.n_actors
            self.n_active_actors += 3

if __name__ == '__main__':
    s = 'abcccccccba'

    time0 = time.time()
    encodings, _ = compress(s)
    print('brute-force time:', time.time() - time0)

    time0 = time.time()
    c = Compression(s)
    print('init time:', time.time() - time0)
    time0 = time.time()
    encodings2, _ = c.run()
    print('concurrent time:', time.time() - time0)

    #for i in range(len(encodings2)):
    #    print(encodings2[i])
