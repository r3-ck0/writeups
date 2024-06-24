## GATES

(73 solves)

This was a simple crack-me that, when executed, took some input, and if the input was the flag, returned `Correct!`.

### Solution
The structure of the crackme lent itself well to trying to crack it using angr, so this is what I tried. We could, just as well, have provided the input variable to `stdin`, however I wanted to spare angr from having to do some of the work that was obvious to reverse engineer, so implemented that in the initial state myself.
The following is the jupyter notebook I used to solve it:


```python
import angr, claripy
from pwn import *
```


```python
elf = ELF("./gates")
```

    [*] '/home/kali/machines/ctf/wani/rev/gates/loot/gates'
        Arch:     amd64-64-little
        RELRO:    Full RELRO
        Stack:    No canary found
        NX:       NX enabled
        PIE:      PIE enabled


    INFO     | 2024-06-21 20:27:55,730 | pwnlib.elf.elf | '/home/kali/machines/ctf/wani/rev/gates/loot/gates'
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      PIE enabled



```python
!objdump -d ./gates
```

    
    ./gates:     file format elf64-x86-64
    
    
    Disassembly of section .init:
    
    0000000000001000 <.init>:
        1000:	f3 0f 1e fa          	endbr64
        1004:	48 83 ec 08          	sub    $0x8,%rsp
        1008:	48 8b 05 d9 2f 00 00 	mov    0x2fd9(%rip),%rax        # 3fe8 <getc@plt+0x2f78>
        100f:	48 85 c0             	test   %rax,%rax
        1012:	74 02                	je     1016 <__cxa_finalize@plt-0x3a>
        1014:	ff d0                	call   *%rax
        1016:	48 83 c4 08          	add    $0x8,%rsp
        101a:	c3                   	ret
    
    Disassembly of section .plt:
    
    0000000000001020 <.plt>:
        1020:	ff 35 92 2f 00 00    	push   0x2f92(%rip)        # 3fb8 <getc@plt+0x2f48>
        1026:	f2 ff 25 93 2f 00 00 	bnd jmp *0x2f93(%rip)        # 3fc0 <getc@plt+0x2f50>
        102d:	0f 1f 00             	nopl   (%rax)
        1030:	f3 0f 1e fa          	endbr64
        1034:	68 00 00 00 00       	push   $0x0
        1039:	f2 e9 e1 ff ff ff    	bnd jmp 1020 <__cxa_finalize@plt-0x30>
        103f:	90                   	nop
        1040:	f3 0f 1e fa          	endbr64
        1044:	68 01 00 00 00       	push   $0x1
        1049:	f2 e9 d1 ff ff ff    	bnd jmp 1020 <__cxa_finalize@plt-0x30>
        104f:	90                   	nop
    
    Disassembly of section .plt.got:
    
    0000000000001050 <__cxa_finalize@plt>:
        1050:	f3 0f 1e fa          	endbr64
        1054:	f2 ff 25 9d 2f 00 00 	bnd jmp *0x2f9d(%rip)        # 3ff8 <getc@plt+0x2f88>
        105b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
    
    Disassembly of section .plt.sec:
    
    0000000000001060 <puts@plt>:
        1060:	f3 0f 1e fa          	endbr64
        1064:	f2 ff 25 5d 2f 00 00 	bnd jmp *0x2f5d(%rip)        # 3fc8 <getc@plt+0x2f58>
        106b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
    
    0000000000001070 <getc@plt>:
        1070:	f3 0f 1e fa          	endbr64
        1074:	f2 ff 25 55 2f 00 00 	bnd jmp *0x2f55(%rip)        # 3fd0 <getc@plt+0x2f60>
        107b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
    
    Disassembly of section .text:
    
    0000000000001080 <.text>:
        1080:	f3 0f 1e fa          	endbr64
        1084:	55                   	push   %rbp
        1085:	53                   	push   %rbx
        1086:	48 8d 1d bf 2f 00 00 	lea    0x2fbf(%rip),%rbx        # 404c <getc@plt+0x2fdc>
        108d:	48 8d ab 00 02 00 00 	lea    0x200(%rbx),%rbp
        1094:	48 83 ec 08          	sub    $0x8,%rsp
        1098:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
        109f:	00 
        10a0:	48 8b 3d 99 3f 00 00 	mov    0x3f99(%rip),%rdi        # 5040 <stdin@GLIBC_2.2.5>
        10a7:	48 83 c3 10          	add    $0x10,%rbx
        10ab:	e8 c0 ff ff ff       	call   1070 <getc@plt>
        10b0:	c6 43 f0 01          	movb   $0x1,-0x10(%rbx)
        10b4:	88 43 f1             	mov    %al,-0xf(%rbx)
        10b7:	48 39 eb             	cmp    %rbp,%rbx
        10ba:	75 e4                	jne    10a0 <getc@plt+0x30>
        10bc:	41 b8 00 01 00 00    	mov    $0x100,%r8d
        10c2:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
        10c8:	31 c0                	xor    %eax,%eax
        10ca:	e8 51 01 00 00       	call   1220 <getc@plt+0x1b0>
        10cf:	41 83 e8 01          	sub    $0x1,%r8d
        10d3:	75 f3                	jne    10c8 <getc@plt+0x58>
        10d5:	48 8d 05 71 3d 00 00 	lea    0x3d71(%rip),%rax        # 4e4d <getc@plt+0x3ddd>
        10dc:	48 8d 15 3d 2f 00 00 	lea    0x2f3d(%rip),%rdx        # 4020 <getc@plt+0x2fb0>
        10e3:	48 8d 88 00 02 00 00 	lea    0x200(%rax),%rcx
        10ea:	eb 11                	jmp    10fd <getc@plt+0x8d>
        10ec:	0f 1f 40 00          	nopl   0x0(%rax)
        10f0:	48 83 c0 10          	add    $0x10,%rax
        10f4:	48 83 c2 01          	add    $0x1,%rdx
        10f8:	48 39 c8             	cmp    %rcx,%rax
        10fb:	74 20                	je     111d <getc@plt+0xad>
        10fd:	0f b6 32             	movzbl (%rdx),%esi
        1100:	40 38 30             	cmp    %sil,(%rax)
        1103:	74 eb                	je     10f0 <getc@plt+0x80>
        1105:	48 8d 3d f8 0e 00 00 	lea    0xef8(%rip),%rdi        # 2004 <getc@plt+0xf94>
        110c:	e8 4f ff ff ff       	call   1060 <puts@plt>
        1111:	b8 01 00 00 00       	mov    $0x1,%eax
        1116:	48 83 c4 08          	add    $0x8,%rsp
        111a:	5b                   	pop    %rbx
        111b:	5d                   	pop    %rbp
        111c:	c3                   	ret
        111d:	48 8d 3d e7 0e 00 00 	lea    0xee7(%rip),%rdi        # 200b <getc@plt+0xf9b>
        1124:	e8 37 ff ff ff       	call   1060 <puts@plt>
        1129:	31 c0                	xor    %eax,%eax
        112b:	eb e9                	jmp    1116 <getc@plt+0xa6>
        112d:	0f 1f 00             	nopl   (%rax)
        1130:	f3 0f 1e fa          	endbr64
        1134:	31 ed                	xor    %ebp,%ebp
        1136:	49 89 d1             	mov    %rdx,%r9
        1139:	5e                   	pop    %rsi
        113a:	48 89 e2             	mov    %rsp,%rdx
        113d:	48 83 e4 f0          	and    $0xfffffffffffffff0,%rsp
        1141:	50                   	push   %rax
        1142:	54                   	push   %rsp
        1143:	45 31 c0             	xor    %r8d,%r8d
        1146:	31 c9                	xor    %ecx,%ecx
        1148:	48 8d 3d 31 ff ff ff 	lea    -0xcf(%rip),%rdi        # 1080 <getc@plt+0x10>
        114f:	ff 15 83 2e 00 00    	call   *0x2e83(%rip)        # 3fd8 <getc@plt+0x2f68>
        1155:	f4                   	hlt
        1156:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
        115d:	00 00 00 
        1160:	48 8d 3d d9 3e 00 00 	lea    0x3ed9(%rip),%rdi        # 5040 <stdin@GLIBC_2.2.5>
        1167:	48 8d 05 d2 3e 00 00 	lea    0x3ed2(%rip),%rax        # 5040 <stdin@GLIBC_2.2.5>
        116e:	48 39 f8             	cmp    %rdi,%rax
        1171:	74 15                	je     1188 <getc@plt+0x118>
        1173:	48 8b 05 66 2e 00 00 	mov    0x2e66(%rip),%rax        # 3fe0 <getc@plt+0x2f70>
        117a:	48 85 c0             	test   %rax,%rax
        117d:	74 09                	je     1188 <getc@plt+0x118>
        117f:	ff e0                	jmp    *%rax
        1181:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
        1188:	c3                   	ret
        1189:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
        1190:	48 8d 3d a9 3e 00 00 	lea    0x3ea9(%rip),%rdi        # 5040 <stdin@GLIBC_2.2.5>
        1197:	48 8d 35 a2 3e 00 00 	lea    0x3ea2(%rip),%rsi        # 5040 <stdin@GLIBC_2.2.5>
        119e:	48 29 fe             	sub    %rdi,%rsi
        11a1:	48 89 f0             	mov    %rsi,%rax
        11a4:	48 c1 ee 3f          	shr    $0x3f,%rsi
        11a8:	48 c1 f8 03          	sar    $0x3,%rax
        11ac:	48 01 c6             	add    %rax,%rsi
        11af:	48 d1 fe             	sar    $1,%rsi
        11b2:	74 14                	je     11c8 <getc@plt+0x158>
        11b4:	48 8b 05 35 2e 00 00 	mov    0x2e35(%rip),%rax        # 3ff0 <getc@plt+0x2f80>
        11bb:	48 85 c0             	test   %rax,%rax
        11be:	74 08                	je     11c8 <getc@plt+0x158>
        11c0:	ff e0                	jmp    *%rax
        11c2:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
        11c8:	c3                   	ret
        11c9:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
        11d0:	f3 0f 1e fa          	endbr64
        11d4:	80 3d 6d 3e 00 00 00 	cmpb   $0x0,0x3e6d(%rip)        # 5048 <stdin@GLIBC_2.2.5+0x8>
        11db:	75 2b                	jne    1208 <getc@plt+0x198>
        11dd:	55                   	push   %rbp
        11de:	48 83 3d 12 2e 00 00 	cmpq   $0x0,0x2e12(%rip)        # 3ff8 <getc@plt+0x2f88>
        11e5:	00 
        11e6:	48 89 e5             	mov    %rsp,%rbp
        11e9:	74 0c                	je     11f7 <getc@plt+0x187>
        11eb:	48 8b 3d 16 2e 00 00 	mov    0x2e16(%rip),%rdi        # 4008 <getc@plt+0x2f98>
        11f2:	e8 59 fe ff ff       	call   1050 <__cxa_finalize@plt>
        11f7:	e8 64 ff ff ff       	call   1160 <getc@plt+0xf0>
        11fc:	c6 05 45 3e 00 00 01 	movb   $0x1,0x3e45(%rip)        # 5048 <stdin@GLIBC_2.2.5+0x8>
        1203:	5d                   	pop    %rbp
        1204:	c3                   	ret
        1205:	0f 1f 00             	nopl   (%rax)
        1208:	c3                   	ret
        1209:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
        1210:	f3 0f 1e fa          	endbr64
        1214:	e9 77 ff ff ff       	jmp    1190 <getc@plt+0x120>
        1219:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
        1220:	f3 0f 1e fa          	endbr64
        1224:	48 8d 0d 15 2e 00 00 	lea    0x2e15(%rip),%rcx        # 4040 <getc@plt+0x2fd0>
        122b:	48 89 c8             	mov    %rcx,%rax
        122e:	48 8d b1 00 10 00 00 	lea    0x1000(%rcx),%rsi
        1235:	eb 52                	jmp    1289 <getc@plt+0x219>
        1237:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
        123e:	00 00 
        1240:	83 fa 01             	cmp    $0x1,%edx
        1243:	74 05                	je     124a <getc@plt+0x1da>
        1245:	83 fa 02             	cmp    $0x2,%edx
        1248:	75 36                	jne    1280 <getc@plt+0x210>
        124a:	48 63 50 04          	movslq 0x4(%rax),%rdx
        124e:	48 c1 e2 04          	shl    $0x4,%rdx
        1252:	48 01 ca             	add    %rcx,%rdx
        1255:	80 7a 0c 00          	cmpb   $0x0,0xc(%rdx)
        1259:	74 25                	je     1280 <getc@plt+0x210>
        125b:	48 63 78 08          	movslq 0x8(%rax),%rdi
        125f:	48 c1 e7 04          	shl    $0x4,%rdi
        1263:	48 01 cf             	add    %rcx,%rdi
        1266:	80 7f 0c 00          	cmpb   $0x0,0xc(%rdi)
        126a:	74 14                	je     1280 <getc@plt+0x210>
        126c:	0f b6 7f 0d          	movzbl 0xd(%rdi),%edi
        1270:	40 02 7a 0d          	add    0xd(%rdx),%dil
        1274:	c6 40 0c 01          	movb   $0x1,0xc(%rax)
        1278:	40 88 78 0d          	mov    %dil,0xd(%rax)
        127c:	0f 1f 40 00          	nopl   0x0(%rax)
        1280:	48 83 c0 10          	add    $0x10,%rax
        1284:	48 39 f0             	cmp    %rsi,%rax
        1287:	74 33                	je     12bc <getc@plt+0x24c>
        1289:	8b 10                	mov    (%rax),%edx
        128b:	83 fa 03             	cmp    $0x3,%edx
        128e:	74 30                	je     12c0 <getc@plt+0x250>
        1290:	7e ae                	jle    1240 <getc@plt+0x1d0>
        1292:	83 fa 04             	cmp    $0x4,%edx
        1295:	75 e9                	jne    1280 <getc@plt+0x210>
        1297:	48 63 50 04          	movslq 0x4(%rax),%rdx
        129b:	48 c1 e2 04          	shl    $0x4,%rdx
        129f:	48 01 ca             	add    %rcx,%rdx
        12a2:	80 7a 0c 00          	cmpb   $0x0,0xc(%rdx)
        12a6:	74 d8                	je     1280 <getc@plt+0x210>
        12a8:	0f b6 52 0d          	movzbl 0xd(%rdx),%edx
        12ac:	48 83 c0 10          	add    $0x10,%rax
        12b0:	c6 40 fc 01          	movb   $0x1,-0x4(%rax)
        12b4:	88 50 fd             	mov    %dl,-0x3(%rax)
        12b7:	48 39 f0             	cmp    %rsi,%rax
        12ba:	75 cd                	jne    1289 <getc@plt+0x219>
        12bc:	c3                   	ret
        12bd:	0f 1f 00             	nopl   (%rax)
        12c0:	48 63 50 04          	movslq 0x4(%rax),%rdx
        12c4:	48 c1 e2 04          	shl    $0x4,%rdx
        12c8:	48 01 ca             	add    %rcx,%rdx
        12cb:	80 7a 0c 00          	cmpb   $0x0,0xc(%rdx)
        12cf:	74 af                	je     1280 <getc@plt+0x210>
        12d1:	48 63 78 08          	movslq 0x8(%rax),%rdi
        12d5:	48 c1 e7 04          	shl    $0x4,%rdi
        12d9:	48 01 cf             	add    %rcx,%rdi
        12dc:	80 7f 0c 00          	cmpb   $0x0,0xc(%rdi)
        12e0:	74 9e                	je     1280 <getc@plt+0x210>
        12e2:	0f b6 52 0d          	movzbl 0xd(%rdx),%edx
        12e6:	32 57 0d             	xor    0xd(%rdi),%dl
        12e9:	c6 40 0c 01          	movb   $0x1,0xc(%rax)
        12ed:	88 50 0d             	mov    %dl,0xd(%rax)
        12f0:	eb 8e                	jmp    1280 <getc@plt+0x210>
    
    Disassembly of section .fini:
    
    00000000000012f4 <.fini>:
        12f4:	f3 0f 1e fa          	endbr64
        12f8:	48 83 ec 08          	sub    $0x8,%rsp
        12fc:	48 83 c4 08          	add    $0x8,%rsp
        1300:	c3                   	ret



