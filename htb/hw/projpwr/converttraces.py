import os
import Trace as trs
from tqdm import tqdm
import numpy as np

# Generate 16 random bytes

# Sample binary plaintext
newTs = trs.TraceSet()
newTs.new("nMY.ts", 0, trs.TraceSet.CodingByte, 16, 1042)

traces = np.load("traces.npy")
pts = np.load("pts.npy")

for power_trace, thispt in zip(traces,pts):
    newTs.addTrace(trs.Trace(b'', thispt, power_trace))

newTs.close()

