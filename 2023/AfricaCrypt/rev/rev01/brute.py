import os
from pwn import *
d = []
for i in range(1000, 9999+1):
    p = process("./rev01")
    p.sendline(str(i).encode())
    p.recvuntil(b"orrect path: ")
    r = p.recvall()
    d.append(r)
    if b"FLAG" in r or b"flag" in r:
        print(r) # FLAG{NYcZHKpStazClNONkDOavgphNhhTQ}
        exit(0)


all = b"\n".join(d)
with open("out", "wb") as f:
    f.write(all)