```python
p = angr.Project("./gates", main_opts={"base_addr": 0x100000}, auto_load_libs=False)
```


```python
s = p.factory.entry_state(addr=0x1010bc)

vs = [claripy.BVS(f"chr{x}", 8) for x in range(32)]

for i, v in enumerate(vs):
    s.memory.store(0x10404c + (i * 0x10), 1, 1)
    s.memory.store(0x10404c + 1 + (i * 0x10), v, 1)

sm = p.factory.simgr(s, veritesting=True)
```


```python
results = sm.explore(find=lambda s: b"Correct" in s.posix.dumps(1), avoid=lambda s: b"Wrong" in s.posix.dumps(1))
```

    WARNING  | 2024-06-21 20:27:55,979 | angr.storage.memory_mixins.default_filler_mixin | The program is accessing register with an unspecified value. This could indicate unwanted behavior.
    WARNING  | 2024-06-21 20:27:55,979 | angr.storage.memory_mixins.default_filler_mixin | angr will cope with this by generating an unconstrained symbolic variable and continuing. You can resolve this by:
    WARNING  | 2024-06-21 20:27:55,980 | angr.storage.memory_mixins.default_filler_mixin | 1) setting a value to the initial state
    WARNING  | 2024-06-21 20:27:55,980 | angr.storage.memory_mixins.default_filler_mixin | 2) adding the state option ZERO_FILL_UNCONSTRAINED_{MEMORY,REGISTERS}, to make unknown regions hold null
    WARNING  | 2024-06-21 20:27:55,981 | angr.storage.memory_mixins.default_filler_mixin | 3) adding the state option SYMBOL_FILL_UNCONSTRAINED_{MEMORY,REGISTERS}, to suppress these messages.
    WARNING  | 2024-06-21 20:27:55,982 | angr.storage.memory_mixins.default_filler_mixin | Filling register ftop with 8 unconstrained bytes referenced from 0x0 (not part of a loaded object)
    WARNING  | 2024-06-21 20:28:02,405 | angr.storage.memory_mixins.default_filler_mixin | Filling register ftop with 8 unconstrained bytes referenced from 0x0 (not part of a loaded object)
    WARNING  | 2024-06-21 20:50:35,599 | angr.storage.memory_mixins.default_filler_mixin | Filling register ftop with 8 unconstrained bytes referenced from 0x0 (not part of a loaded object)



```python
results
```




    <SimulationManager with 1 found, 1 avoid>


```python
for i in range(32):
    print(f"{chr(results.found[0].solver.eval(vs[i]))}", end="")
```

    FLAG{INTr0dUction_70_R3v3R$1NG1}
