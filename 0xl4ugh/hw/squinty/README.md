## Squinty

Squinty was a fun little hardware challenge that revolved around square-and-multiply.

Knowing the weakness of custom square-and-multiply implementations, we assume that it must be some kind of timing attack. The idea is that some plaintext is encrypted by taking it to the power of a big number (basically RSA). To do that, the key can be iterated bitwise. If the bit is a 0, we only square. If it is a 1, we square and multiply. This means that, in a naive implementation, a 1 should take longer to compute than a 0.

We see a distinct repetitive pattern in the data when plotting it. Local maxima are a good starting point if we want to retrieve timing information. We ignore the 5 "humps" as they seem to represent a different kind of computation than what we are interested in.

In the following plot, the points of interests are marked in blue. We simply compute the difference in samples to the next local maximum to find the "runtime" of a single computation, which look like this:
```[84, 84, 84, 84, 100, 100, 80, 84, 84, 84, 100, 100, 100, 96, 92, 84, 100, 100, 84, 84, 96, 84, 84, 100, 84, 100, 100, 80, 100, 84, 100, 84, 100, 100, 96, 108, 100, 100, 84, 84, 100, 96, 92, 84, 84, 100, 84, 100, 96, 100, 100, 84, 100, 100, 100, 96, 108, 100, 84, 84, 100, 84, 96, 108, 84, 84, 84, 100, 100, 96, 108, 84, 100, 84, 100, 100, 96, 108, 84, 84, 100, 84, 100, 96, 92, 100, 100, 100, 84, 100, 96, 92, 84, 100, 84, 100, 100, 96, 108, 84, 84, 100, 84, 100, 96, 92, 100, 100, 100, 84, 100, 96, 108, 100, 100, 84, 84, 100, 96, 92, 84, 100, 84, 100, 100, 80, 100, 100, 84, 84, 100, 84, 96, 84, 84, 84, 84, 100, 84, 96, 100, 84, 84, 84, 84, 84, 96, 108, 100, 100, 100, 100, 84, 96, 100, 100, 84, 84, 100, 84, 96, 108, 84, 100, 84, 100, 100, 96, 108, 100, 84, 84, 84, 100, 96, 106, 100, 84, 100, 84, 100, 96, 108, 100, 84, 84, 100, 100, 96, 108, 84, 100, 100, 100, 100, 96]```

We find that there are distinct timings, 84 samples and 100 samples. We assume 84 samples = 0 while 100 samples = 1. Later we find that it is not as exact as we wish it to be and we set the threshold at 95. All the differences <= 95 are counted as a 0, everything above is a 1.
![Marked points of interest](marked_local_maxima.png)

We retrieve the following array:

```[0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1]```

Grouping each 7 bits into a byte, keeping the MSB 0, we retrieve most of the flag:
`0xL4ugh{Squinting4SPA_Sucks`

The last character was lost due to reasons I didn't care to investigate :)

