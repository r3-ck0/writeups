from  pwn import *
from time import sleep
from Crypto.Util.number import long_to_bytes, bytes_to_long
from hashlib import sha256
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# context.log_level = "debug"

class AND:
    @staticmethod
    def tp():
        return (1, False)

class NAND:
    @staticmethod
    def tp():
        return (1, True)

class OR:
    @staticmethod
    def tp():
        return (0, False)

class NOR:
    @staticmethod
    def tp():
        return (0, True)

class XOR:
    @staticmethod
    def tp():
        return (0, False)

class XNOR:
    @staticmethod
    def tp():
        return (1, False)

class BUF:
    @staticmethod
    def tp():
        return (1, False)

class INV:
    @staticmethod
    def tp():
        return (1, True)

def clean_output(proc):
    proc.recvuntil(b"Your Choice: ")

def check_result():
    return 1 # or 0

def evaluate_circuit(proc):
    proc.sendline(b"3")
    proc.recvuntil(b"Output: ")
    value = proc.recv(1)
    clean_output(proc)

    return int(value)


def inject_safault(proc, net, value):
    proc.sendline(b"1")
    proc.recvuntil(b"? ")
    proc.sendline(bytes(str(net), "ascii"))
    proc.recvuntil(b"? ")
    proc.sendline(bytes(str(value), "ascii"))
    clean_output(proc)


def clean_safault(proc, net):
    
    proc.sendline(b"2")
    proc.recvuntil(b"? ")
    proc.sendline(bytes(str(net), "ascii"))
    clean_output(proc)

gates = dict()

def identify_gate(proc, gate, inverted=False):
    log.info(".")
    log.debug("Identifying " + str(gate))

    truth = []

    if (len(gate) == 3):
        for x1 in (0, 1):
            for x2 in (0, 1):
                inject_safault(proc, gate[0], x1)
                inject_safault(proc, gate[1], x2)
                truth.append(evaluate_circuit(proc))
                clean_safault(proc, gate[0])
                clean_safault(proc, gate[1])

        if inverted:
            truth = [1 if x == 0 else 0 for x in truth]

        if truth == [0, 0, 0, 1]:
            return AND
        elif truth == [1, 1, 1, 0]:
            return NAND
        elif truth == [0, 1, 1, 1]:
            return OR
        elif truth == [1, 0, 0, 0]:
            return NOR
        elif truth == [0, 1, 1, 0]:
            return XOR
        elif truth == [1, 0, 0, 1]:
            return XNOR
        else:
            log.info(f"Gate {gate} has truth table: {truth}")
    
    else:
        inject_safault(proc, gate[0], 0)
        truth = evaluate_circuit(proc)
        clean_safault(proc, gate[0])

        if inverted:
            truth = 1 if truth == 0 else 0

        if truth == 1:
            return INV
        else:
            return BUF

def prune_single_input_gates(circuit):

    log.info(f"Circuit before: {circuit}")

    for cg1 in circuit:
        if len(cg1) == 2:
            for cg2 in circuit:
                if cg1[0] == cg2[-1]:
                    idx = circuit.index(cg2)
                    circuit.remove(cg2)
                    circuit.insert(idx, (cg2[0], cg2[1], cg1[-1]))
                    circuit.remove(cg1)    

    log.info(f"Circuit after: {circuit}")

    return circuit


def get_circuit(proc):
    import ast
    
    proc.sendline(b"5")
    proc.recvline()
    circuit = proc.recvline()
    return eval(circuit)

def get_children(circuit, gate):
    children = []

    if len(gate) == 2:
        for cg in circuit:
            if cg[-1] == gate[0]:
                return [cg]

    for cg in circuit:
        if cg[-1] == gate[0] or cg[-1] == gate[1]:
            children.append(cg)

    return children

def fix_input_for_passthrough(proc, all_gates, gate, ipt):
    if gate[-1] not in all_gates:
        raise f"Error, {gate[-1]} not identified yet!!"

    actual_gate = all_gates[gate[-1]][1]

    (value, needs_inversion) = actual_gate.tp()

    if len(gate) == 2:
        return needs_inversion, False

    inject_safault(proc, gate[ipt], value)
    return needs_inversion, True
    

def identify_children(proc, final_ipts, all_gates, circuit, gate, child_needs_inversion=False):
    children = get_children(circuit, gate)
    log.debug(f"Stepping into child {gate} (Children: {children})")

    for child in children:
        input_to_fix = 0 if gate[0] != child[-1] else 1
        needs_inversion, was_fault_set = fix_input_for_passthrough(proc, all_gates, gate, input_to_fix)
        needs_inversion = needs_inversion if not child_needs_inversion else not needs_inversion

        all_gates[child[-1]] = (child, identify_gate(proc, child, needs_inversion))

        # recursively identify our children:
        identify_children(proc, final_ipts, all_gates, circuit, child, needs_inversion)

        if was_fault_set:
            clean_safault(proc, gate[input_to_fix])
    
    if children == []:
        for i in range(2):
            needs_inversion, was_fault_set = fix_input_for_passthrough(proc, all_gates, gate, i)
            needs_inversion = needs_inversion if not child_needs_inversion else not needs_inversion

            result = evaluate_circuit(proc)
            final_ipts[gate[1-i]] = 1-result if needs_inversion else result

            if was_fault_set:
                clean_safault(proc, gate[i])
        

def main():
    proc = process("./server.py")
    # proc = remote("34.139.98.117", 4333)

    proc.recvuntil("Encrypted Flag: ")
    encflag = proc.recvline().decode("ascii")

    results = []

    proc.recvuntil(b"Circuit 1/")
    circuits = int(proc.recvline())

    log.info(f"Circuits: {circuits}")

    for c in range(circuits):
        log.info(proc.recvuntil(b"Your Choice: "))

        this_circuit = prune_single_input_gates(get_circuit(proc))

        all_gates = dict()
        final_ipts = dict()
        
        root_gate = this_circuit[-1]
        
        all_gates[root_gate[-1]] = (root_gate, identify_gate(proc, root_gate))
        log.debug(f"Root: {all_gates[root_gate[-1]]}")
        
        identify_children(proc, final_ipts, all_gates, this_circuit, root_gate)

        res = ""

        for i in range(64):
            if i in final_ipts:
                res += str(final_ipts[i])

        results.append(int(res, 2))
        

        if c < circuits-1:
            proc.sendline(b"6")

    log.info(results)
    secret = b""
    for result in results:
        secret += long_to_bytes(result)

    key = sha256(secret).digest()
    cipher = AES.new(key, AES.MODE_ECB)
    plaintext = unpad(cipher.decrypt(bytes.fromhex(encflag)), AES.block_size)
    log.info(plaintext)

if __name__ == "__main__":
    main()