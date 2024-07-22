This was a very simple reversing challenge, however I wanted to play around a bit with the capabilities of ghidra bridge (https://github.com/justfoxing/ghidra_bridge/tree/master) to see if this could be useful in CTFs. The solution parses the assembly instructions and solves outputs the flag.
There is no execution or anything happening, its mere "automated static analysis" after I found the pattern behind the binary.



```python
import ghidra_bridge
b = ghidra_bridge.GhidraBridge(namespace=globals()) # creates the bridge and loads the flat API into the global namespace
print(getState().getCurrentAddress().getOffset())
```

    1086848


```python
def getSymbol(name):
    return next(getState().getCurrentProgram().getSymbolTable().getSymbols(name))
```


```python
def getAddress(offset):
    return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(offset)

start_addr = 0x10912d

listing = getState().getCurrentProgram().getListing()

fn_body = getState().getCurrentProgram().getFunctionManager().getFunctionContaining(getAddress(start_addr)).getBody()
instructions = listing.getInstructions(fn_body, True)

state = {}
result = ['x' for _ in range(35)]

for instruction in instructions:    
    if "LEA" in str(instruction):
        state[str(instruction).split(",")[0].split(" ")[1]] = int(str(instruction).split("[")[1][:-1], 16)

    if "MOV qword ptr" in str(instruction):
        target = (int(str(instruction).split("RSP + ")[1].split("]")[0], 16) - 16) // 8
        reg = str(instruction).split(",")[1]

        result[target] = chr(int(str(getInstructionAt(getAddress(state[reg] + 1))).split(",")[1],16))

        print(result[target], end="")
    
```

    HTB{d0nt_p4n1c_justc4tch_the_3rror}

