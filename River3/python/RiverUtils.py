from typing import List, Dict
import heapq
import numpy as np
from triton import TritonContext
import logging

#  Data structures  to hold inputs
# Currently we keep the input as a dictionary mapping from byte indices to values.
# The motivation for this now is that many times the input are large but only small parts from them are changing...
class Input:
    def __init__(self, buffer : Dict[int, any] = None, bound = None , priority = None):
        self.buffer = buffer
        self.bound = bound
        self.priority = priority

    def __lt__(self, other):
        return self.priority > other.priority

    def __str__(self):
        maxKeysToShow = 10
        keysToShow = sorted(self.buffer)[:maxKeysToShow]
        valuesStrToShow = ' '.join(str(self.buffer[k]) for k in keysToShow)
        strRes = (f"({valuesStrToShow}..bound: {self.bound}, priority: {self.priority})")
        return strRes

    # Apply the changes to the buffer, as given in the dictionary mapping from byte index to the new value
    def applyChanges(self, changes : Dict[int, any]):
        self.buffer.update(changes)

# This is used for the contextual bandits problem
class InputRLGenerational(Input):
    def __init__(self):
        Input.__init__(self)
        self.buffer_parent = None # The input of the parent that generated the below PC
        self.priority = -1 # The estimated priority for the state
        self.stateEmbedding = None
        self.PC = None # The parent path constraint that generated the parent input
        self.BBPathInParentPC = None # The same as above but simplified, basically the path of basic blocks obtained by running buffer_parent
        self.constraint = None # The constraint needed (SMT) to give to solve to change the PC using action and produce the new input for this structure
        self.action = -1 # The action to take (which of the self.PC branches should we modify)

# A priority queue data structure for holding inputs by their priority
class InputsWorklist:
    def __init__(self):
        self.internalHeap = []

    def extractInput(self):
        if self.internalHeap:
            next_item = heapq.heappop(self.internalHeap)
            return next_item
        else:
            return None

    def addInput(self, inp: Input):
        heapq.heappush(self.internalHeap, inp)

    def __str__(self):
        str = f"[{' ; '.join(inpStr.__str__() for inpStr in self.internalHeap)}]"
        return str

    def __len__(self):
        return len(self.internalHeap)

# An example how to use the inputs worklist
def example_InputsWorkList():
    worklist = InputsWorklist()
    worklist.addInput(Input("aa", 0, 10))
    worklist.addInput(Input("bb", 1, 20))
    worklist.addInput(Input('cc', 2, 30))
    print(worklist)

# Process the list of inputs to convert to bytes if the input was in a string format
def processSeedDict(seedsDict : List[any]):
    for idx, oldVal in enumerate(seedsDict):
        if isinstance(oldVal, str):
            seedsDict[idx] = str.encode(oldVal)

    #print(seedsDict)
