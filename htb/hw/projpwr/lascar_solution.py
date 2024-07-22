import numpy as np 
from lascar import Session, CpaEngine, ConsoleOutputMethod, MatPlotLibOutputMethod, RankProgressionOutputMethod, ScoreProgressionOutputMethod, DictOutputMethod
from lascar.container import TraceBatchContainer
from lascar.tools.aes import sbox

traces = np.load("traces.npy")
values = np.load("pts.npy")


engines = [
        CpaEngine(f"cpa{i}",  lambda v, k, z=i: sbox[v[z] ^ k], range(256))
        for i in range(16)
]


t = TraceBatchContainer(traces, values)
s = Session(t)
s.add_engines(engines)
s.output_method = ConsoleOutputMethod(*engines)

s.run()

