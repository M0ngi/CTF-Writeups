# AfricaCrypt 2023

AfricaCrypt is an annual International Conference on the Theory and Applications of Cryptology. This was an 8h CTF & this was a qualification round for the finals later on. We participated under the name `roll` & secured the first place.

------------

- [Pwn](#pwn)
    -  [easyret](#pwn1 "Solvers")
	-  [Books everywhere](#pwn2 "Solvers")
    -  [Responsiveness](#pwn3 "Solvers")

- [Rev](#rev)
    -  [rev01](#rev1)

------------

### Pwn
1. <p name="pwn1"><b>easyret</b></p>

A ret2win challenge. [Solver](/2023/AfricaCrypt/pwn/easyret/solve.py)

2. <p name="pwn2"><b>Books everywhere</b></p>

A heap challenge with a use after free vulnerability.

How to?
- Allocate a chunk, free it, modify the next chunk pointer (Libc 2.27, no safe linking) to GOT address (Partial RELRO). Read from GOT to leak libc & overwrite the `free` got entry with system. Allocate a new chunk, write "/bin/sh" & free it.

[Solver](/2023/AfricaCrypt/pwn/Books%20everywhere/solve.py)

3. <p name="pwn2"><b>Responsiveness</b></p>

Format string vulnerability with a full protection binary & blocks `execve` + `execveat` using seccomp.

How to?
- Leak a stack+libc address & the value of the canary using format string. Overflow the buffer (uses `gets` to read input). Write a ROP chain to execute the following:

```c
open("./flag.txt", O_RDONLY, S_IRUSR) // File descriptor will be 3
read(3, stackAdr, 256)
write(1, stackAdr, 256)
```

[Solver](/2023/AfricaCrypt/pwn/Responsiveness/solve.py)

### Rev

3. <p name="rev1"><b>rev01</b></p>

I downloaded the binary for this 30 minutes before the CTF ends so I had to hurry. Running the process in `gdb` showed that there is an anti-debugging mechanism implemented. Patched it (address 0x00401e6b) & moved on.

Found the function for the first check (address 0x00401daa) & it clearly verifies that the input is a 4 digits code. Running out of time so, pwntools & bruteforce.

[Solver](/2023/AfricaCrypt/pwn/Responsiveness/solve.py)
