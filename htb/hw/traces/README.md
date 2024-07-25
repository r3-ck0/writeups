# Traces


## Understanding the problem and first steps
This was a relatively simple challenge in which we have to reverse a circuit. The circuit is given as gerber files and we have a csv files that shows the states of the GPIO pins at given timesteps.
We pull the gerber files into KiCad and see that it is quite well described. It seems to be a hat for a RasPi 3b+, so we look for the pinout for that board. We then simply follow the traces to the pins and map everything out.
This gives us the following information:

- GPIO16 -> K for C0
- GPIO5  -> K for C1
- GPIO6  -> K for C2
- GPIO13 -> K for C3
- GPIO19 -> K for C4
- GPIO26 -> K for C5
- GPIO20 -> K for C6
- GPIO21 -> K for C7

- GPIO12 -> A for R0
- GPIO25 -> A for R1
- GPIO24 -> A for R2
- GPIO22 -> A for R3
- GPIO27 -> A for R4
- GPIO17 -> A for R5
- GPIO18 -> A for R6
- GPIO23 -> A for R7

Which is all we need to know from the gerber files. Let's write some python code to solve the whole thing now.

## Solution

Let's have a function that takes as inputs the values as they come from the .csv file. An LED lights up, whenever the voltage at the anode is higher by a diode-drop than it is at the kathode.
In simple terms it means: The LED is on, when the anode is 1 and the cathode is 0. This can be realized by taking the outer product between the columns and rows, although we have to invert the columns,
as we want a cell to be 1, when r == 1 and c == 0. We later find out that we also need to flip the order of the columns to make the output show correctly, hence the `[::-1]`.


```python
from time import sleep
import numpy as np


def get_matrix(g5, g6, g12, g13, g16, g17, g18, g19, g20, g21, g22, g23, g24, g25, g26, g27):
    c = - (np.array([g16, g5, g6, g13, g19, g26, g20, g21][::-1]) - 1)
    r  = (np.array([g12, g25, g24, g22, g27, g17, g18, g23]))

    mat = np.outer(c, r)

    return mat

```

The rest of the code iterates over the csv file, computes the matrix for each row and displays it. However, we do not display every line of the csv individually. The columns are triggered in quick succession, otherwise only simple
patterns could be created. In real hardware, this would be visible to the naked eye only by a dimming in the overall brightness of the LEDs, however in our python code, this effect doesn't look good. Instead, we simply sum over groups of 8 matrices in order to see the actual letter being printed.

```python
def draw(mat):
    for line in mat:
        print("".join([" " if x == 0 else "o" for x in line ]))

with open("traces.csv") as f:
    skipped = False
    i = 0
    mat = None

    for line in f:
        if not skipped:
            skipped = True
            continue
        values = [int(x) for x in line.split(",")[1:]]

        if i % 8 == 0:
            mat = get_matrix(*values)
        else:
            mat += get_matrix(*values)
        
        if i % 8 == 7:
            draw(mat)
            i = 0
            sleep(1)
        else:
            i += 1
```


And that's it. When we run the code, it will display the flag as if it was displayed on an actual LED matrix.